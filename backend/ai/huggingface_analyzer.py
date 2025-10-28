# backend/ai/huggingface_analyzer.py
import os
import requests
import random
from typing import Tuple, List
from .base_analyzer import BaseAIAnalyzer


class HuggingFaceAnalyzer(BaseAIAnalyzer):
    def __init__(self):
        self.api_key = os.environ.get("VITE_HUGGINGFACE_API_KEY") or os.environ.get(
            "HUGGINGFACE_API_KEY"
        )
        if self.api_key:
            print("✅ Hugging Face Analyzer initialized")
        else:
            print("⚠️  Hugging Face API key not set")

    def analyze_image(self, image_bytes: bytes) -> Tuple[List[str], str, List[str]]:
        """
        Analyze image using Hugging Face AI
        Returns: (tags, description, colors)
        """
        if not self.api_key:
            raise Exception("Hugging Face API key not configured")

        try:
            # Use BLIP for image captioning
            caption = self._get_image_caption(image_bytes)

            # Use Microsoft ResNet for tagging
            tags = self._get_image_tags(image_bytes)

            # Generate colors based on content
            colors = self._extract_colors_based_on_content(caption, tags)

            print(f"✅ Hugging Face Analysis: {len(tags)} tags")
            return tags, caption, colors

        except Exception as e:
            print(f"❌ Hugging Face analysis failed: {e}")
            raise

    def _get_image_caption(self, image_bytes: bytes) -> str:
        """Get image description using BLIP model"""
        try:
            response = requests.post(
                "https://api-inference.huggingface.co/models/Salesforce/blip-image-captioning-base",
                headers={"Authorization": f"Bearer {self.api_key}"},
                data=image_bytes,
                timeout=30,
            )

            if response.status_code != 200:
                raise Exception(f"API returned {response.status_code}: {response.text}")

            result = response.json()

            if isinstance(result, list) and len(result) > 0:
                return result[0]["generated_text"]
            else:
                raise Exception("Unexpected API response format")

        except Exception as e:
            print(f"❌ BLIP captioning failed: {e}")
            return "An interesting image"

    def _get_image_tags(self, image_bytes: bytes) -> List[str]:
        """Get image tags using Microsoft ResNet"""
        try:
            response = requests.post(
                "https://api-inference.huggingface.co/models/microsoft/resnet-50",
                headers={"Authorization": f"Bearer {self.api_key}"},
                data=image_bytes,
                timeout=30,
            )

            if response.status_code != 200:
                raise Exception(f"API returned {response.status_code}: {response.text}")

            result = response.json()

            tags = []
            if isinstance(result, list):
                # Take top 8 labels and clean them up
                for item in result[:8]:
                    label = item.get("label", "")
                    # Clean the label (remove everything after comma if present)
                    clean_label = label.split(",")[0].strip().lower()
                    if clean_label and clean_label not in tags:
                        tags.append(clean_label)

            # If we don't have enough tags, supplement with common ones
            if len(tags) < 5:
                supplemental = [
                    "image",
                    "photo",
                    "digital",
                    "visual",
                    "picture",
                    "photography",
                ]
                tags.extend(
                    [tag for tag in supplemental if tag not in tags][: 8 - len(tags)]
                )

            return tags[:8]  # Return max 8 tags

        except Exception as e:
            print(f"❌ ResNet tagging failed: {e}")
            return ["image", "photo", "digital", "visual"]

    def _extract_colors_based_on_content(
        self, description: str, tags: List[str]
    ) -> List[str]:
        """Generate appropriate colors based on image content"""
        description_lower = description.lower()

        # Color palettes for different content types
        color_palettes = {
            "nature": ["#228B22", "#32CD32", "#006400", "#8FBC8F"],
            "sky": ["#87CEEB", "#4682B4", "#1E90FF", "#00BFFF"],
            "portrait": ["#8B4513", "#D2B48C", "#F4A460", "#DEB887"],
            "city": ["#696969", "#808080", "#A9A9A9", "#708090"],
            "food": ["#FF6347", "#FF4500", "#FF8C00", "#FFA500"],
            "beach": ["#00BFFF", "#FFD700", "#F0E68C", "#FFE4B5"],
            "mountain": ["#708090", "#2F4F4F", "#696969", "#778899"],
            "animal": ["#8B4513", "#A0522D", "#CD853F", "#D2691E"],
            "forest": ["#228B22", "#006400", "#8FBC8F", "#2E8B57"],
        }

        # Determine the best color palette
        for category, colors in color_palettes.items():
            if category in description_lower:
                return colors[:3]

        # Check tags for category hints
        for tag in tags:
            for category in color_palettes.keys():
                if category in tag:
                    return color_palettes[category][:3]

        # Default color palette
        return ["#4A6572", "#344955", "#F9AA33"]
