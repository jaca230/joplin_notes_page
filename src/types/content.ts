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
