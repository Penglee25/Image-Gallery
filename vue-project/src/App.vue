<template>
  <div class="min-h-screen flex flex-col dark:bg-gray-900 text-gray-900">
    <main class="flex-1 p-4">
      <RouterView />
    </main>
  </div>
</template>

<script setup>
import { RouterView, RouterLink } from 'vue-router'
</script>

<style scoped>
a.router-link-active {
  font-weight: bold;
  text-decoration: underline;
}
</style>
