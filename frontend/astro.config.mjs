// @ts-check
import { defineConfig } from 'astro/config';
import node from '@astrojs/node';
import react from '@astrojs/react';

import tailwindcss from '@tailwindcss/vite';

// https://astro.build/config
export default defineConfig({
  output: 'server',
  adapter: node({
    mode: 'standalone',
  }),
  security: {
    checkOrigin: true,
    allowedDomains: [{ hostname: 'estagio.io', protocol: 'https' }],
  },
  integrations: [react()],
  vite: {
    plugins: [tailwindcss()],
  },
});

