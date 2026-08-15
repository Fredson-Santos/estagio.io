import { getViteConfig } from 'astro/config';

export default getViteConfig({
  esbuild: {
    jsx: 'automatic',
  },
  // @ts-ignore
  test: {
    environment: 'node',
    include: ['src/**/*.test.{ts,tsx,js,jsx}'],
  },
});


