import type { FC, ReactNode } from "react";

interface SectionCardProps {
  id: string;
  title: string;
  description?: string;
  actions?: ReactNode;
  children: ReactNode;
}

const SectionCard: FC<SectionCardProps> = ({
  id,
  title,
  description,
  actions,
  children,
}) => (
  <section id={id} className="rounded-2xl bg-white p-6 shadow">
    <div className="mb-4 flex flex-col gap-2 sm:flex-row sm:items-center sm:justify-between">
      <div>
        <h2 className="text-xl font-semibold text-slate-900">{title}</h2>
        {description && <p className="text-sm text-slate-500">{description}</p>}
      </div>
      {actions && <div className="flex shrink-0 gap-3">{actions}</div>}
    </div>
    {children}
  </section>
);

export default SectionCard;
