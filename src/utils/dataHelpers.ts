import type { Nullable, PresentationEntry, WorkLogEntry } from "../types/content";

const ensureTrailingSlash = (value: string) => (value.endsWith("/") ? value : `${value}/`);

export const withBasePath = (path: string) => {
  const base = ensureTrailingSlash(import.meta.env.BASE_URL ?? "/");
  const sanitized = path.replace(/^\/+/, "");
  return `${base}${sanitized}`;
};

export const filterEntries = <T extends { title: string; fileName: string; createdDate: Nullable<string> }>(
  items: T[],
  term: string
): T[] => {
  const normalized = term.trim().toLowerCase();
  if (!normalized) {
    return items;
  }

  return items.filter((item) => {
    const haystack = `${item.title} ${item.fileName} ${item.createdDate ?? ""}`.toLowerCase();
    return haystack.includes(normalized);
  });
};

export const formatDate = (value: Nullable<string>) => value ?? "Unknown";

export const formatSlides = (value?: number) => (typeof value === "number" ? value : "—");

export const formatTimestamp = (value: Nullable<string>) => {
  if (!value) {
    return "Unknown";
  }

  const date = new Date(value);
  return Number.isNaN(date.getTime()) ? value : date.toLocaleString();
};

export const pluralizeEntries = (count: number) => `${count} ${count === 1 ? "entry" : "entries"}`;

const normalizeTerm = (term: string) => term.trim().toLowerCase();

export const matchesMetadata = (
  item: { title: string; fileName: string; createdDate: Nullable<string> },
  term: string
) => {
  const normalized = normalizeTerm(term);
  if (!normalized) {
    return true;
  }
  const haystack = `${item.title} ${item.fileName} ${item.createdDate ?? ""}`.toLowerCase();
  return haystack.includes(normalized);
};

export const matchesTextContent = (text: string | undefined, term: string) => {
  const normalized = normalizeTerm(term);
  if (!normalized) {
    return true;
  }
  return (text ?? "").toLowerCase().includes(normalized);
};

export const buildSnippet = (text: string | undefined, term: string, radius = 160) => {
  if (!text || !term.trim()) {
    return "";
  }
  const normalized = normalizeTerm(term);
  const lowerText = text.toLowerCase();
  const index = lowerText.indexOf(normalized);
  if (index === -1) {
    return text.slice(0, radius) + (text.length > radius ? "…" : "");
  }
  const start = Math.max(index - Math.floor(radius / 2), 0);
  const end = Math.min(index + normalized.length + Math.floor(radius / 2), text.length);
  let snippet = text.slice(start, end);
  if (start > 0) {
    snippet = "…" + snippet;
  }
  if (end < text.length) {
    snippet = snippet + "…";
  }
  return snippet;
};

export const buildCsv = (headers: string[], rows: (string | number | undefined)[][]) => {
  const lines = [headers, ...rows]
    .map((cells) =>
      cells
        .map((cell) => {
          const safe = cell ?? "";
          const needsQuotes = /[",\n]/.test(String(safe));
          const escaped = String(safe).replace(/"/g, '""');
          return needsQuotes ? `"${escaped}"` : escaped;
        })
        .join(",")
    )
    .join("\n");

  return lines;
};

export const triggerCsvDownload = (filename: string, csvContent: string) => {
  const blob = new Blob([csvContent], { type: "text/csv;charset=utf-8;" });
  const url = URL.createObjectURL(blob);
  const link = document.createElement("a");
  link.href = url;
  link.download = filename;
  link.style.display = "none";
  document.body.append(link);
  link.click();
  link.remove();
  URL.revokeObjectURL(url);
};

export const getMostRecentEntries = <T extends { createdDate: Nullable<string> }>(items: T[], limit = 5) => {
  return [...items]
    .sort((a, b) => {
      const aValue = a.createdDate ? new Date(a.createdDate).getTime() : -Infinity;
      const bValue = b.createdDate ? new Date(b.createdDate).getTime() : -Infinity;
      return bValue - aValue;
    })
    .slice(0, limit);
};

export const getLatestWorkLog = (workLogs: WorkLogEntry[]) =>
  getMostRecentEntries(workLogs, 1)[0] ?? null;

export const getLatestPresentation = (presentations: PresentationEntry[]) =>
  getMostRecentEntries(presentations, 1)[0] ?? null;
