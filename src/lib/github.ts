// Build-time GitHub stats. Fetched during `astro build` and baked into the
// HTML — there are no client-side or runtime third-party requests. Every call
// is memoized per repo so a multi-page build hits the API only once.
//
// Any failure (offline dev, rate limiting, API hiccup) resolves to `null` so
// the build never breaks; callers render a sensible fallback. In CI we pass
// GITHUB_TOKEN to lift the unauthenticated 60/hr rate limit.

const cache = new Map<string, Promise<number | null>>();

export function getStarCount(repo = "angr/angr"): Promise<number | null> {
  let pending = cache.get(repo);
  if (!pending) {
    pending = fetchStars(repo);
    cache.set(repo, pending);
  }
  return pending;
}

async function fetchStars(repo: string): Promise<number | null> {
  try {
    const headers: Record<string, string> = {
      Accept: "application/vnd.github+json",
      "User-Agent": "angr.io-build",
    };
    const token =
      typeof process !== "undefined" ? process.env?.GITHUB_TOKEN : undefined;
    if (token) headers.Authorization = `Bearer ${token}`;

    const res = await fetch(`https://api.github.com/repos/${repo}`, {
      headers,
      signal: AbortSignal.timeout(5000),
    });
    if (!res.ok) return null;
    const data = await res.json();
    return typeof data?.stargazers_count === "number"
      ? data.stargazers_count
      : null;
  } catch {
    return null;
  }
}

/** Compact star count: 980 → "980", 7480 → "7.5k", 12340 → "12.3k". */
export function formatStars(n: number): string {
  if (n < 1000) return String(n);
  return (n / 1000).toFixed(1).replace(/\.0$/, "") + "k";
}
