// @ts-check
import { defineConfig } from "astro/config";
import tailwindcss from "@tailwindcss/vite";
import sitemap from "@astrojs/sitemap";
import icon from "astro-icon";

// https://astro.build/config
// Default to the production apex domain. The deploy workflow overrides these
// (via configure-pages) for project-page test deploys served under a subpath,
// e.g. https://angr.github.io/angr.io-next/. Normalize base to a trailing slash
// so `${import.meta.env.BASE_URL}foo` joins cleanly.
const SITE = process.env.SITE_URL || "https://angr.io";
const RAW_BASE = process.env.BASE_PATH || "/";
const BASE = RAW_BASE.endsWith("/") ? RAW_BASE : `${RAW_BASE}/`;

export default defineConfig({
  site: SITE,
  base: BASE,
  // Output a fully static site for GitHub Pages.
  output: "static",
  trailingSlash: "ignore",
  integrations: [sitemap(), icon()],
  build: {
    // Emit /about/index.html style files for clean URLs on static hosts.
    format: "directory",
  },
  prefetch: {
    prefetchAll: true,
    defaultStrategy: "viewport",
  },
  vite: {
    plugins: [tailwindcss()],
  },
  markdown: {
    shikiConfig: {
      // Dual-theme syntax highlighting; toggled via CSS variables.
      themes: {
        light: "github-light",
        dark: "github-dark",
      },
    },
  },
});
