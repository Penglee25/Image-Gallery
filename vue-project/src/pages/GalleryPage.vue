<template>
    <div :class="darkMode ? 'dark' : ''">
        <div class="min-h-screen bg-gray-100 dark:bg-gray-900 text-gray-900 dark:text-gray-100 transition-colors">
            <nav class="flex items-center justify-between px-6 py-4 bg-white dark:bg-gray-800 shadow">
                <h1 class="text-2xl font-semibold">Image Gallery</h1>

                <div class="flex items-center gap-4">
                    <button @click="toggleDarkMode"
                        class="px-3 py-2 rounded-md bg-gray-200 dark:bg-gray-700 hover:bg-gray-300 dark:hover:bg-gray-600 transition">
                        {{ darkMode ? '🌙 Dark' : '☀️ Light' }}
                    </button>

                    <button @click="handleLogout"
                        class="px-3 py-2 rounded-md bg-red-500 hover:bg-red-600 text-white transition">
                        Logout
                    </button>
                </div>
            </nav>

            <div class="p-6">
                <span class="text-lg font-semibold mb-4">Welcome to your gallery {{ email }}!</span>

                <!-- Drag and Drop -->
                <DragAndDrop />

                <!-- Display Uploaded Images with AI info -->
                <div class="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-4 gap-4 mt-6">
                    <div v-for="file in uploadedImages" :key="file.tempId"
                        class="bg-gray-200 dark:bg-gray-700 rounded-lg p-2">
                        <img :src="file.thumbnail" class="w-full h-32 object-cover rounded-md mb-1" />
                        <div class="text-xs text-gray-800 dark:text-gray-200">
                            <div v-if="file.tags.length">Tags: {{ file.tags.join(', ') }}</div>
                            <div v-if="file.description">Desc: {{ file.description }}</div>
                        </div>
                    </div>
                </div>

            </div>
        </div>
    </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import DragAndDrop from '../components/DragAndDrop.vue'

const router = useRouter()
const darkMode = ref(false)
const uploadedImages = ref([])

const email = localStorage.getItem('email');

const toggleDarkMode = () => {
    darkMode.value = !darkMode.value
    localStorage.setItem('darkMode', darkMode.value)
    document.documentElement.classList.toggle('dark', darkMode.value)
}

const handleLogout = () => {
    localStorage.removeItem('user_id')
    localStorage.removeItem('token')
    router.push('/login')
}

onMounted(() => {
    darkMode.value = localStorage.getItem('darkMode') === 'true'
    document.documentElement.classList.toggle('dark', darkMode.value)
})
</script>

<style>
html {
    transition: background-color 0.3s, color 0.3s;
}
</style>
