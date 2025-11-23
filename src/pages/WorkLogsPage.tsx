import { useMemo, useState } from "react";
import type { ReactNode } from "react";
import FilterBar from "../components/FilterBar";
import SectionCard from "../components/SectionCard";
import type { WorkLogEntry } from "../types/content";
import {
  buildCsv,
  buildSnippet,
  matchesMetadata,
  matchesTextContent,
  formatDate,
  pluralizeEntries,
  triggerCsvDownload,
} from "../utils/dataHelpers";

type SortColumn = "title" | "createdDate";
type SortDirection = "asc" | "desc";

interface WorkLogsPageProps {
  workLogs: WorkLogEntry[];
  searchTexts: Record<string, string>;
}

const escapeRegExp = (value: string) => value.replace(/[.*+?^${}()|[\]\\]/g, "\\$&");

const renderSnippet = (text: string | undefined, term: string) => {
  const snippet = buildSnippet(text, term);
  if (!snippet || !term.trim()) {
    return null;
  }
  const regex = new RegExp(escapeRegExp(term), "ig");
  const nodes: ReactNode[] = [];
  let lastIndex = 0;
  let match: RegExpExecArray | null;
  while ((match = regex.exec(snippet)) !== null) {
    if (match.index > lastIndex) {
      nodes.push(snippet.slice(lastIndex, match.index));
    }
    nodes.push(
      <mark key={`worklog-snippet-${match.index}`} className="bg-yellow-200 px-0.5">
        {snippet.slice(match.index, regex.lastIndex)}
      </mark>
    );
    lastIndex = regex.lastIndex;
  }
  if (lastIndex < snippet.length) {
    nodes.push(snippet.slice(lastIndex));
  }
  return nodes;
};

const SortIndicator = ({ active, direction }: { active: boolean; direction: SortDirection }) => (
  <span className="text-xs text-slate-500">{active ? (direction === "asc" ? "▲" : "▼") : "↕"}</span>
);

const WorkLogsPage = ({ workLogs, searchTexts }: WorkLogsPageProps) => {
  const [filterValue, setFilterValue] = useState("");
  const [sortConfig, setSortConfig] = useState<{ column: SortColumn; direction: SortDirection }>({
    column: "createdDate",
    direction: "desc",
  });

  const normalizedFilter = filterValue.trim().toLowerCase();

  const filtered = useMemo(() => {
    if (!normalizedFilter) {
      return workLogs;
    }
    return workLogs.filter((log) => {
      const metadataMatch = matchesMetadata(log, filterValue);
      const textMatch = matchesTextContent(searchTexts[log.fileName], filterValue);
      return metadataMatch || textMatch;
    });
  }, [workLogs, filterValue, normalizedFilter, searchTexts]);

  const sorted = useMemo(() => {
    const items = [...filtered];
    items.sort((a, b) => {
      const { column, direction } = sortConfig;
      let comparison = 0;

      if (column === "title") {
        comparison = a.title.localeCompare(b.title);
      } else {
        const aValue = a.createdDate ? new Date(a.createdDate).getTime() : -Infinity;
        const bValue = b.createdDate ? new Date(b.createdDate).getTime() : -Infinity;
        comparison = aValue - bValue;
      }

      return direction === "asc" ? comparison : -comparison;
    });
    return items;
  }, [filtered, sortConfig]);

  const handleSort = (column: SortColumn) => {
    setSortConfig((prev) => {
      if (prev.column === column) {
        return { column, direction: prev.direction === "asc" ? "desc" : "asc" };
      }
      return { column, direction: column === "title" ? "asc" : "desc" };
    });
  };

  const exportCsv = () => {
    const csv = buildCsv(
      ["File Name", "Creation Date", "Link"],
      sorted.map((log) => [log.title, formatDate(log.createdDate), log.url])
    );
    triggerCsvDownload("work-logs.csv", csv);
  };

  return (
    <SectionCard
      id="work-logs"
      title="Work Logs"
      description="Sortable table of exported Joplin HTML files."
      actions={
        <button
          type="button"
          onClick={exportCsv}
          className="rounded-lg border border-slate-200 px-4 py-2 text-sm font-medium text-slate-700 transition hover:bg-slate-50"
        >
          Export CSV
        </button>
      }
    >
      <FilterBar
        value={filterValue}
        placeholder="Search titles, dates, and file contents"
        onChange={setFilterValue}
        onReset={() => setFilterValue("")}
        resultLabel={pluralizeEntries(sorted.length)}
      />
      <div className="overflow-x-auto">
        <table className="min-w-full divide-y divide-slate-200 text-sm">
          <thead className="bg-slate-100 text-left text-xs font-semibold uppercase tracking-wider text-slate-600">
            <tr>
              <th className="px-4 py-3">
                <button
                  type="button"
                  onClick={() => handleSort("title")}
                  className="flex w-full items-center gap-1"
                >
                  File Name
                  <SortIndicator active={sortConfig.column === "title"} direction={sortConfig.direction} />
                </button>
              </th>
              <th className="w-48 px-4 py-3">
                <button
                  type="button"
                  onClick={() => handleSort("createdDate")}
                  className="flex w-full items-center gap-1"
                >
                  Creation Date
                  <SortIndicator
                    active={sortConfig.column === "createdDate"}
                    direction={sortConfig.direction}
                  />
                </button>
              </th>
            </tr>
          </thead>
          <tbody className="divide-y divide-slate-100">
            {sorted.length === 0 ? (
              <tr>
                <td colSpan={2} className="px-4 py-6 text-center text-slate-500">
                  No work logs matched your search.
                </td>
              </tr>
            ) : (
              sorted.map((log) => (
                <tr key={log.fileName} className="hover:bg-slate-50">
                  <td className="px-4 py-3 font-medium text-brand-blue">
                    <a href={log.url} target="_blank" rel="noreferrer">
                      {log.title}
                    </a>
                    {normalizedFilter && (
                      <p className="mt-1 text-xs italic text-slate-500">
                        {renderSnippet(searchTexts[log.fileName], filterValue)}
                      </p>
                    )}
                  </td>
                  <td className="px-4 py-3 text-slate-600">{formatDate(log.createdDate)}</td>
                </tr>
              ))
            )}
          </tbody>
        </table>
      </div>
    </SectionCard>
  );
};

export default WorkLogsPage;
