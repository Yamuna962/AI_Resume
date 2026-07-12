import { defineConfig, globalIgnores } from "eslint/config";
import nextVitals from "eslint-config-next/core-web-vitals";
import nextTs from "eslint-config-next/typescript";

const eslintConfig = defineConfig([
  ...nextVitals,
  ...nextTs,
  // Override default ignores of eslint-config-next.
  globalIgnores([
    // Keep build outputs ignored, but allow next-env.d.ts so editor diagnostics stay clean.
    ".next/**",
    "out/**",
    "build/**",
  ]),
]);

export default eslintConfig;
