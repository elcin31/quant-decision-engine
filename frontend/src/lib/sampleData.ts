/** Deterministic sample series for demos. No external data. */

export function sampleReturns(n = 60, seed = 42): number[] {
  let s = seed;
  const rand = () => {
    s = (s * 1664525 + 1013904223) % 4294967296;
    return s / 4294967296;
  };
  const out: number[] = [];
  for (let i = 0; i < n; i++) {
    const u1 = Math.max(rand(), 1e-12);
    const u2 = rand();
    const z = Math.sqrt(-2 * Math.log(u1)) * Math.cos(2 * Math.PI * u2);
    out.push(0.0004 + 0.012 * z);
  }
  return out;
}

export function samplePrices(n = 61, start = 100, seed = 42): number[] {
  const rets = sampleReturns(n - 1, seed);
  const prices = [start];
  for (const r of rets) {
    prices.push(prices[prices.length - 1]! * (1 + r));
  }
  return prices;
}

export function sampleBenchmarkReturns(n = 60, seed = 99): number[] {
  return sampleReturns(n, seed).map((r) => r * 0.7);
}

export function sampleMultiReturns(n = 60): number[][] {
  return [sampleReturns(n, 1), sampleReturns(n, 2), sampleReturns(n, 3)];
}

export function parseNumberList(text: string): number[] {
  return text
    .split(/[\s,;]+/)
    .map((s) => s.trim())
    .filter(Boolean)
    .map((s) => Number(s))
    .filter((n) => Number.isFinite(n));
}

export function formatNumber(n: number | null | undefined, digits = 4): string {
  if (n === null || n === undefined || !Number.isFinite(n)) return "—";
  if (Math.abs(n) >= 1000) return n.toFixed(2);
  if (Math.abs(n) >= 1) return n.toFixed(digits);
  return n.toFixed(Math.max(digits, 4));
}

export function formatPct(n: number | null | undefined, digits = 2): string {
  if (n === null || n === undefined || !Number.isFinite(n)) return "—";
  return (n * 100).toFixed(digits) + "%";
}
