// @ts-check

import { defineConfig, globalIgnores } from "eslint/config";
import eslint from '@eslint/js';
import tseslint from 'typescript-eslint';

export default defineConfig([
  // Ignore date-input as the code is copied from a defunct github repo; we will replace this rather than correct it.
  globalIgnores(["src/comps/date-input"]),
  eslint.configs.recommended,
  tseslint.configs.recommended,
]);
