/// <reference path="../.astro/types.d.ts" />

interface ImportMetaEnv {
  readonly BACKEND_URL: string;
}

interface ImportMeta {
  readonly env: ImportMetaEnv;
}
