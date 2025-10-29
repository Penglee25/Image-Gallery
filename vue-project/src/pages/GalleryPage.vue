<template>
    <div :class="darkMode ? 'dark' : ''">
        <div class="min-h-screen bg-gray-100 dark:bg-gray-900 text-gray-900 dark:text-gray-100 transition-colors">
            <!-- Navbar -->
            <nav class="flex items-center justify-between px-6 py-4 bg-white dark:bg-gray-800 shadow">
                <div class="w-full flex flex-col md:flex-row items-start justify-between gap-4">
                    <h1 class="text-xl font-semibold">Image Gallery</h1>

                    <div class="flex gap-2 justify-end">
                        <span class="text-lg font-semibold">Welcome, {{ email }}!</span>

                        <div class="flex gap-2">
                            <button @click="toggleDarkMode"
                                class="px-3 py-2 rounded-md bg-gray-200 dark:bg-gray-700 hover:bg-gray-300 dark:hover:bg-gray-600 transition">
                                {{ darkMode ? '🌙 Dark' : '☀️ Light' }}
                            </button>
                            <button @click="handleLogout"
                                class="px-3 py-2 rounded-md bg-red-500 hover:bg-red-600 text-white transition">
                                Logout
                            </button>
                        </div>
                    </div>
                </div>
            </nav>

            <div class="p-6">
                <DragAndDrop @upload-complete="fetchGallery" />

                <!-- Search -->
                <div class="flex gap-2 mb-4 mt-6">
                    <input v-model="searchQuery" type="text" placeholder="Search by description or tags..."
                        class="border rounded px-3 py-2 flex-1" />
                </div>

                <div class="bg-white dark:bg-gray-800 rounded-lg p-5">
                    <div class="flex gap-2 justify-end w-full" v-if="selectedColor || similarTags.length">
                        <div class="mb-4 text-sm text-gray-500">
                            <span v-if="selectedColor">🎨 Color: <b>{{ selectedColor }}</b></span>
                            <span v-if="similarTags.length"> | Similar tags: <b>{{ similarTags.join(', ') }}</b></span>
                        </div>
                        <span @click="clearFilters" class="cursor-pointer">⛔</span>
                    </div>

                    <div class="text-right">
                        <button @click="exportJSON" v-if="selectedColor || similarTags.length"
                            class="px-3 py-1 bg-indigo-500 text-white rounded-md text-xs hover:bg-indigo-600 my-2 ml-2">
                            📥 Export JSON
                        </button>
                    </div>


                    <!-- Gallery Grid -->
                    <div v-if="gallery.length" class="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-4 gap-4">
                        <div v-for="img in gallery" :key="img.image_id"
                            class="bg-white dark:bg-gray-800 rounded-lg shadow p-2">
                            <img :src="`${SUPABASE_STORAGE_URL}/${img.user_id}/${img.filename}`"
                                class="w-full h-48 object-contain rounded" alt="thumbnail" />

                            <div class="mt-2 text-xs">
                                <p class="line-clamp-2"><b>Description:</b> {{ img.description }}</p>
                                <div class="flex gap-1 mt-2">
                                    <b>Color:</b>
                                    <div v-for="color in img.colors" :key="color" :style="{ backgroundColor: color }"
                                        class="w-4 h-4 rounded border cursor-pointer" @click="filterByColor(color)">
                                    </div>
                                </div>
                                <div class="mt-1 flex flex-wrap gap-1">
                                    <b>Tags:</b>
                                    <span v-for="tag in img.tags" :key="tag"
                                        class="bg-gray-100 dark:bg-gray-700 text-gray-700 dark:text-gray-300 px-1.5 py-0.5 rounded text-xs">#{{
                                            tag }}</span>
                                </div>

                                <div class="flex flex-row gap-2 mt-2">
                                    <button @click="findSimilar(img)"
                                        class="px-4 py-2 bg-blue-600 text-white rounded-md text-sm hover:bg-blue-700">
                                        Find Similar
                                    </button>

                                    <button @click="openTagEditor(img)"
                                        class="px-4 py-2 bg-green-600 text-white rounded-md text-sm hover:bg-green-700">
                                        ✏️ Edit Tags
                                    </button>

                                    <button @click="downloadImage(img)"
                                        class="bg-white text-gray-800 rounded-full p-2 hover:bg-gray-100 mx-1"
                                        title="Download">
                                        <svg xmlns="http://www.w3.org/2000/svg" class="w-5 h-5" fill="none"
                                            viewBox="0 0 24 24" stroke="currentColor" stroke-width="2">
                                            <path stroke-linecap="round" stroke-linejoin="round"
                                                d="M4 16v2a2 2 0 002 2h12a2 2 0 002-2v-2M7 10l5 5 5-5M12 15V3" />
                                        </svg>
                                    </button>
                                </div>

                            </div>
                        </div>
                    </div>

                    <p v-else class="text-gray-400 mt-10 text-center">No images found.</p>

                    <!-- Pagination -->
                    <div v-if="totalPages > 1" class="flex justify-center items-center gap-4 mt-6">
                        <button @click="prevPage" :disabled="page <= 1"
                            class="px-3 py-2 bg-gray-200 dark:bg-gray-700 rounded disabled:opacity-50">Previous</button>
                        <span>Page {{ page }} / {{ totalPages }}</span>
                        <button @click="nextPage" :disabled="page >= totalPages"
                            class="px-3 py-2 bg-gray-200 dark:bg-gray-700 rounded disabled:opacity-50">Next</button>
                    </div>
                </div>
            </div>

            <!-- Modal -->
            <div v-if="showTagModal" class="fixed inset-0 flex items-center justify-center bg-black bg-opacity-50 z-50">
                <div class="bg-white dark:bg-gray-800 p-6 rounded-lg w-96 shadow-lg">
                    <h2 class="text-lg font-semibold mb-4">Edit Tags</h2>
                    <textarea v-model="editableTags" rows="4"
                        class="w-full border rounded px-3 py-2 text-sm dark:bg-gray-700 dark:text-white"></textarea>
                    <div class="flex justify-end gap-2 mt-4">
                        <button @click="showTagModal = false"
                            class="px-4 py-2 bg-gray-300 dark:bg-gray-700 rounded">Cancel</button>
                        <button @click="saveTags"
                            class="px-4 py-2 bg-green-600 text-white rounded hover:bg-green-700">Save</button>
                    </div>
                </div>
            </div>
        </div>
    </div>
</template>

<script setup>
import { ref, watch, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import DragAndDrop from '../components/DragAndDrop.vue'
import api from '../api/axios'
import { showToast } from '../utils/toast'

const router = useRouter()
const darkMode = ref(false)
const email = localStorage.getItem('email')
const userId = localStorage.getItem('user_id')
const SUPABASE_STORAGE_URL = import.meta.env.VITE_SUPABASE_STORAGE_URL

const gallery = ref([])
const searchQuery = ref('')
const selectedColor = ref(null)
const similarTags = ref([])
const page = ref(1)
const limit = ref(20)
const totalPages = ref(1)

// Modal state
const showTagModal = ref(false)
const editableTags = ref('')
const currentImage = ref(null)



const fetchGallery = async () => {

    try {
        const params = new URLSearchParams()
        if (searchQuery.value) params.append('query', searchQuery.value)
        if (selectedColor.value) params.append('color', selectedColor.value)
        if (similarTags.value.length) params.append('similar_tags', similarTags.value.join(','))
        params.append('page', page.value)
        params.append('limit', limit.value)

        const res = await api.get(`/gallery/search?${params}`, {
            headers: { 'x-user-id': userId },
        })

        // Axios already parses JSON
        const data = res.data

        gallery.value = data.data || []
        totalPages.value = data.total_pages || 1
    } catch (err) {
        console.error('Fetch error:', err)
    }
}

// Edit Tags Modal
const openTagEditor = (img) => {
    currentImage.value = img
    editableTags.value = img.tags.join(', ')
    showTagModal.value = true
}

const saveTags = async () => {
    if (!currentImage.value) return

    try {
        const newTags = editableTags.value
            .split(',')
            .map(t => t.trim())
            .filter(Boolean)

        const res = await api.post(
            `/gallery/update-tags`,
            {
                image_id: String(currentImage.value.image_id),
                tags: newTags,
            },
            {
                headers: {
                    'x-user-id': userId,
                },
            }
        )

        if (res.data.status === 'success') {
            showTagModal.value = false
            fetchGallery()
            showToast("success", "Tags successfully updated");
        } else {
            console.error('Update failed:', res.data.message)
        }
    } catch (err) {
        console.error('Error updating tags:', err.response?.data || err)
    }
}


const downloadImage = (img) => {
    if (!img.filename || !img.user_id) return alert("Invalid image data");

    try {
        const url = `${SUPABASE_STORAGE_URL}/${img.user_id}/${img.filename}`;

        const link = document.createElement('a');
        window.open(url, "_blank");

        link.download = img.filename;
        document.body.appendChild(link);
        link.click();
        document.body.removeChild(link);
    } catch (err) {
        console.error("Download failed:", err);
        alert("Download failed: " + err.message);
    }
}

const exportJSON = () => {
    if (!gallery.value.length) return alert("No data to export");

    try {
        const dataStr = JSON.stringify(gallery.value, null, 2); // Pretty print JSON
        const blob = new Blob([dataStr], { type: "application/json" });
        const url = URL.createObjectURL(blob);
        const link = document.createElement("a");

        link.href = url;
        link.download = `gallery_export_page${page.value}.json`;
        link.target = "_blank"; // optional, opens in new tab
        document.body.appendChild(link);
        link.click();
        document.body.removeChild(link);
        URL.revokeObjectURL(url);
    } catch (err) {
        console.error("Export failed:", err);
        alert("Export failed: " + err.message);
    }
}


const nextPage = () => {
    if (page.value < totalPages.value) {
        page.value++
        fetchGallery()
    }
}
const prevPage = () => {
    if (page.value > 1) {
        page.value--
        fetchGallery()
    }
}

watch([searchQuery, selectedColor, similarTags], () => {
    page.value = 1
    fetchGallery()
}, { deep: true })

onMounted(() => {
    fetchGallery()
    darkMode.value = localStorage.getItem('darkMode') === 'true'
    document.documentElement.classList.toggle('dark', darkMode.value)
})

const filterByColor = (color) => {
    selectedColor.value = color
    searchQuery.value = ''
    similarTags.value = []
}

const findSimilar = (img) => {
    similarTags.value = img.tags || []
    selectedColor.value = null
    searchQuery.value = ''
}

const clearFilters = () => {
    searchQuery.value = ''
    selectedColor.value = null
    similarTags.value = []
    page.value = 1
    fetchGallery()
}

const toggleDarkMode = () => {
    darkMode.value = !darkMode.value
    localStorage.setItem('darkMode', darkMode.value)
    document.documentElement.classList.toggle('dark', darkMode.value)
}

const handleLogout = () => {
    localStorage.removeItem('user_id')
    localStorage.removeItem('token')
    localStorage.removeItem('email')
    router.push('/login')
}
</script>

<style scoped>
.line-clamp-2 {
    overflow: hidden;
    display: -webkit-box;
    -webkit-line-clamp: 2;
    -webkit-box-orient: vertical;
}
</style>
