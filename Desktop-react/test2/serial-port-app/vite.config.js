import { defineConfig } from 'vite';
import react from '@vitejs/plugin-react';
import electron from 'vite-plugin-electron';

export default defineConfig({
  plugins: [
    react(),
    electron({
      entry: 'electron/main.js',
      onstart: (options) => {
        options.reload();
      },
      vite: {
        build: {
          outDir: 'dist-electron',
          rollupOptions: {
            input: 'electron/main.js',
          },
        },
      },
    }),
  ],
  resolve: {
    extensions: ['.js', '.jsx', '.ts', '.tsx']
  }
});