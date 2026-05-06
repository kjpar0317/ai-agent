const trimSlash = (s: string) => s.replace(/\/$/, "");

export function apiUrl(path: string): string {
  const base = trimSlash(import.meta.env.VITE_API_BASE_URL ?? "");
  if (!base) {
    return path.startsWith("/") ? path : `/${path}`;
  }
  const p = path.startsWith("/") ? path : `/${path}`;
  return `${trimSlash(base)}${p}`;
}
