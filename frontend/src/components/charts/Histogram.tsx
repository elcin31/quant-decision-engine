"use client";

interface HistogramProps {
  binEdges: number[];
  counts: number[];
  height?: number;
  highlight?: number;
}

export function Histogram({ binEdges, counts, height = 200, highlight }: HistogramProps) {
  if (!counts.length || binEdges.length < 2) {
    return <div className="state-box">No distribution data</div>;
  }
  const maxC = Math.max(...counts, 1);
  const pad = { t: 12, r: 12, b: 28, l: 40 };
  const w = 640;
  const h = height;
  const iw = w - pad.l - pad.r;
  const ih = h - pad.t - pad.b;
  const n = counts.length;
  const barW = iw / n;
  const xmin = binEdges[0]!;
  const xmax = binEdges[binEdges.length - 1]!;

  return (
    <div className="chart-wrap" role="img" aria-label="Histogram">
      <svg className="chart-svg" viewBox={`0 0 ${w} ${h}`} preserveAspectRatio="xMidYMid meet">
        {counts.map((c, i) => {
          const barH = (c / maxC) * ih;
          const x = pad.l + i * barW;
          const y = pad.t + ih - barH;
          const mid = (binEdges[i]! + binEdges[i + 1]!) / 2;
          const isHi =
            highlight !== undefined &&
            mid >= highlight - (xmax - xmin) * 0.02 &&
            mid <= highlight + (xmax - xmin) * 0.02;
          return (
            <rect
              key={i}
              x={x + 1}
              y={y}
              width={Math.max(barW - 2, 1)}
              height={barH}
              fill={isHi ? "#e9c56d" : "#d7ff4f"}
              opacity={0.85}
            />
          );
        })}
        <line x1={pad.l} x2={w - pad.r} y1={h - pad.b} y2={h - pad.b} stroke="#252a2f" />
        <text x={pad.l} y={h - 8} fill="#5e666d" fontSize={10} fontFamily="DM Mono, ui-monospace, monospace">
          {xmin.toFixed(1)}
        </text>
        <text
          x={w - pad.r}
          y={h - 8}
          textAnchor="end"
          fill="#5e666d"
          fontSize={10}
          fontFamily="DM Mono, ui-monospace, monospace"
        >
          {xmax.toFixed(1)}
        </text>
      </svg>
    </div>
  );
}
