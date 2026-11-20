/// <reference types="vite/client" />

interface ImportMetaEnv {
  readonly VITE_CAMPAIGN_PREFIX: string;
}

interface ImportMeta {
  readonly env: ImportMetaEnv;
}
