import { defineConfig } from 'vite';
export default defineConfig({
  base: './',
  build: {
    rollupOptions: {
      input: ['index.html', 'research.html', 'projects.html', 'films.html'],
      output: {
        manualChunks(id) {
          if (id.includes('/three/examples/')) return 'three-extras';
          if (id.includes('/three/')) return 'three-core';
          if (id.includes('/gsap/')) return 'motion';
        },
      },
    },
    chunkSizeWarningLimit: 800,
  },
});
