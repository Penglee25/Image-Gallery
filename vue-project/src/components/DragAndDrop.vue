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
                    <span class="text-blue-600 underline" @click="fileInput.click()">browse</span>
                </span>
                <input type="file" multiple accept="image/jpeg, image/png" class="hidden" @change="onFileChange"
                    ref="fileInput" />
            </label>

            <!-- Preview + Upload Progress -->
            <div class="mt-4 grid grid-cols-2 gap-4">
                <div v-for="(file, index) in files" :key="file.tempId"
                    class="relative group bg-gray-100 dark:bg-gray-800 p-2 rounded-md">
                    <img :src="file.thumbnail" class="w-full h-32 object-cover rounded-md mb-2" />

                    <!-- File Info -->
                    <div class="text-xs text-gray-600 mb-2">
                        {{ file.name }}
                    </div>

                    <!-- Upload Progress -->
                    <div v-if="file.uploading" class="w-full bg-gray-300 h-2 rounded mb-2">
                        <div class="bg-blue-500 h-2 rounded transition-all" :style="{ width: file.progress + '%' }">
                        </div>
                        <div class="text-xs text-gray-500 mt-1">Uploading: {{ file.progress }}%</div>
                    </div>

                    <!-- AI Processing Status -->
                    <div class="text-xs mb-2 mt-5">
                        <span :class="{
                            'text-yellow-600': file.ai_processing_status === 'pending',
                            'text-green-600': file.ai_processing_status === 'done',
                            'text-red-600': file.ai_processing_status === 'failed',
                            'text-blue-600': file.ai_processing_status === 'processing'
                        }">
                            AI: {{ file.ai_processing_status }}
                        </span>
                    </div>

                    <!-- AI Results -->
                    <div class="text-xs text-gray-700 dark:text-gray-200 space-y-1">
                        <div v-if="file.tags.length" class="flex flex-wrap gap-1">
                            <span class="font-semibold">Tags:</span>
                            <span v-for="tag in file.tags" :key="tag"
                                class="bg-blue-100 text-blue-800 px-1 rounded text-xs">
                                {{ tag }}
                            </span>
                        </div>
                        <div v-if="file.description" class="truncate">
                            <span class="font-semibold">Desc:</span> {{ file.description }}
                        </div>
                        <div v-if="file.colors.length" class="flex items-center gap-1">
                            <span class="font-semibold">Colors:</span>
                            <span v-for="color in file.colors" :key="color" :style="{ backgroundColor: color }"
                                class="inline-block w-4 h-4 rounded-full border border-gray-300" :title="color">
                            </span>
                        </div>
                    </div>

                    <button @click="removeFile(index)"
                        class="absolute top-2 right-2 text-white bg-red-500 border-none rounded-md px-2 py-1 opacity-0 group-hover:opacity-100 transition text-xs">×</button>
                </div>
            </div>
        </div>
    </div>
</template>

<script setup>
import { ref } from 'vue'
import { analyzeImage } from '../api/huggingface'
import api from '../api/axios'

const files = ref([])
const isDragging = ref(false)
const fileInput = ref(null)

const onDragOver = () => { isDragging.value = true }
const onDragLeave = () => { isDragging.value = false }
const onDrop = (e) => { isDragging.value = false; handleFiles(e.dataTransfer.files) }
const onFileChange = () => handleFiles(fileInput.value.files)

const handleFiles = (selectedFiles) => {
    for (const file of selectedFiles) {
        if (!['image/jpeg', 'image/png'].includes(file.type)) continue

        const reader = new FileReader()
        reader.onload = async (e) => {
            const thumbnail = await createThumbnail(e.target.result)
            const tempFile = {
                tempId: crypto.randomUUID(),
                file: file,
                name: file.name,
                thumbnail,
                uploading: false, // no upload yet
                ai_processing_status: 'processing',
                tags: [],
                description: '',
                colors: [],
            }
            files.value.push(tempFile)

            // Run AI in frontend
            try {
                tempFile.tags = await analyzeImage(file)

                // Extract colors using ColorThief
                const img = new Image()
                img.src = tempFile.thumbnail
                img.crossOrigin = 'Anonymous'
                img.onload = () => {
                    const colorThief = new ColorThief()
                    const palette = colorThief.getPalette(img, 5)
                    tempFile.colors = palette.map(c => `rgb(${c[0]},${c[1]},${c[2]})`)
                    tempFile.ai_processing_status = 'done'
                }
            } catch (err) {
                tempFile.ai_processing_status = 'failed'
            }
        }
        reader.readAsDataURL(file)
    }
}

const createThumbnail = (imageSrc) => {
    return new Promise((resolve) => {
        const img = new Image()
        img.src = imageSrc
        img.onload = () => {
            const canvas = document.createElement('canvas')
            const size = 300
            canvas.width = size
            canvas.height = size
            const ctx = canvas.getContext('2d')
            const scale = Math.min(size / img.width, size / img.height)
            const x = (size - img.width * scale) / 2
            const y = (size - img.height * scale) / 2
            ctx.clearRect(0, 0, size, size)
            ctx.drawImage(img, x, y, img.width * scale, img.height * scale)
            resolve(canvas.toDataURL())
        }
    })
}

const removeFile = (index) => {
    files.value.splice(index, 1)
}

// Later, you can implement a separate upload button
const uploadAll = async () => {
    for (const fileObj of files.value) {
        if (fileObj.uploading) continue
        fileObj.uploading = true
        try {
            const formData = new FormData()
            formData.append('files', fileObj.file)
            const userId = localStorage.getItem('user_id')

            const res = await api.post('/upload', formData, {
                headers: {
                    'Content-Type': 'multipart/form-data',
                    'X-User-Id': userId
                }
            })

            fileObj.uploading = false
            fileObj.ai_processing_status = 'done'
        } catch (err) {
            console.error('Upload error:', err)
            fileObj.uploading = false
            fileObj.ai_processing_status = 'failed'
        }
    }
}
</script>
