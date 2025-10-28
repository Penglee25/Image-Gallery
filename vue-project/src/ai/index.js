// frontend/src/ai/index.js
import { analyzeWithHuggingFace } from "./huggingface.js";
import { analyzeWithMock } from "./mockAnalyzer.js";
import { generateColorsFromDescription } from "./utils.js";

class AIManager {
  constructor() {
    this.analyzers = [
      { name: "huggingface", analyze: analyzeWithHuggingFace },
      { name: "mock", analyze: analyzeWithMock },
    ];
    console.log(
      "🤖 AI Manager initialized with",
      this.analyzers.length,
      "analyzers"
    );
  }

  async analyzeImage(imageBytes, maxRetries = 2) {
    for (const analyzer of this.analyzers) {
      try {
        console.log(`🔍 Trying ${analyzer.name} analyzer...`);
        const result = await analyzer.analyze(imageBytes);
        console.log(`✅ Analysis successful with ${analyzer.name}`);
        return result;
      } catch (error) {
        console.log(`❌ ${analyzer.name} failed:`, error.message);
        // Continue to next analyzer
      }
    }

    // If all analyzers fail, use mock as final fallback
    console.log("🔄 All analyzers failed, using mock data as final fallback");
    return analyzeWithMock(imageBytes);
  }
}

// Global instance
export const aiManager = new AIManager();

// Main export function
export const analyzeImageAI = async (imageBytes, maxRetries = 2) => {
  return aiManager.analyzeImage(imageBytes, maxRetries);
};
