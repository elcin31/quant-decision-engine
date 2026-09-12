import type { Metadata } from "next";
import "@/styles/globals.css";
import { Header } from "@/components/layout/Header";

export const metadata: Metadata = {
  title: "Quant Decision Engine",
  description: "Quantitative research and decision-support calculation engine",
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en">
      <body>
        <div className="app-shell">
          <Header />
          <main className="app-main">{children}</main>
          <footer className="app-footer">
            <span>QDE / 0.1</span>
            <span>Research calculations only</span>
            <span>Not financial advice</span>
          </footer>
        </div>
      </body>
    </html>
  );
}
