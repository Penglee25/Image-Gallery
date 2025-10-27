<template>
    <div class="flex items-center justify-center min-h-screen bg-gray-100">
        <div class="w-full max-w-md bg-white rounded-2xl shadow-lg p-8">
            <h2 class="text-2xl font-semibold text-center text-gray-700 mb-6">
                Create your account
            </h2>

            <form @submit.prevent="handleSignUp" class="space-y-5">
                <div>
                    <label class="block text-gray-600 mb-2">Email</label>
                    <input v-model="email" type="email" placeholder="you@example.com" required
                        class="w-full border border-gray-300 rounded-lg px-4 py-2 focus:outline-none focus:ring-2 focus:ring-blue-500" />
                </div>

                <div>
                    <label class="block text-gray-600 mb-2">Password</label>
                    <input v-model="password" type="password" placeholder="••••••••" required
                        class="w-full border border-gray-300 rounded-lg px-4 py-2 focus:outline-none focus:ring-2 focus:ring-blue-500" />
                </div>

                <div>
                    <label class="block text-gray-600 mb-2">Confirm Password</label>
                    <input v-model="confirmPassword" type="password" placeholder="••••••••" required
                        class="w-full border border-gray-300 rounded-lg px-4 py-2 focus:outline-none focus:ring-2 focus:ring-blue-500" />
                </div>

                <button type="submit" :disabled="loading"
                    class="w-full bg-blue-600 text-white py-2 rounded-lg hover:bg-blue-700 transition duration-200 disabled:opacity-60">
                    {{ loading ? "Creating account..." : "Sign Up" }}
                </button>

                <p v-if="error" class="text-red-500 text-sm mt-2 text-center">
                    {{ error }}
                </p>
            </form>

            <p class="text-center text-sm text-gray-600 mt-6">
                Already have an account?
                <router-link to="/" class="text-blue-600 hover:underline font-medium">
                    Log in
                </router-link>
            </p>
        </div>
    </div>
</template>

<script setup>
import { ref } from "vue";
import api from "../api/axios"; // import your axios instance
import { useRouter } from "vue-router";
import Swal from "sweetalert2";

const router = useRouter();

const email = ref("");
const password = ref("");
const confirmPassword = ref("");
const loading = ref(false);
const error = ref("");

const handleSignUp = async () => {
    if (password.value !== confirmPassword.value) {
        error.value = "Passwords don't match.";
        return;
    }

    loading.value = true;
    error.value = "";

    try {
        const { data } = await api.post("/signup", {
            email: email.value,
            password: password.value,
        });

        Swal.fire({
            position: "top-end",
            icon: "success",
            title: "Account created successfully!",
            showConfirmButton: false,
            timer: 4500
        });
        console.log("✅ Signup success:", data);

        // redirect to login
        router.push("/");
    } catch (err) {
        console.error("Signup error:", err);
        error.value =
            err.response?.data?.detail || "An error occurred during signup.";
    } finally {
        loading.value = false;
    }
};
</script>