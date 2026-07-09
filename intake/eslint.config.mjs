// @ts-check

import { defineConfig, globalIgnores } from 'eslint/config'
import eslint from '@eslint/js'
import tseslint from 'typescript-eslint'

export default defineConfig([
  globalIgnores(['dist']),
  eslint.configs.recommended,
  tseslint.configs.recommended,
])
