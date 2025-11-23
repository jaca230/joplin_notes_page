import { useMemo, useState } from "react";
import FilterBar from "../components/FilterBar";
import SectionCard from "../components/SectionCard";
import type { PresentationEntry } from "../types/content";
import {
  buildCsv,
  filterEntries,
  formatDate,
  formatSlides,
  pluralizeEntries,
  triggerCsvDownload,
} from "../utils/dataHelpers";

type SortColumn = "title" | "slides" | "createdDate";
type SortDirection = "asc" | "desc";

interface PresentationsPageProps {
  presentations: PresentationEntry[];
}

const SortIndicator = ({ active, direction }: { active: boolean; direction: SortDirection }) => (
  <span className="text-xs text-slate-500">{active ? (direction === "asc" ? "▲" : "▼") : "↕"}</span>
);

const PresentationsPage = ({ presentations }: PresentationsPageProps) => {
  const [filterValue, setFilterValue] = useState("");
  const [sortConfig, setSortConfig] = useState<{ column: SortColumn; direction: SortDirection }>({
    column: "createdDate",
    direction: "desc",
  });

  const filtered = useMemo(
    () => filterEntries(presentations, filterValue),
    [presentations, filterValue]
  );

  const sorted = useMemo(() => {
    const items = [...filtered];
    items.sort((a, b) => {
      const { column, direction } = sortConfig;
      let comparison = 0;

      if (column === "title") {
        comparison = a.title.localeCompare(b.title);
      } else if (column === "slides") {
        const aSlides = a.slides ?? -Infinity;
        const bSlides = b.slides ?? -Infinity;
        comparison = aSlides - bSlides;
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
      ["File Name", "Slides", "Creation Date", "Link"],
      sorted.map((deck) => [deck.title, deck.slides ?? "", formatDate(deck.createdDate), deck.url])
    );
    triggerCsvDownload("presentations.csv", csv);
  };

  return (
    <SectionCard
      id="presentations"
      title="Presentations"
      description="Sortable archive of exported Google Slides decks."
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
        placeholder="Filter by deck name or date"
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
              <th className="w-32 px-4 py-3">
                <button
                  type="button"
                  onClick={() => handleSort("slides")}
                  className="flex w-full items-center gap-1"
                >
                  Slides
                  <SortIndicator active={sortConfig.column === "slides"} direction={sortConfig.direction} />
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
                <td colSpan={3} className="px-4 py-6 text-center text-slate-500">
                  No presentations matched your search.
                </td>
              </tr>
            ) : (
              sorted.map((deck) => (
                <tr key={deck.fileName} className="hover:bg-slate-50">
                  <td className="px-4 py-3 font-medium text-brand-blue">
                    <a href={deck.url} target="_blank" rel="noreferrer">
                      {deck.title}
                    </a>
                  </td>
                  <td className="px-4 py-3 text-slate-600">{formatSlides(deck.slides)}</td>
                  <td className="px-4 py-3 text-slate-600">{formatDate(deck.createdDate)}</td>
                </tr>
              ))
            )}
          </tbody>
        </table>
      </div>
    </SectionCard>
  );
};

export default PresentationsPage;
