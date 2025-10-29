from fastapi import APIRouter, Request, Query
from supabase import create_client, Client
from pydantic import BaseModel
from typing import Union
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
    page: int = Query(1, ge=1),
    limit: int = Query(20, ge=1, le=100),
):
    """Search gallery with pagination"""
    user_id = request.headers.get("x-user-id")
    if not user_id:
        return {"status": "error", "message": "Missing user_id"}

    try:
        # Pagination range
        start = (page - 1) * limit
        end = start + limit - 1

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

        # Count total before range
        total_result = (
            supabase.table("image_metadata")
            .select("image_id", count="exact")
            .eq("user_id", user_id)
            .execute()
        )
        total_count = total_result.count or 0

        # Fetch paginated metadata
        meta_result = metadata_query.range(start, end).execute()
        metadata = meta_result.data or []

        # Join with images table
        image_ids = [m["image_id"] for m in metadata]
        if not image_ids:
            return {"status": "success", "data": [], "page": page, "total": total_count}

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

        return {
            "status": "success",
            "data": combined,
            "page": page,
            "limit": limit,
            "total": total_count,
            "total_pages": (total_count + limit - 1) // limit,
        }

    except Exception as e:
        return {"status": "error", "message": str(e)}


class TagUpdate(BaseModel):
    image_id: Union[str, int]
    tags: list[str]


@router.post("/gallery/update-tags")
async def update_tags(request: Request, payload: TagUpdate):
    user_id = request.headers.get("x-user-id")
    if not user_id:
        return {"status": "error", "message": "Missing user_id"}

    try:
        # Update tags in Supabase
        result = (
            supabase.table("image_metadata")
            .update({"tags": payload.tags})
            .eq("image_id", payload.image_id)
            .eq("user_id", user_id)
            .execute()
        )

        if result.data:
            return {"status": "success", "data": result.data}
        else:
            return {"status": "error", "message": "Image not found or update failed"}
    except Exception as e:
        return {"status": "error", "message": str(e)}
