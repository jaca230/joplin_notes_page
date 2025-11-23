import { Link } from "react-router-dom";
import SectionCard from "../components/SectionCard";
import type { PresentationEntry, WorkLogEntry } from "../types/content";
import {
  getMostRecentEntries,
  getLatestPresentation,
  getLatestWorkLog,
  withBasePath,
} from "../utils/dataHelpers";
interface HomePageProps {
  workLogs: WorkLogEntry[];
  presentations: PresentationEntry[];
}

const StatCard = ({ label, value }: { label: string; value: string | number }) => (
  <div className="rounded-2xl border border-slate-200 bg-white p-4 text-center shadow-sm">
    <p className="text-xs uppercase text-slate-500">{label}</p>
    <p className="mt-2 text-2xl font-semibold text-slate-900">{value}</p>
  </div>
);

const HomePage = ({ workLogs, presentations }: HomePageProps) => {
  const recentLogs = getMostRecentEntries(workLogs, 4);
  const recentDecks = getMostRecentEntries(presentations, 4);
  const latestLog = getLatestWorkLog(workLogs);
  const latestPresentation = getLatestPresentation(presentations);

  return (
    <div className="space-y-10">
      <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-4">
        <StatCard label="Work Logs" value={workLogs.length} />
        <StatCard label="Presentations" value={presentations.length} />
        <StatCard label="Last Uploaded Work Log" value={latestLog?.createdDate ?? "Unknown"} />
        <StatCard label="Last Uploaded Presentation" value={latestPresentation?.createdDate ?? "Unknown"} />
      </div>

      <SectionCard
        id="recent-work"
        title="Recent Work Logs"
        description="Newest log exports at a glance."
        actions={
          <Link className="text-sm font-medium text-brand-blue" to="/work-logs">
            View all logs →
          </Link>
        }
      >
        {recentLogs.length === 0 ? (
          <p className="text-sm text-slate-500">No work logs available yet.</p>
        ) : (
          <ul className="divide-y divide-slate-100">
            {recentLogs.map((log) => (
              <li key={log.fileName} className="flex items-center justify-between py-3 text-sm">
                <div className="flex flex-col">
                  <a
                    className="font-medium text-brand-blue"
                    href={withBasePath(log.url)}
                    target="_blank"
                    rel="noreferrer"
                  >
                    {log.title}
                  </a>
                  <span className="text-slate-500">{log.createdDate ?? "Unknown"}</span>
                </div>
                <Link className="text-xs font-semibold text-brand-blue" to="/work-logs">
                  Details
                </Link>
              </li>
            ))}
          </ul>
        )}
      </SectionCard>

      <SectionCard
        id="recent-presentations"
        title="Recent Presentations"
        description="Latest decks exported from Google Drive."
        actions={
          <Link className="text-sm font-medium text-brand-blue" to="/presentations">
            View all decks →
          </Link>
        }
      >
        {recentDecks.length === 0 ? (
          <p className="text-sm text-slate-500">No presentations available yet.</p>
        ) : (
          <ul className="divide-y divide-slate-100">
            {recentDecks.map((deck) => (
              <li key={deck.fileName} className="flex items-center justify-between py-3 text-sm">
                <div className="flex flex-col">
                  <a
                    className="font-medium text-brand-blue"
                    href={withBasePath(deck.url)}
                    target="_blank"
                    rel="noreferrer"
                  >
                    {deck.title}
                  </a>
                  <span className="text-slate-500">
                    {deck.createdDate ?? "Unknown"} · {deck.slides ?? "—"} slides
                  </span>
                </div>
                <Link className="text-xs font-semibold text-brand-blue" to="/presentations">
                  Details
                </Link>
              </li>
            ))}
          </ul>
        )}
      </SectionCard>
    </div>
  );
};

export default HomePage;
