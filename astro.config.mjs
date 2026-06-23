// @ts-check
import { defineConfig } from "astro/config";
import tailwindcss from "@tailwindcss/vite";
import sitemap from "@astrojs/sitemap";
import icon from "astro-icon";

// https://astro.build/config
export default defineConfig({
  site: "https://angr.io",
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
