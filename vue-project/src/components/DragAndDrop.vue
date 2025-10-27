<template>
    <div class="bg-gray-100 dark:bg-gray-900 text-gray-900 flex items-center justify-center mb-10">
        <div class="lg:max-w-xl w-full mx-auto p-6 bg-white dark:bg-gray-900 text-gray-900 rounded-md shadow-md">
            <!-- Drop Zone -->
            <label @dragover.prevent="onDragOver" @dragleave="onDragLeave" @drop.prevent="onDrop"
                class="flex flex-col items-center w-full h-40 p-6 border-2 border-gray-300 border-dashed rounded-md cursor-pointer hover:border-gray-400 transition"
                :class="{ 'border-gray-400': isDragging }">
                <svg xmlns="http://www.w3.org/2000/svg" class="w-12 h-12 text-gray-400 mb-2" fill="none"
                    viewBox="0 0 24 24" stroke="currentColor" stroke-width="2">
                    <path stroke-linecap="round" stroke-linejoin="round"
                        d="M7 16a4 4 0 01-.88-7.903A5 5 0 1115.9 6L16 6a5 5 0 011 9.9M15 13l-3-3m0 0l-3 3m3-3v12" />
                </svg>
                <span class="text-sm text-gray-600">
                    Drop JPEG/PNG files here or
                    <span class="text-blue-600 underline">browse</span>
                </span>
                <input type="file" multiple accept="image/jpeg, image/png" class="hidden" @change="onFileChange"
                    ref="fileInput" />
            </label>

            <!-- Preview Container -->
            <div class="mt-4 grid grid-cols-2 gap-4">
                <div v-for="(file, index) in files" :key="index" class="relative group">
                    <img :src="file.thumbnail" class="w-full h-32 object-cover rounded-md mb-2" />
                    <button @click="removeFile(index)"
                        class="absolute top-2 right-2 text-white bg-red-500 border-none rounded-md px-2 py-1 opacity-0 group-hover:opacity-100 transition">×</button>
                </div>
            </div>
        </div>
    </div>
</template>

<script setup>
import { ref } from 'vue';

const files = ref([]);
const isDragging = ref(false);
const fileInput = ref(null);

const onDragOver = () => {
    isDragging.value = true;
};

const onDragLeave = () => {
    isDragging.value = false;
};

const onDrop = (event) => {
    isDragging.value = false;
    handleFiles(event.dataTransfer.files);
};

const onFileChange = () => {
    handleFiles(fileInput.value.files);
};

const handleFiles = (selectedFiles) => {
    for (const file of selectedFiles) {
        // Only accept JPEG or PNG
        if (!['image/jpeg', 'image/png'].includes(file.type)) continue;

        const reader = new FileReader();
        reader.onload = (e) => {
            createThumbnail(e.target.result).then((thumbnail) => {
                files.value.push({ file, thumbnail });
            });
        };
        reader.readAsDataURL(file);
    }
};

const createThumbnail = (imageSrc) => {
    return new Promise((resolve) => {
        const img = new Image();
        img.src = imageSrc;
        img.onload = () => {
            const canvas = document.createElement('canvas');
            const size = 300;
            canvas.width = size;
            canvas.height = size;
            const ctx = canvas.getContext('2d');

            // Fit image inside 300x300 square
            const scale = Math.min(size / img.width, size / img.height);
            const x = (size - img.width * scale) / 2;
            const y = (size - img.height * scale) / 2;

            ctx.clearRect(0, 0, size, size);
            ctx.drawImage(img, x, y, img.width * scale, img.height * scale);

            resolve(canvas.toDataURL());
        };
    });
};

const removeFile = (index) => {
    files.value.splice(index, 1);
};
</script>
