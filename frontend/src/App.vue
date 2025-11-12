<template>
  <div id="app">
    <div class="app-content">
      <RouterView />
    </div>
    <Footer />
  </div>
</template>

<script setup lang="ts">
import { RouterView } from 'vue-router'
import Footer from './components/Footer.vue'
</script>

<style scoped>
#app {
  min-height: 100vh;
  background-color: #f5f5f5;
  display: flex;
  flex-direction: column;
}

.app-content {
  flex: 1;
}
</style> 