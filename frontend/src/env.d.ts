/// <reference path="../.astro/types.d.ts" />

interface ImportMetaEnv {
  readonly BACKEND_URL: string;
  readonly ADMIN_API_KEY: string;
  readonly ADMIN_PASSWORD: string;
  readonly ADMIN_SECRET: string;
}

interface ImportMeta {
  readonly env: ImportMetaEnv;
}

declare namespace App {
  interface Locals {}
}
