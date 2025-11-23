import { Navigate, Route, Routes } from "react-router-dom";
import NavBar from "./components/NavBar";
import HomePage from "./pages/HomePage";
import PresentationsPage from "./pages/PresentationsPage";
import WorkLogsPage from "./pages/WorkLogsPage";
import rawContent from "./data/content.json";
import rawSearchIndex from "./data/search-index.json";
import type { ContentPayload, SearchIndexEntry } from "./types/content";

const navLinks = [
  { to: "/", label: "Home" },
  { to: "/work-logs", label: "Work Logs" },
  { to: "/presentations", label: "Presentations" },
];

const content = rawContent as ContentPayload;
const searchIndex = rawSearchIndex as SearchIndexEntry[];

const workLogSearchTexts: Record<string, string> = {};
const presentationSearchTexts: Record<string, string> = {};

searchIndex.forEach((entry) => {
  if (entry.kind === "work-log") {
    workLogSearchTexts[entry.fileName] = entry.text;
  } else if (entry.kind === "presentation") {
    presentationSearchTexts[entry.fileName] = entry.text;
  }
});

const App = () => {
  const workLogs = content.workLogs ?? [];
  const presentations = content.presentations ?? [];
  const lastRefreshedLabel = content.generatedAt
    ? new Date(content.generatedAt).toLocaleString()
    : "Unknown";

  return (
    <div className="min-h-screen bg-slate-50 text-slate-900">
      <NavBar links={navLinks} lastRefreshedLabel={lastRefreshedLabel} />
      <main className="mx-auto w-full max-w-6xl space-y-10 px-4 py-10">
        <Routes>
          <Route
            path="/"
            element={
              <HomePage
                workLogs={workLogs}
                presentations={presentations}
              />
            }
          />
          <Route
            path="/work-logs"
            element={<WorkLogsPage workLogs={workLogs} searchTexts={workLogSearchTexts} />}
          />
          <Route
            path="/presentations"
            element={
              <PresentationsPage presentations={presentations} searchTexts={presentationSearchTexts} />
            }
          />
          <Route path="*" element={<Navigate to="/" replace />} />
        </Routes>
      </main>
    </div>
  );
};

export default App;
