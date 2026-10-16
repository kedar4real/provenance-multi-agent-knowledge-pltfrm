import { Dialog } from "@base-ui/react/dialog";
import { Command, CornerDownLeft, Search, type LucideIcon } from "lucide-react";
import { useEffect, useMemo, useRef, useState } from "react";

import { cn } from "../lib/cn";

export interface PaletteAction {
  id: string;
  label: string;
  group: string;
  icon: LucideIcon;
  hint?: string;
  run: () => void;
}

/** Ctrl/Cmd+K: jump anywhere, switch identity, reopen history, or ask what you type. */
export function CommandPalette({
  open,
  onOpenChange,
  actions,
  onAsk,
}: {
  open: boolean;
  onOpenChange: (open: boolean) => void;
  actions: PaletteAction[];
  onAsk: (question: string) => void;
}) {
  const [query, setQuery] = useState("");
  const [active, setActive] = useState(0);
  const listRef = useRef<HTMLUListElement>(null);

  useEffect(() => {
    if (open) {
      setQuery("");
      setActive(0);
    }
  }, [open]);

  const shown = useMemo(() => {
    const q = query.trim().toLowerCase();
    const matches = q ? actions.filter((a) => `${a.label} ${a.group}`.toLowerCase().includes(q)) : actions;
    const ask: PaletteAction[] = q.length > 3
      ? [{ id: "ask", label: `Ask: “${query.trim()}”`, group: "Question", icon: CornerDownLeft, run: () => onAsk(query.trim()) }]
      : [];
    return [...matches, ...ask];
  }, [actions, query, onAsk]);

  useEffect(() => {
    listRef.current?.querySelector<HTMLElement>(`[data-index="${active}"]`)?.scrollIntoView({ block: "nearest" });
  }, [active]);

  const choose = (action: PaletteAction | undefined) => {
    if (!action) return;
    onOpenChange(false);
    action.run();
  };

  let lastGroup = "";
  return (
    <Dialog.Root open={open} onOpenChange={onOpenChange}>
      <Dialog.Portal>
        <Dialog.Backdrop className="fixed inset-0 z-40 bg-ink/25 backdrop-blur-[2px] transition-opacity duration-150 data-ending-style:opacity-0 data-starting-style:opacity-0" />
        <Dialog.Popup className="glass fixed top-[14vh] left-1/2 z-50 w-[min(36rem,92vw)] -translate-x-1/2 overflow-hidden rounded-2xl border border-rule shadow-lift transition-[opacity,transform] duration-150 data-ending-style:scale-95 data-ending-style:opacity-0 data-starting-style:scale-95 data-starting-style:opacity-0">
          <Dialog.Title className="sr-only">Command palette</Dialog.Title>
          <div className="flex items-center gap-3 border-b border-rule px-4">
            <Search aria-hidden className="size-4 text-ink-4" />
            <input
              autoFocus
              value={query}
              onChange={(e) => {
                setQuery(e.target.value);
                setActive(0);
              }}
              onKeyDown={(e) => {
                if (e.key === "ArrowDown") {
                  e.preventDefault();
                  setActive((i) => Math.min(i + 1, shown.length - 1));
                } else if (e.key === "ArrowUp") {
                  e.preventDefault();
                  setActive((i) => Math.max(i - 1, 0));
                } else if (e.key === "Enter") {
                  e.preventDefault();
                  choose(shown[active]);
                }
              }}
              placeholder="Type a command, or a question to ask…"
              aria-label="Command or question"
              aria-controls="palette-list"
              aria-activedescendant={shown[active] ? `palette-${shown[active].id}` : undefined}
              className="h-12 min-w-0 flex-1 bg-transparent text-[15px] placeholder:text-ink-4 focus:outline-none"
            />
            <kbd className="rounded border border-rule px-1.5 font-mono text-[11px] text-ink-4">Esc</kbd>
          </div>
          <ul id="palette-list" role="listbox" ref={listRef} className="max-h-80 overflow-y-auto p-1.5">
            {shown.map((action, i) => {
              const header = action.group !== lastGroup ? action.group : null;
              lastGroup = action.group;
              const Icon = action.icon;
              return (
                <li key={action.id} role="presentation">
                  {header && <p className="px-2.5 pt-2 pb-1 text-[11px] font-medium text-ink-4">{header}</p>}
                  <div
                    id={`palette-${action.id}`}
                    role="option"
                    aria-selected={i === active}
                    data-index={i}
                    onMouseMove={() => setActive(i)}
                    onClick={() => choose(action)}
                    className={cn(
                      "flex cursor-pointer items-center gap-3 rounded-lg px-2.5 py-2 text-sm",
                      i === active ? "bg-ink text-paper" : "text-ink-2",
                    )}
                  >
                    <Icon aria-hidden className="size-4 shrink-0 opacity-80" />
                    <span className="min-w-0 flex-1 truncate">{action.label}</span>
                    {action.hint && <span className={cn("font-mono text-[11px]", i === active ? "text-paper/70" : "text-ink-4")}>{action.hint}</span>}
                  </div>
                </li>
              );
            })}
            {shown.length === 0 && <li className="px-3 py-6 text-center text-sm text-ink-4">No matches</li>}
          </ul>
          <footer className="flex items-center gap-3 border-t border-rule px-4 py-2 text-[11px] text-ink-4">
            <Command aria-hidden className="size-3.5" />
            <span>↑↓ to move · Enter to run</span>
          </footer>
        </Dialog.Popup>
      </Dialog.Portal>
    </Dialog.Root>
  );
}
