<template>
    <div class="min-h-screen flex items-center justify-center bg-gray-100">
        <div class="bg-white shadow-lg rounded-lg w-full max-w-md p-8">
            <h2 class="text-2xl font-bold text-center mb-6">Login</h2>

            <form @submit.prevent="handleLogin" class="space-y-5">
                <div>
                    <label class="block text-gray-700 mb-2">Email</label>
                    <input v-model="email" type="email" placeholder="Enter your email"
                        class="w-full border rounded-lg px-4 py-2 focus:outline-none focus:ring-2 focus:ring-blue-500"
                        required />
                </div>

                <div>
                    <label class="block text-gray-700 mb-2">Password</label>
                    <input v-model="password" type="password" placeholder="Enter your password"
                        class="w-full border rounded-lg px-4 py-2 focus:outline-none focus:ring-2 focus:ring-blue-500"
                        required />
                </div>

                <button type="submit"
                    class="w-full bg-blue-600 text-white py-2 rounded-lg hover:bg-blue-700 transition disabled:opacity-50"
                    :disabled="loading">
                    {{ loading ? 'Logging in...' : 'Login' }}
                </button>

                <p class="text-center text-gray-500 text-sm mt-3">
                    Don’t have an account?
                    <RouterLink to="/signup" class="text-blue-600 hover:underline">Sign up</RouterLink>
                </p>

                <p v-if="errorMessage" class="mt-4 text-center text-sm text-red-600">
                    {{ errorMessage }}
                </p>
            </form>
        </div>
    </div>
</template>

<script setup>
import { ref } from 'vue';
import api from '../api/axios';
import { useRouter } from 'vue-router';
import { showToast } from '../utils/toast';


const email = ref('');
const password = ref('');
const errorMessage = ref('');
const success = ref(false);
const loading = ref(false);
const router = useRouter();

const handleLogin = async () => {
    loading.value = true;

    try {
        const response = await api.post('/login', {
            email: email.value,
            password: password.value,
        });

        success.value = true;

        showToast("success", "Login successful");

        // Optionally store token for authenticated routes
        localStorage.setItem('token', response.data.access_token);
        localStorage.setItem('user_id', response.data.user_id);
        localStorage.setItem('email', response.data.email);

        setTimeout(() => {
            router.push('/gallery');
        }, 1000);
    } catch (error) {
        success.value = false;
        errorMessage.value =
            error.response?.data?.detail || 'Invalid credentials. Please try again.';
    } finally {
        loading.value = false;
    }
};
</script>