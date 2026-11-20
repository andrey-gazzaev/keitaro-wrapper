import react from '@vitejs/plugin-react';
import { fileURLToPath } from 'node:url';
import { defineConfig, loadEnv } from 'vite';

const repoRoot = fileURLToPath(new URL('../..', import.meta.url));

/** Dev server and production build. */
export default defineConfig(({ mode }) => {
  const env = loadEnv(mode, repoRoot, '');
  const prefix = env.CAMPAIGN_PREFIX || process.env.CAMPAIGN_PREFIX || '';

  return {
    plugins: [react()],
    define: {
      'import.meta.env.VITE_CAMPAIGN_PREFIX': JSON.stringify(prefix),
    },
    resolve: {
      alias: { '@': fileURLToPath(new URL('./src', import.meta.url)) },
    },
    server: {
      host: '127.0.0.1',
      port: 5173,
      strictPort: true,
      proxy: {
        '/health': 'http://127.0.0.1:8000',
        '/offers': 'http://127.0.0.1:8000',
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
  };
});
