export type Nullable<T> = T | null | undefined;

export type WorkLogEntry = {
  fileName: string;
  title: string;
  url: string;
  createdDate: Nullable<string>;
};

export type PresentationEntry = WorkLogEntry & {
  slides?: number;
};

export interface ContentPayload {
  generatedAt: Nullable<string>;
  workLogs: WorkLogEntry[];
  presentations: PresentationEntry[];
}

export type SearchEntryKind = "work-log" | "presentation";

export interface SearchIndexEntry {
  kind: SearchEntryKind;
  title: string;
  fileName: string;
  url: string;
  createdDate: Nullable<string>;
  text: string;
  textLength: number;
}
