import { Menu } from "@base-ui/react/menu";
import { Check, ChevronsUpDown, Plus, UserRound } from "lucide-react";
import { useState } from "react";

import { identities, useIdentities } from "../lib/identities";
import { AddIdentityDialog } from "./AddIdentityDialog";

const itemClass =
  "flex cursor-default items-center gap-2 rounded-md px-2.5 py-2 text-sm outline-none select-none data-highlighted:bg-inset";

export function IdentityMenu() {
  const { all, active } = useIdentities();
  const [adding, setAdding] = useState(false);

  return (
    <>
      <Menu.Root>
        <Menu.Trigger className="flex h-9 items-center gap-2 rounded-full border border-rule bg-sheet pr-2.5 pl-1 text-sm shadow-card transition-[border-color,box-shadow] hover:border-rule-strong hover:shadow-lift data-popup-open:border-rule-strong">
          <span aria-hidden className="grid size-7 place-items-center rounded-full bg-mark text-mark-ink">
            {active ? (
              <span className="font-mono text-[11px] font-medium">{initials(active.displayName)}</span>
            ) : (
              <UserRound className="size-3.5" />
            )}
          </span>
          <span className="max-w-48 truncate">{active ? active.displayName : "No identity"}</span>
          <ChevronsUpDown aria-hidden className="size-3.5 text-ink-4" />
        </Menu.Trigger>
        <Menu.Portal>
          <Menu.Positioner sideOffset={6} align="end" className="z-30">
            <Menu.Popup className="glass w-72 origin-(--transform-origin) rounded-xl border border-rule p-1 shadow-lift transition-[opacity,transform] duration-150 ease-out data-ending-style:scale-95 data-ending-style:opacity-0 data-starting-style:scale-95 data-starting-style:opacity-0">
              {all.length > 0 && (
                <Menu.RadioGroup value={active?.name ?? ""} onValueChange={(v: string) => identities.activate(v)}>
                  <Menu.GroupLabel className="px-2.5 pt-1.5 pb-1 text-xs font-medium text-ink-3">
                    Search as
                  </Menu.GroupLabel>
                  {all.map((identity) => (
                    <Menu.RadioItem key={identity.name} value={identity.name} closeOnClick className={itemClass}>
                      <span className="grid size-4 place-items-center">
                        <Menu.RadioItemIndicator>
                          <Check aria-hidden className="size-3.5" />
                        </Menu.RadioItemIndicator>
                      </span>
                      <span className="min-w-0 flex-1">
                        <span className="block truncate">{identity.displayName}</span>
                        <span className="block truncate font-mono text-[12px] text-ink-3">
                          {identity.groups.join(" · ")}
                        </span>
                      </span>
                    </Menu.RadioItem>
                  ))}
                </Menu.RadioGroup>
              )}
              {all.length > 0 && <Menu.Separator className="mx-1 my-1 h-px bg-rule" />}
              <Menu.Item className={itemClass} onClick={() => setAdding(true)}>
                <Plus aria-hidden className="size-4 text-ink-3" />
                Add identity…
              </Menu.Item>
            </Menu.Popup>
          </Menu.Positioner>
        </Menu.Portal>
      </Menu.Root>
      <AddIdentityDialog open={adding} onOpenChange={setAdding} />
    </>
  );
}

export function AddIdentityButton({ className }: { className?: string }) {
  const [open, setOpen] = useState(false);
  return (
    <>
      <button
        type="button"
        onClick={() => setOpen(true)}
        className={
          className ??
          "inline-flex h-10 items-center gap-2 rounded-xl bg-ink px-4 text-sm font-medium text-paper shadow-card transition-[transform,box-shadow,background-color] hover:-translate-y-px hover:bg-ink-2 hover:shadow-lift"
        }
      >
        <Plus aria-hidden className="size-4" />
        Add an identity
      </button>
      <AddIdentityDialog open={open} onOpenChange={setOpen} />
    </>
  );
}

function initials(name: string): string {
  return name
    .replace(/\(.*?\)/g, "")
    .trim()
    .split(/\s+/)
    .map((w) => w[0] ?? "")
    .join("")
    .slice(0, 2)
    .toUpperCase();
}
