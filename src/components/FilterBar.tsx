import type { FC, ReactNode } from "react";

interface FilterBarProps {
  value: string;
  placeholder: string;
  onChange: (next: string) => void;
  onReset: () => void;
  resultLabel: string;
  extraActions?: ReactNode;
}

const FilterBar: FC<FilterBarProps> = ({
  value,
  placeholder,
  onChange,
  onReset,
  resultLabel,
  extraActions,
}) => (
  <div className="mb-4 flex flex-col gap-3 lg:flex-row lg:items-center lg:justify-between">
    <div className="flex w-full gap-3 lg:max-w-xl">
      <input
        type="text"
        placeholder={placeholder}
        value={value}
        onChange={(event) => onChange(event.target.value)}
        className="w-full rounded-xl border border-slate-200 px-4 py-2 text-sm shadow-sm focus:border-brand-blue focus:outline-none focus:ring-2 focus:ring-brand-blue/20"
      />
      {value && (
        <button
          type="button"
          onClick={onReset}
          className="rounded-xl border border-slate-200 px-4 py-2 text-sm font-medium text-slate-700 transition hover:bg-slate-50"
        >
          Clear
        </button>
      )}
    </div>
    <div className="flex flex-wrap items-center gap-3">
      <p className="text-sm text-slate-500">{resultLabel}</p>
      {extraActions}
    </div>
  </div>
);

export default FilterBar;
