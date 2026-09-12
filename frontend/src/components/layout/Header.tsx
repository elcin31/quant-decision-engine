"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";

export function Header() {
  const pathname = usePathname();
  return (
    <header className="app-header">
      <div className="app-header-inner">
        <Link href="/" className="brand">
          <span className="brand-mark">Q</span>
          <span>QUANT <b>DECISION ENGINE</b></span>
        </Link>
        <nav className="nav" aria-label="Main">
          <Link href="/" aria-current={pathname === "/" ? "page" : undefined}>Research</Link>
          <Link href="/analysis" aria-current={pathname.startsWith("/analysis") ? "page" : undefined}>
            New analysis <span className="nav-plus">+</span>
          </Link>
        </nav>
      </div>
    </header>
  );
}
