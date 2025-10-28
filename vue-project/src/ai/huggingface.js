// frontend/src/ai/huggingface.js
import { generateColorsFromDescription } from "./utils.js";

export const analyzeWithHuggingFace = async (imageBytes) => {
  const API_TOKEN =
    import.meta.env.VITE_HUGGINGFACE_API_KEY ||
    localStorage.getItem("HUGGINGFACE_API_KEY");

  console.log("🔑 Hugging Face API Key available:", !!API_TOKEN);

  if (!API_TOKEN) {
    throw new Error("Hugging Face API key not configured");
  }

  try {
    console.log("🔄 Starting Hugging Face analysis...");

    // Use BLIP for image captioning
    const captionResponse = await fetch(
      "https://api-inference.huggingface.co/models/Salesforce/blip-image-captioning-base",
      {
        headers: {
          Authorization: `Bearer ${API_TOKEN}`,
          "Content-Type": "application/json",
        },
        method: "POST",
        body: imageBytes,
      }
    );

    if (!captionResponse.ok) {
      throw new Error(
        `BLIP API error: ${captionResponse.status} ${captionResponse.statusText}`
      );
    }

    const captionResult = await captionResponse.json();
    console.log("📝 Caption result:", captionResult);

    const description =
      captionResult[0]?.generated_text || "An interesting image";

    // Use Microsoft ResNet for tagging
    const tagsResponse = await fetch(
      "https://api-inference.huggingface.co/models/microsoft/resnet-50",
      {
        headers: {
          Authorization: `Bearer ${API_TOKEN}`,
          "Content-Type": "application/json",
        },
        method: "POST",
        body: imageBytes,
      }
    );

    if (!tagsResponse.ok) {
      throw new Error(
        `ResNet API error: ${tagsResponse.status} ${tagsResponse.statusText}`
      );
    }

    const tagsResult = await tagsResponse.json();
    console.log("🏷️ Tags result:", tagsResult);

    // Extract tags from ResNet response
    let tags = [];
    if (Array.isArray(tagsResult)) {
      tags = tagsResult
        .slice(0, 8)
        .map((item) => {
          const label = item.label?.split(",")[0]?.trim() || "unknown";
          return label.toLowerCase();
        })
        .filter((tag) => tag && tag !== "unknown");
    }

    // If we don't have enough tags, supplement with description keywords
    if (tags.length < 5) {
      const words = description.toLowerCase().split(" ");
      const additionalTags = words
        .filter(
          (word) =>
            word.length > 3 &&
            ![
              "this",
              "that",
              "with",
              "from",
              "what",
              "when",
              "where",
              "which",
              "there",
            ].includes(word)
        )
        .slice(0, 8 - tags.length);
      tags = [...tags, ...additionalTags];
    }

    // Ensure we have at least some tags
    if (tags.length === 0) {
      tags = ["image", "photo", "digital", "visual", "picture"];
    }

    // Generate colors based on image content
    const colors = generateColorsFromDescription(description);

    console.log("✅ Hugging Face analysis completed");
    return {
      tags: [...new Set(tags)].slice(0, 8), // Remove duplicates
      description,
      colors,
    };
  } catch (error) {
    console.error("❌ Hugging Face API error:", error);
    throw new Error(`AI analysis failed: ${error.message}`);
  }
};

// Test function to verify API key
export const testHuggingFaceAPI = async () => {
  const API_TOKEN = import.meta.env.VITE_HUGGINGFACE_API_KEY;
  if (!API_TOKEN) {
    console.log("❌ No Hugging Face API key found");
    return false;
  }

  try {
    const response = await fetch(
      "https://api-inference.huggingface.co/models/Salesforce/blip-image-captioning-base",
      {
        headers: { Authorization: `Bearer ${API_TOKEN}` },
        method: "POST",
        body: new Uint8Array([0]), // dummy data
      }
    );
    console.log("🔑 API Key test result:", response.status);
    return response.status === 200;
  } catch (error) {
    console.log("🔑 API Key test failed:", error);
    return false;
  }
};
