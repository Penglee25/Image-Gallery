// frontend/src/ai/mockAnalyzer.js
import { generateColorsFromDescription } from "./utils.js";

export const analyzeWithMock = async (imageBytes) => {
  console.log("🎭 Using mock AI analyzer");

  const mockCategories = [
    {
      tags: [
        "landscape",
        "nature",
        "mountains",
        "sky",
        "outdoors",
        "scenery",
        "peaceful",
        "horizon",
      ],
      description:
        "A beautiful natural landscape with majestic mountains under a clear sky",
      colors: ["#4A6572", "#344955", "#87CEEB"],
    },
    {
      tags: [
        "portrait",
        "person",
        "face",
        "people",
        "human",
        "smile",
        "expression",
        "closeup",
      ],
      description:
        "A compelling portrait capturing expressive human features and emotions",
      colors: ["#5D4037", "#8D6E63", "#FF9800"],
    },
    {
      tags: [
        "city",
        "urban",
        "building",
        "architecture",
        "street",
        "modern",
        "cityscape",
        "downtown",
      ],
      description:
        "An urban cityscape featuring modern architecture and bustling city life",
      colors: ["#607D8B", "#455A64", "#FFC107"],
    },
    {
      tags: [
        "animal",
        "wildlife",
        "nature",
        "fur",
        "wild",
        "creature",
        "mammal",
        "outdoors",
      ],
      description:
        "A wildlife animal in its natural habitat showcasing natural beauty",
      colors: ["#795548", "#5D4037", "#8BC34A"],
    },
    {
      tags: [
        "food",
        "delicious",
        "meal",
        "fresh",
        "cooking",
        "restaurant",
        "cuisine",
        "appetizing",
      ],
      description:
        "Delicious-looking food beautifully presented and professionally photographed",
      colors: ["#FF5722", "#E91E63", "#FFC107"],
    },
    {
      tags: [
        "beach",
        "ocean",
        "water",
        "sand",
        "coast",
        "vacation",
        "tropical",
        "waves",
      ],
      description: "A scenic beach landscape with ocean waves and sandy shore",
      colors: ["#4FC3F7", "#29B6F6", "#FFB74D"],
    },
    {
      tags: [
        "forest",
        "trees",
        "greenery",
        "woodland",
        "path",
        "wilderness",
        "foliage",
        "hiking",
      ],
      description:
        "A dense forest with lush green trees and natural wilderness",
      colors: ["#388E3C", "#4CAF50", "#8BC34A"],
    },
  ];

  // Simulate processing time
  await new Promise((resolve) =>
    setTimeout(resolve, 1000 + Math.random() * 1000)
  );

  const randomData =
    mockCategories[Math.floor(Math.random() * mockCategories.length)];

  console.log("✅ Mock analysis completed:", randomData.tags.length, "tags");
  return randomData;
};

// Quick mock analysis for testing
export const quickMockAnalysis = async () => {
  const mockData = await analyzeWithMock(new Uint8Array([0]));
  return mockData;
};
