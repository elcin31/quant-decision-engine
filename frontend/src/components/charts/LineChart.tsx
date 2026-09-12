"use client";

interface LineChartProps {
  series: { id: string; label: string; values: number[]; color?: string }[];
  height?: number;
  yFormat?: (v: number) => string;
}

const COLORS = ["#d7ff4f", "#a9e95f", "#e9c56d", "#ff6b72", "#8c9399"];

export function LineChart({ series, height = 220, yFormat }: LineChartProps) {
  if (!series.length || !series[0]?.values.length) {
    return <div className="state-box">No series data</div>;
  }
  const n = Math.max(...series.map((s) => s.values.length));
  const all = series.flatMap((s) => s.values);
  let ymin = Math.min(...all);
  let ymax = Math.max(...all);
  if (ymin === ymax) {
    ymin -= 1;
    ymax += 1;
  }
  const pad = { t: 12, r: 12, b: 28, l: 48 };
  const w = 640;
  const h = height;
  const iw = w - pad.l - pad.r;
  const ih = h - pad.t - pad.b;
  const sx = (i: number) => pad.l + (i / Math.max(n - 1, 1)) * iw;
  const sy = (v: number) => pad.t + ((ymax - v) / (ymax - ymin)) * ih;

  const ticks = 4;
  const yTicks = Array.from({ length: ticks + 1 }, (_, i) => ymin + ((ymax - ymin) * i) / ticks);

  return (
    <div className="chart-wrap" role="img" aria-label="Line chart">
      <svg className="chart-svg" viewBox={`0 0 ${w} ${h}`} preserveAspectRatio="xMidYMid meet">
        {yTicks.map((t) => (
          <g key={`yt-${t}`}>
            <line x1={pad.l} x2={w - pad.r} y1={sy(t)} y2={sy(t)} stroke="#252a2f" strokeWidth={1} />
            <text
              x={pad.l - 6}
              y={sy(t)}
              textAnchor="end"
              dominantBaseline="middle"
              fill="#5e666d"
              fontSize={10}
              fontFamily="DM Mono, ui-monospace, monospace"
            >
              {yFormat ? yFormat(t) : t.toFixed(3)}
            </text>
          </g>
        ))}
        {series.map((s, si) => {
          const pts = s.values.map((v, i) => `${sx(i)},${sy(v)}`).join(" ");
          const color = s.color ?? COLORS[si % COLORS.length];
          return (
            <polyline
              key={s.id}
              points={pts}
              fill="none"
              stroke={color}
              strokeWidth={1.5}
              strokeLinejoin="round"
              strokeLinecap="round"
            />
          );
        })}
        <line x1={pad.l} x2={w - pad.r} y1={h - pad.b} y2={h - pad.b} stroke="#252a2f" />
        <line x1={pad.l} x2={pad.l} y1={pad.t} y2={h - pad.b} stroke="#252a2f" />
      </svg>
      <div className="chart-legend">
        {series.map((s, si) => (
          <span key={s.id} className="chart-legend-item">
            <span className="chart-legend-swatch" style={{ background: s.color ?? COLORS[si % COLORS.length] }} />
            {s.label}
          </span>
        ))}
      </div>
    </div>
  );
}
