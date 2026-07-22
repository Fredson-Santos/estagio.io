import { getViteConfig } from 'astro/config';

export default getViteConfig({
  // @ts-ignore
  test: {
    environment: 'node',
    include: ['src/**/*.test.{ts,tsx,js,jsx}'],
  },
});
