import { Dialog } from "@base-ui/react/dialog";
import { BadgeCheck, CircleAlert, History, MessageSquareText, SearchX, ShieldAlert, Trash2, X, Zap } from "lucide-react";

import { history, type HistoryItem } from "../lib/history";
import type { Identity } from "../lib/identities";
import { formatMs } from "../lib/steps";

function ago(ts: number): string {
  const s = (Date.now() - ts) / 1000;
  if (s < 60) return "just now";
  if (s < 3600) return `${Math.floor(s / 60)} min ago`;
  if (s < 86400) return `${Math.floor(s / 3600)} h ago`;
  return new Date(ts).toLocaleDateString();
}

function Outcome({ item }: { item: HistoryItem }) {
  const r = item.result;
  if (r.control?.abstained) return <ShieldAlert aria-label="withheld" className="size-4 text-pencil" />;
  if (r.declined) return <SearchX aria-label="no answer" className="size-4 text-ink-4" />;
  if (r.control?.cache?.hit) return <Zap aria-label="from cache" className="size-4 text-ok" />;
  if (r.verification?.ok) return <BadgeCheck aria-label="verified" className="size-4 text-ok" />;
  return <CircleAlert aria-label="unverified" className="size-4 text-danger" />;
}

/** Past questions for this identity, newest first; opening one shows the stored answer
 *  without asking again (no quota spent). Kept in this browser only. */
export function HistoryDrawer({
  open,
  onOpenChange,
  items,
  identity,
  onPick,
}: {
  open: boolean;
  onOpenChange: (open: boolean) => void;
  items: HistoryItem[];
  identity: Identity;
  onPick: (item: HistoryItem) => void;
}) {
  return (
    <Dialog.Root open={open} onOpenChange={onOpenChange}>
      <Dialog.Portal>
        <Dialog.Backdrop className="fixed inset-0 z-40 bg-ink/25 backdrop-blur-[2px] transition-opacity duration-200 data-ending-style:opacity-0 data-starting-style:opacity-0" />
        <Dialog.Popup className="fixed inset-y-0 left-0 z-50 flex w-[min(26rem,92vw)] flex-col border-r border-rule bg-sheet shadow-lift transition-transform duration-300 ease-[cubic-bezier(0.2,0.8,0.2,1)] data-ending-style:-translate-x-full data-starting-style:-translate-x-full">
          <header className="flex items-center gap-3 border-b border-rule px-5 py-4">
            <span aria-hidden className="icon-tile size-9 rounded-xl">
              <History className="size-4" />
            </span>
            <div className="min-w-0 flex-1">
              <Dialog.Title className="font-display text-xl">History</Dialog.Title>
              <Dialog.Description className="text-[12px] text-ink-3">
                {identity.displayName}'s questions, kept in this browser
              </Dialog.Description>
            </div>
            <Dialog.Close aria-label="Close history" className="grid size-8 place-items-center rounded-full text-ink-3 hover:bg-inset hover:text-ink">
              <X aria-hidden className="size-4" />
            </Dialog.Close>
          </header>
          {items.length === 0 ? (
            <div className="grid flex-1 place-items-center px-8 text-center">
              <div>
                <MessageSquareText aria-hidden className="mx-auto size-8 text-ink-4" />
                <p className="mt-3 text-sm text-ink-3">Answers you get will appear here, so you can reopen them without asking again.</p>
              </div>
            </div>
          ) : (
            <ol className="flex-1 space-y-1 overflow-y-auto p-2">
              {items.map((item, i) => (
                <li key={item.id} className="group animate-rise relative" style={{ animationDelay: `${Math.min(i, 10) * 30}ms` }}>
                  <button
                    type="button"
                    onClick={() => onPick(item)}
                    className="grid w-full grid-cols-[1.25rem_1fr] gap-3 rounded-xl px-3 py-2.5 pr-10 text-left transition-colors hover:bg-inset"
                  >
                    <span className="pt-0.5">
                      <Outcome item={item} />
                    </span>
                    <span className="min-w-0">
                      <span className="line-clamp-2 font-serif text-[15px] text-ink">{item.question}</span>
                      <span className="mt-0.5 block font-mono text-[11px] text-ink-4">
                        {ago(item.askedAt)} · {formatMs(item.elapsedMs)}
                        {item.result.confidence !== null && ` · ${Math.round(item.result.confidence * 100)}%`}
                      </span>
                    </span>
                  </button>
                  <button
                    type="button"
                    onClick={() => history.remove(item.id)}
                    aria-label="Remove from history"
                    className="absolute top-2.5 right-2 grid size-7 place-items-center rounded-md text-ink-4 opacity-0 transition-opacity group-hover:opacity-100 hover:bg-sheet hover:text-danger focus-visible:opacity-100"
                  >
                    <Trash2 aria-hidden className="size-3.5" />
                  </button>
                </li>
              ))}
            </ol>
          )}
          {items.length > 0 && (
            <footer className="border-t border-rule px-5 py-3">
              <button type="button" onClick={() => history.clear(identity.name)} className="text-[12px] text-ink-3 hover:text-danger">
                Clear {identity.displayName.split(" ")[0]}'s history
              </button>
            </footer>
          )}
        </Dialog.Popup>
      </Dialog.Portal>
    </Dialog.Root>
  );
}
