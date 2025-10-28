// src/api/huggingface.js
export const HUGGINGFACE_API_KEY = import.meta.env.VITE_HUGGINGFACE_API_KEY; // replace with your key

/**
 * Analyze image using Hugging Face Inference API (image classification)
 * @param {File} file - image file
 * @returns {Promise<Array>} tags
 */
export async function analyzeImage(file) {
  // Only accept JPEG/PNG
  if (!["image/jpeg", "image/png"].includes(file.type)) {
    console.error("Unsupported file type:", file.type);
    return { tags: [], description: "" };
  }

  // Read as ArrayBuffer
  const arrayBuffer = await file.arrayBuffer();

  try {
    const response = await fetch(
      "https://api-inference.huggingface.co/models/google/vit-base-patch16-224",
      {
        method: "POST",
        headers: {
          Authorization: `Bearer ${HUGGINGFACE_API_KEY}`,
          "Content-Type": "application/octet-stream",
        },
        body: arrayBuffer,
      }
    );

    const result = await response.json();

    if (!Array.isArray(result)) {
      console.error("HF API error:", result);
      return { tags: [], description: "" };
    }

    const tags = result.slice(0, 5).map((r) => r.label);
    const description = result
      .slice(0, 5)
      .map((r) => `${r.label} (${(r.score * 100).toFixed(1)}%)`)
      .join(", ");

    return { tags, description };
  } catch (err) {
    console.error("HF AI analysis failed", err);
    return { tags: [], description: "" };
  }
}
