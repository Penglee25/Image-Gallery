# ai_utils.py - UPDATED for OpenAI v1.0+
import os
import base64
import json
import time
from openai import OpenAI
from io import BytesIO

# Initialize OpenAI client with v1.0+ syntax
OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY") or os.environ.get("AI_API_KEY")
if not OPENAI_API_KEY:
    raise Exception("OpenAI API Key not set in environment")

client = OpenAI(api_key=OPENAI_API_KEY)


def analyze_image_ai(image_bytes: bytes, max_retries: int = 3, delay: float = 2.0):
    """
    Analyze an image via OpenAI:
    - Generate 5-10 tags
    - One descriptive sentence
    - Top 3 dominant colors (HEX)
    Returns: (tags, description, colors)
    """

    for attempt in range(max_retries + 1):
        try:
            # Convert image to base64 for GPT-4 Vision
            image_base64 = base64.b64encode(image_bytes).decode("utf-8")

            response = client.chat.completions.create(
                model="gpt-4-vision-preview",  # or "gpt-4o" if you have access
                messages=[
                    {
                        "role": "user",
                        "content": [
                            {
                                "type": "text",
                                "text": """Analyze this image and return ONLY valid JSON in this exact format:
{
    "description": "one descriptive sentence about the image",
    "tags": ["tag1", "tag2", "tag3", "tag4", "tag5"],
    "colors": ["#HEX1", "#HEX2", "#HEX3"]
}

Return ONLY the JSON, no other text.""",
                            },
                            {
                                "type": "image_url",
                                "image_url": {
                                    "url": f"data:image/jpeg;base64,{image_base64}"
                                },
                            },
                        ],
                    }
                ],
                max_tokens=300,
                temperature=0,
            )

            # Extract and parse JSON response
            content = response.choices[0].message.content

            # Clean response (remove markdown code blocks if present)
            content = content.strip()
            if content.startswith("```json"):
                content = content[7:]
            if content.endswith("```"):
                content = content[:-3]
            content = content.strip()

            data = json.loads(content)

            # Return as tuple to match your existing code
            tags = data.get("tags", [])
            description = data.get("description", "")
            colors = data.get("colors", [])

            print(f"AI Analysis Success: {len(tags)} tags, {len(colors)} colors")
            return tags, description, colors

        except json.JSONDecodeError as e:
            print(f"JSON parse error (attempt {attempt+1}): {e}")
            print(f"Raw response: {content if 'content' in locals() else 'No content'}")

        except Exception as e:
            print(f"AI analysis error (attempt {attempt+1}): {e}")

        # Wait before retry (if any attempts left)
        if attempt < max_retries:
            time.sleep(delay)

    # Return empty results if all retries failed
    return [], "Analysis failed", []
