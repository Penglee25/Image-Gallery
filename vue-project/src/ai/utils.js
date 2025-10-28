// frontend/src/ai/utils.js
export const generateColorsFromDescription = (description) => {
  const descriptionLower = description.toLowerCase();

  // Color palettes for different content types
  const colorPalettes = {
    nature: ["#228B22", "#32CD32", "#006400", "#8FBC8F"],
    sky: ["#87CEEB", "#4682B4", "#1E90FF", "#00BFFF"],
    portrait: ["#8B4513", "#D2B48C", "#F4A460", "#DEB887"],
    city: ["#696969", "#808080", "#A9A9A9", "#708090"],
    food: ["#FF6347", "#FF4500", "#FF8C00", "#FFA500"],
    beach: ["#00BFFF", "#FFD700", "#F0E68C", "#FFE4B5"],
    mountain: ["#708090", "#2F4F4F", "#696969", "#778899"],
    animal: ["#8B4513", "#A0522D", "#CD853F", "#D2691E"],
    forest: ["#228B22", "#006400", "#8FBC8F", "#2E8B57"],
    water: ["#1E90FF", "#00BFFF", "#87CEEB", "#4682B4"],
    sunset: ["#FF4500", "#FF8C00", "#FFD700", "#FF6347"],
  };

  // Determine the best color palette
  for (const [category, colors] of Object.entries(colorPalettes)) {
    if (descriptionLower.includes(category)) {
      return colors.slice(0, 3);
    }
  }

  // Default color palette
  return ["#4A6572", "#344955", "#F9AA33"];
};

export const validateImageFile = (file) => {
  const allowedTypes = ["image/jpeg", "image/png", "image/jpg"];
  const maxSize = 10 * 1024 * 1024; // 10MB

  if (!allowedTypes.includes(file.type)) {
    throw new Error(
      `File ${file.name} is not a supported image type. Please use JPEG or PNG.`
    );
  }

  if (file.size > maxSize) {
    throw new Error(`File ${file.name} is too large. Maximum size is 10MB.`);
  }

  return true;
};

export const formatFileSize = (bytes) => {
  if (bytes === 0) return "0 Bytes";
  const k = 1024;
  const sizes = ["Bytes", "KB", "MB", "GB"];
  const i = Math.floor(Math.log(bytes) / Math.log(k));
  return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + " " + sizes[i];
};

export const createImageThumbnail = (imageSrc, size = 300) => {
  return new Promise((resolve) => {
    const img = new Image();
    img.src = imageSrc;
    img.onload = () => {
      const canvas = document.createElement("canvas");
      canvas.width = size;
      canvas.height = size;
      const ctx = canvas.getContext("2d");
      const scale = Math.min(size / img.width, size / img.height);
      const x = (size - img.width * scale) / 2;
      const y = (size - img.height * scale) / 2;
      ctx.clearRect(0, 0, size, size);
      ctx.drawImage(img, x, y, img.width * scale, img.height * scale);
      resolve(canvas.toDataURL());
    };
  });
};
