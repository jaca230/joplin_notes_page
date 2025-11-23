import type { FC } from "react";
import { NavLink as RouterNavLink } from "react-router-dom";

export interface NavLink {
  to: string;
  label: string;
}

interface NavBarProps {
  links: NavLink[];
  lastRefreshedLabel: string;
}

const NavBar: FC<NavBarProps> = ({ links, lastRefreshedLabel }) => (
  <header className="bg-slate-900 text-white shadow-sm">
    <div className="mx-auto flex max-w-6xl items-center justify-between px-4 py-4">
      <div>
        <RouterNavLink className="text-lg font-semibold tracking-tight" to="/">
          Jack Carlton&apos;s Notes Page
        </RouterNavLink>
        <p className="text-xs text-slate-300">
          Last refreshed:
          <span className="ml-1 font-semibold text-white">{lastRefreshedLabel}</span>
        </p>
      </div>
      <nav className="flex gap-6 text-sm">
        {links.map((link) => (
          <RouterNavLink
            key={link.to}
            to={link.to}
            className={({ isActive }) =>
              [
                "text-slate-200 transition hover:text-white",
                isActive ? "font-semibold text-white" : "",
              ]
                .filter(Boolean)
                .join(" ")
            }
          >
            {link.label}
          </RouterNavLink>
        ))}
      </nav>
    </div>
  </header>
);

export default NavBar;
