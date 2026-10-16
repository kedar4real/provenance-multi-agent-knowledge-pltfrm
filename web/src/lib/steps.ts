import {
  ArrowUpRight,
  DatabaseZap,
  FileSearch,
  Gauge,
  ListChecks,
  PenLine,
  RefreshCcw,
  Route,
  ShieldAlert,
  ShieldCheck,
  Table2,
  type LucideIcon,
} from "lucide-react";

/** Names for the steps the controller and agent stream back, shared by the timeline and the
 *  trace panel. */
export const STEP_LABELS: Record<string, string> = {
  route: "Choose a model",
  cache: "Check earlier answers",
  plan: "Plan",
  search: "Read filings",
  sql: "Query financial data",
  write: "Write answer",
  revise: "Revise answer",
  verify: "Verify numbers and citations",
  score: "Score each claim",
  escalate: "Escalate to the large model",
  abstain: "Withhold the answer",
};

export function formatMs(ms: number): string {
  return ms >= 1000 ? `${(ms / 1000).toFixed(1)} s` : `${Math.round(ms)} ms`;
}

/** One icon per step, used by the live timeline. */
export const STEP_ICONS: Record<string, LucideIcon> = {
  route: Route,
  cache: DatabaseZap,
  plan: ListChecks,
  search: FileSearch,
  sql: Table2,
  write: PenLine,
  revise: RefreshCcw,
  verify: ShieldCheck,
  score: Gauge,
  escalate: ArrowUpRight,
  abstain: ShieldAlert,
};
