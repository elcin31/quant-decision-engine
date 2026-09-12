"use client";

interface PathChartProps {
  paths: number[][];
  initialValue?: number;
  maxPaths?: number;
  height?: number;
}

export function PathChart({ paths, initialValue, maxPaths = 40, height = 240 }: PathChartProps) {
  if (!paths.length) return <div className="state-box">No path data</div>;
  const shown = paths.slice(0, maxPaths);
  const withInit = shown.map((p) => (initialValue !== undefined ? [initialValue, ...p] : p));
  const all = withInit.flat();
  let ymin = Math.min(...all);
  let ymax = Math.max(...all);
  if (ymin === ymax) {
    ymin -= 1;
    ymax += 1;
  }
  const pad = { t: 12, r: 12, b: 20, l: 48 };
  const w = 640;
  const h = height;
  const iw = w - pad.l - pad.r;
  const ih = h - pad.t - pad.b;
  const n = withInit[0]!.length;
  const sx = (i: number) => pad.l + (i / Math.max(n - 1, 1)) * iw;
  const sy = (v: number) => pad.t + ((ymax - v) / (ymax - ymin)) * ih;

  return (
    <div className="chart-wrap" role="img" aria-label="Monte Carlo paths">
      <svg className="chart-svg" viewBox={`0 0 ${w} ${h}`} preserveAspectRatio="xMidYMid meet">
        {withInit.map((path, pi) => {
          const pts = path.map((v, i) => `${sx(i)},${sy(v)}`).join(" ");
          return (
            <polyline
              key={pi}
              points={pts}
              fill="none"
              stroke="#d7ff4f"
              strokeWidth={1}
              opacity={0.22}
            />
          );
        })}
        {initialValue !== undefined && (
          <line
            x1={pad.l}
            x2={w - pad.r}
            y1={sy(initialValue)}
            y2={sy(initialValue)}
            stroke="#e9c56d"
            strokeWidth={1}
            strokeDasharray="4 3"
          />
        )}
        <text
          x={pad.l - 6}
          y={sy(ymax)}
          textAnchor="end"
          fill="#5e666d"
          fontSize={10}
          fontFamily="DM Mono, ui-monospace, monospace"
        >
          {ymax.toFixed(1)}
        </text>
        <text
          x={pad.l - 6}
          y={sy(ymin)}
          textAnchor="end"
          fill="#5e666d"
          fontSize={10}
          fontFamily="DM Mono, ui-monospace, monospace"
        >
          {ymin.toFixed(1)}
        </text>
      </svg>
      <p className="text-sm text-dim" style={{ marginTop: 8, textAlign: "center", fontFamily: "var(--mono)" }}>
        Showing {shown.length} of {paths.length} paths
        {initialValue !== undefined ? " · dashed = initial value" : ""}
      </p>
    </div>
  );
}
