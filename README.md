# angr.io

The website for the [angr](https://github.com/angr/angr) binary analysis
platform.

## Stack

- **[Astro](https://astro.build)** — static site generation, zero JS by default,
  build-time syntax highlighting (Shiki), view transitions.
- **[Tailwind CSS v4](https://tailwindcss.com)** — utility styling layered on a
  small custom design-token system (see `src/styles/global.css`).
- **Self-hosted assets** — variable fonts ([Inter](https://rsms.me/inter/) +
  [JetBrains Mono](https://www.jetbrains.com/lp/mono/)) and all images are
  bundled locally. No third-party/CDN requests at runtime.

## Develop

```bash
npm install          # install dependencies
npm run dev          # local dev server at http://localhost:4321
npm run check        # astro check (typecheck) — same gate CI runs
npm run build        # production build → dist/
npm run preview      # serve the production build locally
```

No system Node? `./scripts/bootstrap.sh` installs Node, the dependencies, and
the Playwright browser in one idempotent step.

## Structure

```
hero/            recorded-terminal demos for the hero (see hero/README.md)
src/
  assets/        logo, screenshots, hero notebooks (json) + CLI casts
  components/    one .astro file per section (Hero, Features, …)
  data/          content: feature cards, code demos, ecosystem links
  layouts/       Base.astro — <head>, SEO/OG meta, theme init, scroll-reveal
  lib/           icon set (inline SVG line icons)
  pages/         index.astro, 404.astro
  styles/        global.css — design tokens, themes, components, animations
```

## Hero & CLI demos

Both the hero and the CLI section are generated from **real angr scripts** in
[`hero/demos/`](hero/demos/):

- The **hero** is a static IPython-notebook carousel, built by
  `build_notebooks.py` → `src/assets/hero/notebooks.json`.
- The **CLI section** is animated
  [asciinema-player](https://github.com/asciinema/asciinema-player) playback,
  built by `record_cli.py` → `src/assets/cli/*.cast` + `manifest.json`.

The generated artifacts are committed, so the site build never needs angr
installed — only re-generating does. See [hero/README.md](hero/README.md) for the
edit → regenerate → commit workflow (`npm run gen:hero` / `npm run gen:cli`).

## Theming

Color is driven by CSS custom properties that flip on the `data-theme`
attribute (`light` | `dark`). The theme is set before first paint (no flash)
and persisted to `localStorage`, defaulting to the OS preference. To adjust the
palette, edit the token blocks at the top of `src/styles/global.css`.

## Deploy

`.github/workflows/deploy.yml` typechecks and builds on every push and PR, and
publishes `dist/` to GitHub Pages on push to `main`. The custom domain comes from
[`public/CNAME`](public/CNAME). Enable Pages → "GitHub Actions" once.
