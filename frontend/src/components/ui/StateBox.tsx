interface Props {
  children: React.ReactNode;
  variant?: "loading" | "error" | "empty";
}

export function StateBox({ children, variant = "empty" }: Props) {
  return <div className={`state-box ${variant}`}>{children}</div>;
}
