/// <reference types="vite/client" />

interface ImportMetaEnv {
  readonly VITE_API_URL: string
  readonly VITE_WS_URL: string
  readonly VITE_ENABLE_OFFLINE: string
  readonly VITE_CAMERA_ANALYSIS_INTERVAL: string
}

interface ImportMeta {
  readonly env: ImportMetaEnv
}
