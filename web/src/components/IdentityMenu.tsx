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
        <Menu.Trigger className="flex h-9 items-center gap-2 rounded-md border border-rule bg-sheet pr-2 pl-2.5 text-sm hover:border-rule-strong data-popup-open:border-rule-strong">
          <UserRound aria-hidden className="size-4 text-ink-3" />
          <span className="max-w-48 truncate">{active ? active.displayName : "No identity"}</span>
          <ChevronsUpDown aria-hidden className="size-3.5 text-ink-4" />
        </Menu.Trigger>
        <Menu.Portal>
          <Menu.Positioner sideOffset={6} align="end" className="z-30">
            <Menu.Popup className="w-72 origin-(--transform-origin) rounded-lg border border-rule bg-sheet p-1 shadow-md transition-[opacity,transform] duration-150 ease-out data-ending-style:scale-95 data-ending-style:opacity-0 data-starting-style:scale-95 data-starting-style:opacity-0">
              {all.length > 0 && (
                <Menu.RadioGroup value={active?.name ?? ""} onValueChange={(v: string) => identities.activate(v)}>
                  <Menu.GroupLabel className="px-2.5 pt-1.5 pb-1 text-xs font-medium text-ink-3">
                    Search as
                  </Menu.GroupLabel>
                  {all.map((identity) => (
                    <Menu.RadioItem key={identity.name} value={identity.name} className={itemClass}>
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
          "inline-flex h-9 items-center gap-2 rounded-md bg-ink px-3.5 text-sm font-medium text-paper hover:bg-ink-2"
        }
      >
        <Plus aria-hidden className="size-4" />
        Add an identity
      </button>
      <AddIdentityDialog open={open} onOpenChange={setOpen} />
    </>
  );
}
