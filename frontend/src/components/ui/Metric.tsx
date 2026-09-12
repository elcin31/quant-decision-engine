interface Props {
  label: string;
  value: number | null | undefined;
  format?: "raw" | "pct" | "number";
  signed?: boolean;
  digits?: number;
}

export function Metric({ label, value, format = "number", signed = false, digits = 2 }: Props) {
  let text = "—";
  let tone = "";

  if (value !== null && value !== undefined && Number.isFinite(value)) {
    if (format === "pct") {
      const pct = value * 100;
      const sign = signed && pct > 0 ? "+" : "";
      text = `${sign}${pct.toFixed(digits)}%`;
    } else if (format === "raw") {
      text = Number.isInteger(value) ? String(value) : value.toFixed(digits);
    } else {
      const sign = signed && value > 0 ? "+" : "";
      text = `${sign}${value.toFixed(digits)}`;
    }
    if (signed || format === "pct") {
      if (value < 0) tone = "negative";
      else if (value > 0 && signed) tone = "positive";
    }
  }

  return (
    <div className="metric">
      <div className="metric-label">{label}</div>
      <div className={`metric-value ${tone}`}>{text}</div>
    </div>
  );
}
