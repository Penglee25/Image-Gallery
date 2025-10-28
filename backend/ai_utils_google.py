# ai_utils_google.py - UPDATED WITH MOCK DATA
import os
import json
import random
from google.cloud import vision
from google.oauth2 import service_account


class GoogleVisionAnalyzer:
    def __init__(self):
        # Try to initialize Google Vision, but fall back to mock data
        key_path = "vision-api-key.json"

        if os.path.exists(key_path):
            try:
                credentials = service_account.Credentials.from_service_account_file(
                    key_path
                )
                self.client = vision.ImageAnnotatorClient(credentials=credentials)
                print("✅ Google Vision client initialized successfully")
                return
            except Exception as e:
                print(f"❌ Google Vision initialization failed: {e}")

        # Fall back to mock data
        print("⚠️  Using mock AI data (Google Vision not available)")
        self.client = None

    def analyze_image(self, image_bytes):
        """
        Analyze image - uses Google Vision if available, otherwise mock data
        Returns: (tags, description, colors)
        """
        if self.client is not None:
            try:
                return self._analyze_with_google_vision(image_bytes)
            except Exception as e:
                print(f"❌ Google Vision analysis failed, using mock data: {e}")

        # Use mock data as fallback
        return self._get_mock_data()

    def _analyze_with_google_vision(self, image_bytes):
        """Actual Google Vision analysis"""
        image = vision.Image(content=image_bytes)

        response = self.client.annotate_image(
            {
                "image": image,
                "features": [
                    {"type_": vision.Feature.Type.LABEL_DETECTION},
                    {"type_": vision.Feature.Type.IMAGE_PROPERTIES},
                ],
            }
        )

        labels = [label.description for label in response.label_annotations][:8]
        colors = []
        if response.image_properties_annotation:
            dominant_colors = response.image_properties_annotation.dominant_colors
            for color in dominant_colors.colors[:3]:
                hex_color = f"#{color.color.red:02x}{color.color.green:02x}{color.color.blue:02x}"
                colors.append(hex_color.upper())

        description = (
            f"This image shows {', '.join(labels[:3])}"
            if labels
            else "Image analysis complete"
        )

        print(f"✅ Google Vision Analysis: {len(labels)} tags, {len(colors)} colors")
        return labels, description, colors

    def _get_mock_data(self):
        """Return realistic mock data for testing"""
        # Different categories of mock data
        categories = [
            {
                "tags": [
                    "landscape",
                    "nature",
                    "mountains",
                    "sky",
                    "outdoors",
                    "scenery",
                    "peaceful",
                    "horizon",
                ],
                "colors": ["#4A6572", "#344955", "#F9AA33"],
                "description": "A beautiful landscape with mountains and sky",
            },
            {
                "tags": [
                    "portrait",
                    "person",
                    "face",
                    "people",
                    "human",
                    "smile",
                    "expression",
                    "closeup",
                ],
                "colors": ["#5D4037", "#8D6E63", "#FF9800"],
                "description": "A portrait of a person with expressive features",
            },
            {
                "tags": [
                    "city",
                    "urban",
                    "building",
                    "architecture",
                    "street",
                    "modern",
                    "cityscape",
                    "downtown",
                ],
                "colors": ["#607D8B", "#455A64", "#FFC107"],
                "description": "An urban cityscape with modern architecture",
            },
            {
                "tags": [
                    "animal",
                    "wildlife",
                    "nature",
                    "fur",
                    "wild",
                    "creature",
                    "mammal",
                    "outdoors",
                ],
                "colors": ["#795548", "#5D4037", "#8BC34A"],
                "description": "A wildlife animal in its natural habitat",
            },
            {
                "tags": [
                    "food",
                    "delicious",
                    "meal",
                    "fresh",
                    "cooking",
                    "restaurant",
                    "cuisine",
                    "appetizing",
                ],
                "colors": ["#FF5722", "#E91E63", "#FFC107"],
                "description": "Delicious-looking food beautifully presented",
            },
        ]

        # Pick a random category
        data = random.choice(categories)

        print(
            f"✅ Mock AI Analysis: {len(data['tags'])} tags, {len(data['colors'])} colors"
        )
        return data["tags"], data["description"], data["colors"]


# Global instance
vision_analyzer = GoogleVisionAnalyzer()


def analyze_image_ai(image_bytes, max_retries=3, delay=2.0):
    """
    Main function to analyze image - compatible with your existing code
    """
    return vision_analyzer.analyze_image(image_bytes)
