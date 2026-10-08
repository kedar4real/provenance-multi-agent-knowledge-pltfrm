import { CircleAlert, History, LoaderCircle, PenLine, Send, Sparkles } from "lucide-react";
import { Fragment, useEffect, useRef, useState, type FormEvent } from "react";

import { history, useHistory } from "../lib/history";
import type { Identity } from "../lib/identities";
import { useAgentRun } from "../lib/useAgentRun";
import { AnswerView } from "./Answer";
import { ExampleList } from "./ExampleList";
import { HistoryDrawer } from "./HistoryDrawer";
import { StepTimeline } from "./Steps";
import { Button } from "./ui";

const EXAMPLES = [
  "How did JPMorgan's net interest income change in fiscal 2025, and what drove it?",
  "Compare Apple's and Microsoft's R&D spending in fiscal 2025.",
  "What risks does Nvidia describe about export controls?",
];

export const QUESTION_INPUT_ID = "ask-question";

interface Props {
  identity: Identity;
  onOpenSource: (chunkId: number) => void;
  /** A question handed over from elsewhere (a passage, the command palette); asked once. */
  pending: { question: string; ask: boolean; nonce: number } | null;
  onPendingTaken: () => void;
  historyOpen: boolean;
  onHistoryOpenChange: (open: boolean) => void;
}

export function AskView({ identity, onOpenSource, pending, onPendingTaken, historyOpen, onHistoryOpenChange }: Props) {
  const [question, setQuestion] = useState("");
  const { run, ask, show } = useAgentRun(identity.key, (q, result, elapsedMs) =>
    history.add(identity.name, q, result, elapsedMs),
  );
  const past = useHistory(identity.name);
  const inputRef = useRef<HTMLTextAreaElement>(null);

  useEffect(() => {
    if (!pending) return;
    setQuestion(pending.question);
    if (pending.ask) void ask(pending.question);
    else inputRef.current?.focus();
    onPendingTaken();
  }, [pending, ask, onPendingTaken]);

  function submit(event: FormEvent) {
    event.preventDefault();
    void ask(question);
  }

  return (
    <div className="space-y-6">
      <form onSubmit={submit} className="space-y-2">
        <label htmlFor={QUESTION_INPUT_ID} className="sr-only">
          Ask a question
        </label>
        <div className="flex items-end gap-3 rounded-2xl border border-rule bg-sheet p-2 pl-3 shadow-card transition-[box-shadow,border-color] duration-200 focus-within:border-pencil/50 focus-within:shadow-glow">
          <span aria-hidden className="icon-tile mb-0.5 size-9 rounded-xl">
            <Sparkles className="size-4" />
          </span>
          <textarea
            id={QUESTION_INPUT_ID}
            ref={inputRef}
            rows={1}
            value={question}
            onChange={(e) => setQuestion(e.target.value)}
            onKeyDown={(e) => {
              if (e.key === "Enter" && !e.shiftKey) {
                e.preventDefault();
                void ask(question);
              }
            }}
            placeholder="Ask a question. The agent reads filings, queries the numbers, and checks its answer."
            maxLength={1000}
            className="field-sizing-content max-h-40 min-h-9 min-w-0 flex-1 resize-none bg-transparent py-1.5 font-serif text-[17px] placeholder:text-ink-4 focus:outline-none"
          />
          <Button
            type="submit"
            disabled={run.status === "running" || !question.trim()}
            aria-busy={run.status === "running"}
            className="h-10 rounded-xl px-4"
          >
            {run.status === "running" ? (
              <LoaderCircle aria-hidden className="size-4 animate-spin" />
            ) : (
              <Send aria-hidden className="size-4" />
            )}
            {run.status === "running" ? "Working" : "Ask"}
          </Button>
        </div>
        <div className="flex items-center justify-between gap-3 px-1 text-[12px] text-ink-4">
          <span className="hidden sm:inline">
            <Kbd>Enter</Kbd> to ask · <Kbd>/</Kbd> to focus · <Kbd>Ctrl K</Kbd> for commands
          </span>
          <button
            type="button"
            onClick={() => onHistoryOpenChange(true)}
            className="ml-auto inline-flex items-center gap-1.5 rounded-md px-2 py-1 text-ink-3 hover:bg-inset hover:text-ink"
          >
            <History aria-hidden className="size-3.5" />
            History{past.length > 0 && <span className="font-mono tabular-nums">· {past.length}</span>}
          </button>
        </div>
      </form>

      {run.status === "idle" && (
        <ExampleList
          examples={EXAMPLES}
          onPick={(q) => {
            setQuestion(q);
            void ask(q);
          }}
        />
      )}

      {run.status !== "idle" && (
        <StepTimeline
          steps={run.steps}
          running={run.status === "running"}
          startedAt={run.status === "running" ? run.startedAt : null}
          elapsedMs={run.status === "done" ? run.elapsedMs : null}
        />
      )}

      {run.status === "running" && run.draft && <DraftAnswer text={run.draft} revising={run.steps.some((s) => s.step === "verify" && s.detail.ok === false)} />}

      {run.status === "error" && (
        <p
          role="alert"
          className="flex animate-rise items-start gap-3 rounded-xl border border-danger/30 bg-sheet px-4 py-3 text-sm text-danger shadow-card"
        >
          <CircleAlert aria-hidden className="mt-0.5 size-4 shrink-0" />
          {run.message}
        </p>
      )}

      {run.status === "done" && (
        <AnswerView
          key={run.question + run.elapsedMs}
          result={run.result}
          elapsedMs={run.elapsedMs}
          identity={identity}
          onOpenSource={onOpenSource}
          steps={run.steps}
        />
      )}

      <HistoryDrawer
        open={historyOpen}
        onOpenChange={onHistoryOpenChange}
        items={past}
        identity={identity}
        onPick={(item) => {
          setQuestion(item.question);
          show(item.question, item.result, item.elapsedMs);
          onHistoryOpenChange(false);
        }}
      />
    </div>
  );
}

function Kbd({ children }: { children: string }) {
  return (
    <kbd className="rounded border border-rule bg-sheet px-1 py-px font-mono text-[11px] text-ink-3 shadow-[0_1px_0_var(--color-rule)]">
      {children}
    </kbd>
  );
}

const CITATION = /(\[(?:[PF]\d+)(?:\s*,\s*[PF]\d+)*\])/g;

/** The answer as the model writes it. Unverified until the result arrives: numbers are
 *  checked against the evidence only once the text is complete. */
function DraftAnswer({ text, revising }: { text: string; revising: boolean }) {
  return (
    <section aria-label="Answer being written" aria-live="off" className="animate-rise rounded-2xl border border-dashed border-rule-strong bg-sheet/70 p-5">
      <p className="mb-3 flex items-center gap-2 text-[13px] text-ink-3">
        <PenLine aria-hidden className="size-4 text-pencil" />
        {revising ? "Revising the draft" : "Writing"}
        <span className="rounded-full bg-inset px-2 py-0.5 text-[11px] text-ink-3">unverified draft</span>
      </p>
      <p className="font-serif text-[18px] leading-[1.7] whitespace-pre-line text-ink-2">
        {text.split(CITATION).map((part, i) =>
          i % 2 ? (
            <span key={i} className="mx-0.5 rounded bg-inset px-1 font-mono text-[11px] text-ink-3">
              {part.slice(1, -1)}
            </span>
          ) : (
            <Fragment key={i}>{part}</Fragment>
          ),
        )}
        <span aria-hidden className="ml-0.5 inline-block h-[1.1em] w-[2px] translate-y-[0.2em] animate-pulse bg-pencil" />
      </p>
    </section>
  );
}
