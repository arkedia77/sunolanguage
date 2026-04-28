import { defineConfig } from 'vite';
import { resolve } from 'path';

export default defineConfig({
  resolve: {
    alias: {
      '@rag': resolve(__dirname, '../rag'),
      '@reanalysis': resolve(__dirname, '../data/reanalysis_v2'),
    },
  },
});
