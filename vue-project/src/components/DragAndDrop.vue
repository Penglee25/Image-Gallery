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

            <!-- Upload Button -->
            <div class="mt-4 flex justify-center" v-if="files.length">
                <button @click="uploadAll" :disabled="isUploading || !allAIProcessed" class="relative px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700 
           disabled:opacity-50 disabled:cursor-not-allowed flex items-center gap-2 w-40 justify-center">
                    <!-- Text states -->
                    <template v-if="!isUploading && allAIProcessed">
                        Upload All
                    </template>
                    <template v-else-if="isUploading">
                        Uploading... {{ uploadProgress }}%
                    </template>
                    <template v-else>
                        Processing AI...
                    </template>

                    <!-- Spinner -->
                    <svg v-if="isUploading" class="w-4 h-4 animate-spin ml-2" fill="none" stroke="currentColor"
                        viewBox="0 0 24 24">
                        <circle cx="12" cy="12" r="10" stroke-width="4" stroke-opacity="0.25" />
                        <path d="M4 12a8 8 0 018-8v8H4z" stroke-width="4" stroke-linecap="round"
                            stroke-linejoin="round" />
                    </svg>

                    <!-- Progress bar -->
                    <div v-if="isUploading"
                        class="absolute bottom-0 left-0 h-1 bg-blue-300 transition-all duration-300 rounded-b-md"
                        :style="{ width: uploadProgress + '%' }"></div>
                </button>
            </div>


            <!-- Preview + AI Results -->
            <div class="mt-4 grid grid-cols-2 gap-4">
                <div v-for="(file, index) in files" :key="file.tempId"
                    class="relative group bg-gray-100 dark:bg-gray-800 p-2 rounded-md overflow-hidden">
                    <img :src="file.thumbnail" class="w-full h-32 object-cover rounded-md mb-2" />

                    <div class="text-xs text-gray-600 dark:text-gray-200 mb-2">{{ file.name }}</div>

                    <!-- AI Skeleton -->
                    <div v-if="file.ai_processing_status === 'processing'" class="space-y-1">
                        <span class="font-semibold">Tags:</span>
                        <div class="h-4 w-32 bg-gray-300 dark:bg-gray-700 rounded animate-pulse"></div>
                        <span class="font-semibold">Description:</span>
                        <div class="h-4 w-full bg-gray-300 dark:bg-gray-700 rounded animate-pulse"></div>
                        <span class="font-semibold">Colors:</span>
                        <div class="flex gap-1">
                            <div class="w-4 h-4 bg-gray-300 rounded animate-pulse"></div>
                            <div class="w-4 h-4 bg-gray-300 rounded animate-pulse"></div>
                            <div class="w-4 h-4 bg-gray-300 rounded animate-pulse"></div>
                        </div>
                    </div>

                    <!-- AI Results -->
                    <div v-else-if="file.ai_processing_status === 'done'"
                        class="text-xs text-gray-700 dark:text-gray-200 space-y-1">
                        <div v-if="file.tags.length" class="flex flex-wrap gap-1">
                            <span class="font-semibold">Tags:</span>
                            <span v-for="tag in file.tags" :key="tag"
                                class="bg-blue-100 text-blue-800 px-1 rounded text-xs">{{ tag
                                }}</span>
                        </div>
                        <div v-if="file.description" class="truncate">
                            <span class="font-semibold">Desc:</span> {{ file.description }}
                        </div>
                        <div v-if="file.colors.length" class="flex items-center gap-1">
                            <span class="font-semibold">Colors:</span>
                            <span v-for="color in file.colors.slice(0, 3)" :key="color"
                                :style="{ backgroundColor: color }"
                                class="inline-block w-4 h-4 rounded-full border border-gray-300" :title="color"></span>
                        </div>
                    </div>

                    <div v-else-if="file.ai_processing_status === 'failed'" class="text-red-600">AI: Failed</div>

                    <button @click="removeFile(index)"
                        class="absolute top-2 right-2 text-white bg-red-500 border-none rounded-md px-2 py-1 opacity-0 group-hover:opacity-100 transition text-xs">×</button>
                </div>
            </div>

        </div>
    </div>
</template>

<script setup>
import { ref, computed, nextTick } from 'vue'
import { analyzeImage } from '../api/huggingface'
import ColorThief from 'colorthief'
import api from '../api/axios'
import Swal from "sweetalert2"

const files = ref([])
const isDragging = ref(false)
const fileInput = ref(null)
const isUploading = ref(false)
const uploadProgress = ref(0)

const emit = defineEmits(['upload-complete'])

const onDragOver = () => isDragging.value = true
const onDragLeave = () => isDragging.value = false
const onDrop = (e) => { isDragging.value = false; handleFiles(e.dataTransfer.files) }
const onFileChange = () => handleFiles(fileInput.value.files)


// ✅ computed property that checks if all AI processing is finished
const allAIProcessed = computed(() =>
    files.value.length > 0 &&
    files.value.every(f => ['done', 'failed'].includes(f.ai_processing_status))
)

const handleFiles = (selectedFiles) => {
    for (const file of selectedFiles) {
        if (!['image/jpeg', 'image/png'].includes(file.type)) continue

        const reader = new FileReader();
        reader.onload = async (e) => {
            const thumbnail = await createThumbnail(e.target.result)
            const tempFile = {
                tempId: crypto.randomUUID(),
                file,
                name: file.name,
                thumbnail,
                ai_processing_status: 'processing',
                tags: [],
                description: '',
                colors: [],
            }
            files.value.push(tempFile)
            await nextTick()
            runAI(tempFile)
        }
        reader.readAsDataURL(file)
    }
}

const runAI = async (fileObj) => {
    try {
        const { tags, description } = await analyzeImage(fileObj.file)

        const img = new Image()
        img.src = fileObj.thumbnail
        img.crossOrigin = 'Anonymous'
        img.onload = () => {
            const colorThief = new ColorThief()
            const palette = colorThief.getPalette(img, 5)
            const colors = palette.map(c => `rgb(${c[0]},${c[1]},${c[2]})`)

            const index = files.value.findIndex(f => f.tempId === fileObj.tempId)
            if (index !== -1) {
                files.value[index] = {
                    ...fileObj,
                    tags,
                    description,
                    colors: colors.slice(0, 3),
                    ai_processing_status: 'done'
                }
            }
        }
    } catch (err) {
        const index = files.value.findIndex(f => f.tempId === fileObj.tempId)
        if (index !== -1) files.value[index].ai_processing_status = 'failed'
    }
}

const createThumbnail = (imageSrc) => new Promise(resolve => {
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

const uploadAll = async () => {
    if (!files.value.length) return
    const userId = localStorage.getItem('user_id')
    if (!userId) return alert("User ID missing")
    isUploading.value = true

    try {
        const formData = new FormData()
        files.value.forEach(f => formData.append('files', f.file))

        const res = await api.post('/upload', formData, {
            headers: { 'Content-Type': 'multipart/form-data', 'X-User-Id': userId },
            onUploadProgress: (e) => {
                const progress = Math.round((e.loaded / e.total) * 100)
                uploadProgress.value = progress // ✅ global progress for all files
                files.value.forEach(f => f.progress = progress)
            }
        })

        res.data.uploaded.forEach((uploaded, index) => {
            const file = files.value[index]
            file.image_id = uploaded.image_id
            const topColors = file.colors.slice(0, 3)

            // Send AI metadata to backend
            api.post('/ai-metadata', {
                image_id: file.image_id,
                user_id: userId,
                description: file.description || '',
                tags: file.tags,
                colors: topColors,
                ai_processing_status: file.ai_processing_status
            }).catch(err => console.error(err))
        })

        clearAllFiles()
        emit('upload-complete')
        Swal.fire({ position: "top-end", icon: "success", title: "Image successfully uploaded", showConfirmButton: false, timer: 4500 })
    } catch (err) {
        console.error('Upload failed:', err)
    } finally {
        isUploading.value = false
    }
}

const clearAllFiles = () => {
    files.value = []
    if (fileInput.value) fileInput.value.value = ''
}

const removeFile = (index) => files.value.splice(index, 1)
</script>
