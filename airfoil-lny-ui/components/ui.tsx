export function Button({
  children,
  href,
  onClick,
  disabled,
  variant = "primary",
  download,
}: {
  children: React.ReactNode;
  href?: string;
  onClick?: () => void;
  disabled?: boolean;
  variant?: "primary" | "ghost";
  download?: boolean;
}) {
  const base =
    "inline-flex items-center justify-center rounded-2xl px-4 py-2 text-sm font-semibold transition shadow-sm";
  const styles =
    variant === "primary"
      ? "bg-lny-yellow text-black hover:brightness-110 active:brightness-95 disabled:opacity-60"
      : "bg-white/5 text-white hover:bg-white/10 border border-white/10 disabled:opacity-60";
  if (href) {
    return (
      <a className={`${base} ${styles}`} href={href} download={download}>
        {children}
      </a>
    );
  }
  return (
    <button className={`${base} ${styles}`} onClick={onClick} disabled={disabled}>
      {children}
    </button>
  );
}

export function Card({
  title,
  subtitle,
  children,
}: {
  title: string;
  subtitle?: string;
  children: React.ReactNode;
}) {
  return (
    <div className="rounded-3xl border border-white/10 bg-white/[0.04] p-5 shadow-[0_0_0_1px_rgba(244,196,1,0.06)]">
      <div className="mb-4">
        <div className="text-lg font-semibold">{title}</div>
        {subtitle ? <div className="text-sm text-white/60">{subtitle}</div> : null}
      </div>
      {children}
    </div>
  );
}
