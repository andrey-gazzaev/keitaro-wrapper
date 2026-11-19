import react from '@vitejs/plugin-react';
import { fileURLToPath } from 'node:url';
import { defineConfig } from 'vite';

/** Dev server and production build. */
export default defineConfig({
  plugins: [react()],
  resolve: {
    alias: { '@': fileURLToPath(new URL('./src', import.meta.url)) },
  },
  server: {
    host: '127.0.0.1',
    port: 5173,
    strictPort: true,
    proxy: {
      '/health': 'http://127.0.0.1:8000',
      '/campaigns': {
        target: 'http://127.0.0.1:8000',
        bypass(req) {
          const accept = req.headers.accept ?? '';

          if (accept.includes('text/html')) {
            return '/index.html';
          }
        },
      },
    },
  },
});
