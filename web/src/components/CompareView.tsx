import { Select } from "@base-ui/react/select";
import { ArrowLeftRight, Check, ChevronsUpDown, Columns2, LoaderCircle, Send, ShieldCheck } from "lucide-react";
import { useEffect, useState, type FormEvent } from "react";

import { api, type Me } from "../lib/api";
import { useIdentities, type Identity } from "../lib/identities";
import { useAgentRun, type RunState } from "../lib/useAgentRun";
import { AnswerView } from "./Answer";
import { StepTimeline } from "./Steps";
import { Button } from "./ui";

const EXAMPLE = "How does Nvidia describe its dependence on TSMC?";

/** One question, asked as two people at once. The answers differ only because the database
 *  shows each of them different rows: the clearest way to see row-level security work. */
export function CompareView({
  identity,
  onOpenSource,
}: {
  identity: Identity;
  onOpenSource: (chunkId: number, apiKey?: string) => void;
}) {
  const { all } = useIdentities();
  const others = all.filter((i) => i.name !== identity.name);
  const [rightName, setRightName] = useState(others[0]?.name ?? "");
  const right = all.find((i) => i.name === rightName) ?? null;
  const [question, setQuestion] = useState(EXAMPLE);
  const left = useAgentRun(identity.key);
  const rightRun = useAgentRun(right?.key ?? "");
  const running = left.run.status === "running" || rightRun.run.status === "running";

  useEffect(() => {
    if (!all.some((i) => i.name === rightName)) setRightName(others[0]?.name ?? "");
  }, [all, others, rightName]);

  function submit(event: FormEvent) {
    event.preventDefault();
    if (!question.trim() || !right) return;
    void left.ask(question);
    void rightRun.ask(question);
  }

  if (others.length === 0) {
    return (
      <div className="animate-rise rounded-2xl border border-dashed border-rule-strong bg-sheet/70 p-8 text-center">
        <Columns2 aria-hidden className="mx-auto size-8 text-ink-4" />
        <p className="mt-3 font-display text-2xl">Add a second identity to compare</p>
        <p className="mx-auto mt-1 max-w-md text-sm text-ink-3">
          Compare asks one question as two people at once, so you can see what each is allowed to read. Add another
          identity from the user menu (for example a healthcare analyst next to a tech analyst).
        </p>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      <form onSubmit={submit} className="space-y-3">
        <div className="flex flex-wrap items-center gap-2 text-sm">
          <span className="inline-flex items-center gap-2 rounded-full border border-rule bg-sheet px-3 py-1.5 shadow-card">
            <span className="size-2 rounded-full" style={{ background: "var(--series-1)" }} />
            {identity.displayName}
          </span>
          <ArrowLeftRight aria-hidden className="size-4 text-ink-4" />
          <Select.Root value={rightName} onValueChange={(v) => setRightName(String(v))}>
            <Select.Trigger className="inline-flex items-center gap-2 rounded-full border border-rule bg-sheet px-3 py-1.5 shadow-card hover:border-rule-strong">
              <span className="size-2 rounded-full" style={{ background: "var(--series-2)" }} />
              <Select.Value>{(v: string) => all.find((i) => i.name === v)?.displayName ?? "Choose"}</Select.Value>
              <ChevronsUpDown aria-hidden className="size-3.5 text-ink-4" />
            </Select.Trigger>
            <Select.Portal>
              <Select.Positioner sideOffset={6} className="z-30">
                <Select.Popup className="glass rounded-xl border border-rule p-1 shadow-lift">
                  {others.map((o) => (
                    <Select.Item key={o.name} value={o.name} className="flex cursor-default items-center gap-2 rounded-md px-2.5 py-2 text-sm outline-none select-none data-highlighted:bg-inset">
                      <span className="grid size-4 place-items-center">
                        <Select.ItemIndicator>
                          <Check aria-hidden className="size-3.5" />
                        </Select.ItemIndicator>
                      </span>
                      <Select.ItemText>{o.displayName}</Select.ItemText>
                    </Select.Item>
                  ))}
                </Select.Popup>
              </Select.Positioner>
            </Select.Portal>
          </Select.Root>
        </div>
        <div className="flex items-center gap-3 rounded-2xl border border-rule bg-sheet p-2 pl-4 shadow-card focus-within:border-pencil/50 focus-within:shadow-glow">
          <label htmlFor="compare-question" className="sr-only">
            Question to ask both
          </label>
          <input
            id="compare-question"
            value={question}
            onChange={(e) => setQuestion(e.target.value)}
            maxLength={1000}
            className="h-10 min-w-0 flex-1 bg-transparent font-serif text-[17px] focus:outline-none"
          />
          <Button type="submit" disabled={running || !question.trim() || !right} className="h-10 rounded-xl px-4">
            {running ? <LoaderCircle aria-hidden className="size-4 animate-spin" /> : <Send aria-hidden className="size-4" />}
            Ask both
          </Button>
        </div>
        <p className="text-[12px] text-ink-4">Asks twice, so it uses twice the free-tier quota.</p>
      </form>

      <div className="grid gap-5 lg:grid-cols-2">
        <Column identity={identity} run={left.run} dot="var(--series-1)" onOpenSource={onOpenSource} />
        {right && <Column identity={right} run={rightRun.run} dot="var(--series-2)" onOpenSource={onOpenSource} />}
      </div>
    </div>
  );
}

function Column({
  identity,
  run,
  dot,
  onOpenSource,
}: {
  identity: Identity;
  run: RunState;
  dot: string;
  onOpenSource: (chunkId: number, apiKey?: string) => void;
}) {
  const [me, setMe] = useState<Me | null>(null);
  useEffect(() => {
    const controller = new AbortController();
    api.me(identity.key, controller.signal).then(setMe, () => undefined);
    return () => controller.abort();
  }, [identity.key]);

  return (
    <section aria-label={`Answer for ${identity.displayName}`} className="min-w-0 space-y-4 rounded-2xl border border-rule bg-paper/40 p-4">
      <header className="flex items-center justify-between gap-3">
        <p className="flex items-center gap-2 font-medium">
          <span className="size-2.5 rounded-full" style={{ background: dot }} />
          {identity.displayName}
        </p>
        {me && (
          <span className="inline-flex items-center gap-1.5 text-[12px] text-ink-3">
            <ShieldCheck aria-hidden className="size-3.5" />
            {me.visible.tickers.length} companies · {me.visible.documents} filings
          </span>
        )}
      </header>
      {run.status === "idle" && <p className="py-10 text-center text-sm text-ink-4">Waiting for a question</p>}
      {run.status !== "idle" && (
        <StepTimeline
          steps={run.steps}
          running={run.status === "running"}
          startedAt={run.status === "running" ? run.startedAt : null}
          elapsedMs={run.status === "done" ? run.elapsedMs : null}
        />
      )}
      {run.status === "error" && <p className="text-sm text-danger">{run.message}</p>}
      {run.status === "done" && (
        <AnswerView
          result={run.result}
          elapsedMs={run.elapsedMs}
          identity={identity}
          onOpenSource={(id) => onOpenSource(id, identity.key)}
          compact
        />
      )}
    </section>
  );
}
