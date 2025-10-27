<template>
    <div :class="darkMode ? 'dark' : ''">
        <div class="min-h-screen bg-gray-100 dark:bg-gray-900 text-gray-900 dark:text-gray-100 transition-colors">
            <!-- Navbar -->
            <nav class="flex items-center justify-between px-6 py-4 bg-white dark:bg-gray-800 shadow">
                <h1 class="text-2xl font-semibold">Image Gallery</h1>

                <div class="flex items-center gap-4">
                    <!-- Dark Mode Toggle -->
                    <button @click="toggleDarkMode"
                        class="px-3 py-2 rounded-md bg-gray-200 dark:bg-gray-700 hover:bg-gray-300 dark:hover:bg-gray-600 transition">
                        {{ darkMode ? '🌙 Dark' : '☀️ Light' }}
                    </button>

                    <!-- Logout Button -->
                    <button @click="handleLogout"
                        class="px-3 py-2 rounded-md bg-red-500 hover:bg-red-600 text-white transition">
                        Logout
                    </button>
                </div>
            </nav>

            <!-- Main Content -->
            <div class="p-6">
                <h2 class="text-xl font-semibold mb-4">Welcome to your gallery!</h2>


                <DragAndDrop :onFilesSelected="handleFilesSelected" />
                <div class="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-4 gap-4">
                    <!-- Placeholder images -->
                    <div v-for="n in 8" :key="n"
                        class="w-full h-40 bg-gray-300 dark:bg-gray-700 rounded-lg flex items-center justify-center">
                        Image {{ n }}
                    </div>
                </div>
            </div>
        </div>
    </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import api from '../api/axios';
import DragAndDrop from '../components/DragAndDrop.vue'

const router = useRouter()

const darkMode = ref(false)

const images = ref([])

const handleFilesSelected = (files) => {
    files.forEach(file => {
        const reader = new FileReader()
        reader.onload = (e) => {
            images.value.push({
                url: e.target.result,
                tags: [], // populate later from AI
                description: '',
            })
        }
        reader.readAsDataURL(file)
    })
}

const toggleDarkMode = () => {
    darkMode.value = !darkMode.value
    localStorage.setItem('darkMode', darkMode.value)
    document.documentElement.classList.toggle('dark', darkMode.value)
}

const handleLogout = async () => {
    try {
        await api.post('/logout');
        localStorage.removeItem('token')
        router.push('/login')
    } catch (error) {
        console.error('Logout error:', error)
    }
}

onMounted(() => {
    // Keep user's dark mode preference
    darkMode.value = localStorage.getItem('darkMode') === 'true'
    document.documentElement.classList.toggle('dark', darkMode.value)
})
</script>

<style>
/* Optional smooth transition between themes */
html {
    transition: background-color 0.3s, color 0.3s;
}
</style>
