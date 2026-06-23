/**
 * Semantic icon names → Iconify icon ids. Icons come from the locally
 * installed `lucide` and `simple-icons` sets and are inlined at build time
 * by astro-icon — no runtime network requests.
 */
export const ICONS = {
  sigma: "lucide:sigma",
  braces: "lucide:braces",
  "git-graph": "lucide:network",
  binary: "lucide:binary",
  cpu: "lucide:cpu",
  puzzle: "lucide:puzzle",
  terminal: "lucide:square-terminal",
  "git-fork": "lucide:git-fork",
  github: "simple-icons:github",
  discord: "simple-icons:discord",
  book: "lucide:book-open",
  "arrow-right": "lucide:arrow-right",
  "arrow-up-right": "lucide:arrow-up-right",
  download: "lucide:download",
  copy: "lucide:copy",
  check: "lucide:check",
  sun: "lucide:sun",
  moon: "lucide:moon",
  menu: "lucide:menu",
  close: "lucide:x",
  zap: "lucide:zap",
  heart: "lucide:heart",
  "life-buoy": "lucide:life-buoy",
  code: "lucide:code-xml",
  "graduation-cap": "lucide:graduation-cap",
} as const;

export type IconName = keyof typeof ICONS;
