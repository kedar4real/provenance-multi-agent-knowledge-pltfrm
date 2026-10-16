/* Small SVG charts, no library. The rules they follow (see the dataviz notes in
   docs/decisions.md): thin bars with 4px rounded data-ends on a single baseline, a 2px surface
   gap between touching bars, hairline recessive grid, a legend whenever there are two or more
   series, text always in ink (never the series colour), a tooltip on every mark, and a table
   view of the same numbers. Series colours come from --series-1..4, validated for colour-blind
   separation in light and dark mode; charts cap at four series. */

import { Table2 } from "lucide-react";
import { useLayoutEffect, useRef, useState, type ReactNode } from "react";

import { cn } from "../lib/cn";

const SERIES = ["var(--series-1)", "var(--series-2)", "var(--series-3)", "var(--series-4)"];
export const MAX_SERIES = SERIES.length;

function useWidth<T extends HTMLElement>(): [React.RefObject<T | null>, number] {
  const ref = useRef<T>(null);
  const [width, setWidth] = useState(0);
  useLayoutEffect(() => {
    const el = ref.current;
    if (!el) return;
    const observer = new ResizeObserver(([entry]) => setWidth(entry?.contentRect.width ?? 0));
    observer.observe(el);
    setWidth(el.getBoundingClientRect().width);
    return () => observer.disconnect();
  }, []);
  return [ref, width];
}

/** Round axis ticks: 0 and 3-5 clean steps up to at least `max`. */
export function niceTicks(max: number, count = 4, integer = false): number[] {
  if (!(max > 0)) return [0, 1];
  const raw = integer ? Math.max(max / count, 1) : max / count;
  const magnitude = 10 ** Math.floor(Math.log10(raw));
  const steps = (integer && magnitude < 10 ? [1, 2, 5, 10] : [1, 2, 2.5, 5, 10]).map((m) => m * magnitude);
  const step = steps.find((s) => s >= raw && (!integer || Number.isInteger(s))) ?? Math.ceil(raw);
  const ticks: number[] = [];
  for (let v = 0; v < max + step * 0.999; v += step) ticks.push(Number(v.toPrecision(12)));
  return ticks;
}

/** A column with a 4px rounded data-end and a square foot on the baseline. */
function columnPath(x: number, y: number, w: number, h: number): string {
  if (h <= 0) return "";
  const r = Math.min(4, w / 2, h);
  return `M${x},${y + h}V${y + r}Q${x},${y} ${x + r},${y}H${x + w - r}Q${x + w},${y} ${x + w},${y + r}V${y + h}Z`;
}

/** A bar growing right from the baseline, rounded at its end. */
function barPath(x: number, y: number, w: number, h: number): string {
  if (w <= 0) return "";
  const r = Math.min(4, h / 2, w);
  return `M${x},${y}H${x + w - r}Q${x + w},${y} ${x + w},${y + r}V${y + h - r}Q${x + w},${y + h} ${x + w - r},${y + h}H${x}Z`;
}

interface Tip {
  x: number;
  y: number;
  content: ReactNode;
}

function Tooltip({ tip }: { tip: Tip | null }) {
  if (!tip) return null;
  return (
    <div
      role="tooltip"
      className="pointer-events-none absolute z-10 -translate-x-1/2 -translate-y-[calc(100%+10px)] rounded-lg border border-rule bg-sheet px-2.5 py-1.5 text-[12px] whitespace-nowrap text-ink shadow-lift"
      style={{ left: tip.x, top: tip.y }}
    >
      {tip.content}
    </div>
  );
}

export function Legend({ names, colors }: { names: string[]; colors?: string[] }) {
  if (names.length < 2) return null;
  return (
    <ul className="flex flex-wrap gap-x-4 gap-y-1 text-[12px] text-ink-2">
      {names.map((name, i) => (
        <li key={name} className="flex items-center gap-1.5">
          <span aria-hidden className="size-2.5 rounded-[3px]" style={{ background: colors?.[i] ?? SERIES[i] }} />
          {name}
        </li>
      ))}
    </ul>
  );
}

/** The same numbers as a table, behind a toggle: the accessible view of every chart. */
export function ChartFrame({
  title,
  subtitle,
  legend,
  legendColors,
  table,
  children,
  className,
}: {
  title: ReactNode;
  subtitle?: ReactNode;
  legend?: string[];
  /** Legend swatches when they aren't the series palette (status colours). */
  legendColors?: string[];
  table: { columns: string[]; rows: (string | number)[][] };
  children: ReactNode;
  className?: string;
}) {
  const [showTable, setShowTable] = useState(false);
  return (
    <figure className={cn("rounded-2xl border border-rule bg-sheet p-4 shadow-card", className)}>
      <figcaption className="mb-3 flex flex-wrap items-start justify-between gap-2">
        <div>
          <p className="text-sm font-medium text-ink">{title}</p>
          {subtitle && <p className="text-[12px] text-ink-3">{subtitle}</p>}
        </div>
        <button
          type="button"
          onClick={() => setShowTable((v) => !v)}
          aria-pressed={showTable}
          className="inline-flex items-center gap-1.5 rounded-md px-2 py-1 text-[12px] text-ink-3 hover:bg-inset hover:text-ink"
        >
          <Table2 aria-hidden className="size-3.5" />
          {showTable ? "Chart" : "Table"}
        </button>
      </figcaption>
      {legend && legend.length > 1 && (
        <div className="mb-2">
          <Legend names={legend} colors={legendColors} />
        </div>
      )}
      {showTable ? (
        <div className="max-h-72 overflow-auto rounded-lg border border-rule">
          <table className="greenbar w-full text-left text-[12px]">
            <thead className="smallcaps sticky top-0 bg-sheet text-ink-4">
              <tr>
                {table.columns.map((c) => (
                  <th key={c} scope="col" className="px-3 py-1.5 font-medium">
                    {c}
                  </th>
                ))}
              </tr>
            </thead>
            <tbody className="font-mono tabular-nums">
              {table.rows.map((r, i) => (
                <tr key={i}>
                  {r.map((v, j) => (
                    <td key={j} className="px-3 py-1">
                      {v}
                    </td>
                  ))}
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      ) : (
        children
      )}
    </figure>
  );
}

/** Grouped columns: one group per category, one column per series (at most four). */
export function ColumnChart({
  categories,
  series,
  format,
  height = 200,
  label,
  integer = false,
}: {
  categories: string[];
  series: { name: string; values: (number | null)[] }[];
  format: (v: number) => string;
  height?: number;
  label: string;
  /** Counts: whole-number ticks only. */
  integer?: boolean;
}) {
  const [ref, width] = useWidth<HTMLDivElement>();
  const [tip, setTip] = useState<Tip | null>(null);
  const shown = series.slice(0, MAX_SERIES);
  const max = Math.max(0, ...shown.flatMap((s) => s.values.map((v) => v ?? 0)));
  const min = Math.min(0, ...shown.flatMap((s) => s.values.map((v) => v ?? 0)));
  const ticks = niceTicks(max > 0 ? max : 1, 4, integer);
  const top = ticks.at(-1) ?? 1;
  const pad = { left: 56, right: 8, top: 18, bottom: 26 };
  const plotW = Math.max(width - pad.left - pad.right, 10);
  const plotH = height - pad.top - pad.bottom;
  const band = plotW / Math.max(categories.length, 1);
  const barW = Math.min(24, (band * 0.7 - 2 * (shown.length - 1)) / shown.length);
  const groupW = barW * shown.length + 2 * (shown.length - 1);
  const y = (v: number) => pad.top + plotH - (Math.max(v, 0) / top) * plotH;
  // Value labels on the caps only for a single series with few bars; side-by-side caps would
  // collide, so grouped values live in the tooltip and the table.
  const labelAll = shown.length === 1 && categories.length <= 8;

  return (
    <div ref={ref} className="relative" onMouseLeave={() => setTip(null)}>
      {width > 0 && (
        <svg width={width} height={height} role="img" aria-label={label} className="block overflow-visible">
          {ticks.map((t) => (
            <g key={t}>
              <line x1={pad.left} x2={width - pad.right} y1={y(t)} y2={y(t)} stroke="var(--chart-grid)" />
              <text x={pad.left - 8} y={y(t)} dy="0.32em" textAnchor="end" className="fill-ink-4 font-mono text-[10px]">
                {format(t)}
              </text>
            </g>
          ))}
          <line x1={pad.left} x2={width - pad.right} y1={y(0)} y2={y(0)} stroke="var(--chart-axis)" />
          {categories.map((cat, ci) => {
            const gx = pad.left + band * ci + (band - groupW) / 2;
            return (
              <g key={cat}>
                {shown.map((s, si) => {
                  const v = s.values[ci];
                  if (v === null || v === undefined) return null;
                  const x = gx + si * (barW + 2);
                  const h = y(0) - y(v);
                  return (
                    <g key={s.name}>
                      <path
                        d={columnPath(x, y(v), barW, h)}
                        fill={SERIES[si]}
                        className="origin-bottom animate-[grow-up_600ms_cubic-bezier(0.2,0.8,0.2,1)_both]"
                        style={{ transformBox: "fill-box", animationDelay: `${(ci * shown.length + si) * 40}ms` }}
                      />
                      {labelAll && (
                        <text x={x + barW / 2} y={y(v) - 5} textAnchor="middle" className="fill-ink-2 font-mono text-[10px]">
                          {format(v)}
                        </text>
                      )}
                      <rect
                        x={x - 3}
                        y={pad.top}
                        width={barW + 6}
                        height={plotH}
                        fill="transparent"
                        onMouseEnter={() =>
                          setTip({
                            x: x + barW / 2,
                            y: y(v),
                            content: (
                              <>
                                <span className="text-ink-3">
                                  {s.name !== label ? `${s.name} · ` : ""}
                                  {cat}
                                </span>{" "}
                                <span className="font-mono font-medium">{format(v)}</span>
                              </>
                            ),
                          })
                        }
                      />
                    </g>
                  );
                })}
                <text x={pad.left + band * ci + band / 2} y={height - 8} textAnchor="middle" className="fill-ink-3 text-[11px]">
                  {cat}
                </text>
              </g>
            );
          })}
          {min < 0 && (
            <text x={width - pad.right} y={pad.top - 6} textAnchor="end" className="fill-ink-4 text-[10px]">
              negative values shown in the table
            </text>
          )}
        </svg>
      )}
      <Tooltip tip={tip} />
    </div>
  );
}

/** A ranked list of horizontal bars, one series, value at the tip. */
export function BarList({
  rows,
  format,
  label,
}: {
  rows: { name: string; value: number; tone?: "ok" | "danger" | "warn" }[];
  format: (v: number) => string;
  label: string;
}) {
  const max = Math.max(1e-9, ...rows.map((r) => r.value));
  if (rows.length === 0) return <p className="py-6 text-center text-sm text-ink-4">Nothing yet</p>;
  return (
    <ul aria-label={label} className="space-y-2.5">
      {rows.map((r, i) => (
        <li key={r.name} className="grid grid-cols-[minmax(6rem,9rem)_1fr_auto] items-center gap-3 text-[13px]" title={`${r.name}: ${format(r.value)}`}>
          <span className="truncate text-ink-2">{r.name}</span>
          <span className="h-2.5 rounded-full bg-inset">
            <span
              className="block h-full origin-left animate-[grow_700ms_cubic-bezier(0.2,0.8,0.2,1)_both] rounded-full"
              style={{
                width: `${(r.value / max) * 100}%`,
                background:
                  r.tone === "danger" ? "var(--color-danger)" : r.tone === "warn" ? "var(--color-warn)" : "var(--series-1)",
                animationDelay: `${i * 60}ms`,
              }}
            />
          </span>
          <span className="font-mono text-[12px] text-ink tabular-nums">{format(r.value)}</span>
        </li>
      ))}
    </ul>
  );
}

/** When each step ran: one bar per step from its start to its end, on a shared time axis. */
export function Waterfall({
  steps,
  totalMs,
  labelOf,
  isProblem,
}: {
  steps: { step: string; at: number; ms: number }[];
  totalMs: number;
  labelOf: (step: string) => string;
  isProblem: (i: number) => boolean;
}) {
  const [ref, width] = useWidth<HTMLDivElement>();
  const [tip, setTip] = useState<Tip | null>(null);
  const rowH = 22;
  const pad = { left: 190, right: 56, top: 4, bottom: 22 };
  const plotW = Math.max(width - pad.left - pad.right, 10);
  const end = Math.max(totalMs, ...steps.map((s) => s.at), 1);
  const ticks = niceTicks(end / 1000, 4);
  const top = ticks.at(-1) ?? 1;
  const x = (ms: number) => pad.left + (ms / 1000 / top) * plotW;
  const height = pad.top + steps.length * rowH + pad.bottom;

  return (
    <div ref={ref} className="relative" onMouseLeave={() => setTip(null)}>
      {width > 0 && (
        <svg width={width} height={height} role="img" aria-label="When each step ran" className="block">
          {ticks.map((t) => (
            <g key={t}>
              <line x1={x(t * 1000)} x2={x(t * 1000)} y1={pad.top} y2={height - pad.bottom} stroke="var(--chart-grid)" />
              <text x={x(t * 1000)} y={height - 6} textAnchor="middle" className="fill-ink-4 font-mono text-[10px]">
                {t} s
              </text>
            </g>
          ))}
          {steps.map((s, i) => {
            const start = Math.max(s.at - s.ms, 0);
            const yy = pad.top + i * rowH + 5;
            const w = Math.max(x(s.at) - x(start), 2);
            return (
              <g key={i}>
                <text x={pad.left - 10} y={yy + 6} dy="0.32em" textAnchor="end" className="fill-ink-2 text-[11px]">
                  {labelOf(s.step)}
                </text>
                <path
                  d={barPath(x(start), yy, w, 12)}
                  fill={isProblem(i) ? "var(--color-danger)" : "var(--series-1)"}
                  className="origin-left animate-[grow_500ms_cubic-bezier(0.2,0.8,0.2,1)_both]"
                  style={{ transformBox: "fill-box", animationDelay: `${i * 50}ms` }}
                />
                <text x={x(start) + w + 6} y={yy + 6} dy="0.32em" className="fill-ink-3 font-mono text-[10px]">
                  {s.ms >= 1000 ? `${(s.ms / 1000).toFixed(1)} s` : `${Math.round(s.ms)} ms`}
                </text>
                <rect
                  x={pad.left}
                  y={yy - 5}
                  width={plotW}
                  height={rowH}
                  fill="transparent"
                  onMouseEnter={() =>
                    setTip({
                      x: x(start) + w / 2,
                      y: yy,
                      content: (
                        <>
                          <span className="text-ink-3">{labelOf(s.step)}</span>{" "}
                          <span className="font-mono">
                            {(start / 1000).toFixed(1)}–{(s.at / 1000).toFixed(1)} s
                          </span>
                        </>
                      ),
                    })
                  }
                />
              </g>
            );
          })}
        </svg>
      )}
      <Tooltip tip={tip} />
    </div>
  );
}

/** Calls per day, stacked by outcome (status colours, always with the legend's labels). */
export function StackedDays({
  days,
  outcomes,
  counts,
}: {
  days: string[];
  outcomes: { key: string; label: string; color: string }[];
  counts: Record<string, Record<string, number>>;
}) {
  const [ref, width] = useWidth<HTMLDivElement>();
  const [tip, setTip] = useState<Tip | null>(null);
  const height = 180;
  const pad = { left: 36, right: 8, top: 10, bottom: 24 };
  const totals = days.map((d) => outcomes.reduce((s, o) => s + (counts[d]?.[o.key] ?? 0), 0));
  const ticks = niceTicks(Math.max(1, ...totals), 4, true);
  const top = ticks.at(-1) ?? 1;
  const plotW = Math.max(width - pad.left - pad.right, 10);
  const plotH = height - pad.top - pad.bottom;
  const band = plotW / Math.max(days.length, 1);
  const barW = Math.min(24, band * 0.6);
  const scale = (v: number) => (v / top) * plotH;

  return (
    <div ref={ref} className="relative" onMouseLeave={() => setTip(null)}>
      {width > 0 && (
        <svg width={width} height={height} role="img" aria-label="Tool calls per day by outcome" className="block">
          {ticks.map((t) => (
            <g key={t}>
              <line x1={pad.left} x2={width - pad.right} y1={pad.top + plotH - scale(t)} y2={pad.top + plotH - scale(t)} stroke="var(--chart-grid)" />
              <text x={pad.left - 6} y={pad.top + plotH - scale(t)} dy="0.32em" textAnchor="end" className="fill-ink-4 font-mono text-[10px]">
                {t}
              </text>
            </g>
          ))}
          {days.map((d, di) => {
            const x = pad.left + band * di + (band - barW) / 2;
            let base = pad.top + plotH;
            const segments = outcomes
              .map((o) => ({ o, v: counts[d]?.[o.key] ?? 0 }))
              .filter((s) => s.v > 0);
            return (
              <g key={d}>
                {segments.map(({ o, v }, si) => {
                  const h = scale(v);
                  const last = si === segments.length - 1;
                  // 2px surface gap between stacked segments; only the top segment is rounded.
                  const yTop = base - h;
                  const node = last ? (
                    <path key={o.key} d={columnPath(x, yTop, barW, Math.max(h - (si ? 2 : 0), 0))} fill={o.color} />
                  ) : (
                    <rect key={o.key} x={x} y={yTop + (si ? 2 : 0)} width={barW} height={Math.max(h - (si ? 2 : 0), 0)} fill={o.color} />
                  );
                  base = yTop;
                  return node;
                })}
                <rect
                  x={x - 4}
                  y={pad.top}
                  width={barW + 8}
                  height={plotH}
                  fill="transparent"
                  onMouseEnter={() =>
                    setTip({
                      x: x + barW / 2,
                      y: pad.top + plotH - scale(totals[di] ?? 0),
                      content: (
                        <span className="grid gap-0.5">
                          <span className="text-ink-3">{d}</span>
                          {outcomes.map((o) => (
                            <span key={o.key} className="flex items-center gap-1.5">
                              <span className="size-2 rounded-sm" style={{ background: o.color }} />
                              {o.label} <span className="ml-auto pl-3 font-mono">{counts[d]?.[o.key] ?? 0}</span>
                            </span>
                          ))}
                        </span>
                      ),
                    })
                  }
                />
                {(days.length <= 8 || di % Math.ceil(days.length / 7) === 0) && (
                  <text x={x + barW / 2} y={height - 8} textAnchor="middle" className="fill-ink-4 font-mono text-[10px]">
                    {d.slice(5)}
                  </text>
                )}
              </g>
            );
          })}
        </svg>
      )}
      <Tooltip tip={tip} />
    </div>
  );
}

export function StatTile({
  label,
  value,
  note,
  icon,
  delay = 0,
}: {
  label: string;
  value: ReactNode;
  note?: ReactNode;
  icon: ReactNode;
  delay?: number;
}) {
  return (
    <div className="lift animate-rise rounded-2xl border border-rule bg-sheet p-4" style={{ animationDelay: `${delay}ms` }}>
      <p className="flex items-center gap-2 text-[13px] text-ink-3">
        <span aria-hidden className="icon-tile size-7 rounded-lg">
          {icon}
        </span>
        {label}
      </p>
      <p className="mt-3 text-[28px] leading-none font-semibold tracking-tight text-ink">{value}</p>
      {note && <p className="mt-1.5 text-[12px] text-ink-3">{note}</p>}
    </div>
  );
}

/** A filled share of a whole; the track is a lighter step of the same hue. */
export function Meter({ value, max, label, danger = 0.9 }: { value: number; max: number; label: string; danger?: number }) {
  const share = max > 0 ? Math.min(value / max, 1) : 0;
  return (
    <div
      role="meter"
      aria-label={label}
      aria-valuemin={0}
      aria-valuemax={max}
      aria-valuenow={value}
      className="h-2.5 overflow-hidden rounded-full"
      style={{ background: "color-mix(in oklch, var(--series-1) 18%, transparent)" }}
    >
      <div
        className="h-full origin-left animate-[grow_800ms_cubic-bezier(0.2,0.8,0.2,1)_both] rounded-full"
        style={{ width: `${share * 100}%`, background: share >= danger ? "var(--color-danger)" : "var(--series-1)" }}
      />
    </div>
  );
}
