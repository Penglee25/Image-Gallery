from fastapi import APIRouter, Request, Query
from supabase import create_client, Client
import os

router = APIRouter()

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_SERVICE_ROLE_KEY")
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)


@router.get("/gallery/search")
async def search_gallery(
    request: Request,
    query: str = Query(None),
    color: str = Query(None),
    similar_tags: str = Query(None),
):
    user_id = request.headers.get("x-user-id")
    if not user_id:
        return {"status": "error", "message": "Missing user_id"}

    try:
        metadata_query = (
            supabase.table("image_metadata").select("*").eq("user_id", user_id)
        )

        # Text search
        if query:
            metadata_query = metadata_query.or_(
                f"description.ilike.%{query}%,tags.cs.{{{query}}}"
            )

        # Filter by color
        if color:
            metadata_query = metadata_query.contains("colors", [color])

        # Filter by similar tags
        if similar_tags:
            tags = [t.strip() for t in similar_tags.split(",")]
            or_conditions = ",".join([f"tags.cs.{{{t}}}" for t in tags])
            metadata_query = metadata_query.or_(or_conditions)

        meta_result = metadata_query.execute()
        metadata = meta_result.data or []

        # Join with images table
        image_ids = [m["image_id"] for m in metadata]
        if not image_ids:
            return {"status": "success", "data": []}

        images_result = (
            supabase.table("images")
            .select("*")
            .in_("id", image_ids)
            .eq("user_id", user_id)
            .execute()
        )
        images = {img["id"]: img for img in images_result.data or []}

        # Merge
        combined = []
        for meta in metadata:
            img = images.get(meta["image_id"])
            if img:
                combined.append(
                    {
                        "image_id": meta["image_id"],
                        "filename": img["filename"],
                        "user_id": img["user_id"],
                        "description": meta["description"],
                        "tags": meta["tags"],
                        "colors": meta["colors"],
                    }
                )

        return {"status": "success", "data": combined}

    except Exception as e:
        return {"status": "error", "message": str(e)}
