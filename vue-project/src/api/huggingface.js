// src/api/huggingface.js
export const HUGGINGFACE_API_KEY = import.meta.env.VITE_HUGGINGFACE_API_KEY; // replace with your key

/**
 * Analyze image using Hugging Face Inference API (image classification)
 * @param {File} file - image file
 * @returns {Promise<Array>} tags
 */
export async function analyzeImage(file) {
  try {
    const res = await fetch(
      "https://api-inference.huggingface.co/models/google/vit-base-patch16-224",
      {
        method: "POST",
        headers: {
          Authorization: `Bearer ${HUGGINGFACE_API_KEY}`,
          "Content-Type": "application/octet-stream",
        },
        body: file,
      }
    );

    if (!res.ok) {
      throw new Error("Hugging Face API error");
    }

    const data = await res.json();
    // data is an array of {label, score}
    return data.map((item) => item.label);
  } catch (err) {
    console.error("Hugging Face error:", err);
    return [];
  }
}
