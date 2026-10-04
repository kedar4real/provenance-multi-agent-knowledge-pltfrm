import { forwardRef, type ButtonHTMLAttributes } from "react";

import { cn } from "../lib/cn";

type Variant = "primary" | "ghost" | "outline";

const variants: Record<Variant, string> = {
  primary: "bg-ink text-paper hover:bg-ink-2",
  outline: "border border-rule bg-sheet text-ink hover:border-rule-strong",
  ghost: "text-ink-2 hover:bg-inset hover:text-ink",
};

export const Button = forwardRef<HTMLButtonElement, ButtonHTMLAttributes<HTMLButtonElement> & { variant?: Variant }>(
  function Button({ variant = "primary", className, type = "button", ...props }, ref) {
    return (
      <button
        ref={ref}
        type={type}
        className={cn(
          "inline-flex h-9 items-center justify-center gap-2 rounded-md px-3.5 text-sm font-medium transition-[background-color,border-color,transform] duration-100 active:scale-[0.97] disabled:cursor-not-allowed disabled:opacity-50 disabled:active:scale-100",
          variants[variant],
          className,
        )}
        {...props}
      />
    );
  },
);

export function Chip({ children, className }: { children: React.ReactNode; className?: string }) {
  return (
    <span
      className={cn(
        "inline-flex items-center rounded border border-rule px-1.5 py-px font-mono text-[12px] leading-5 text-ink-2",
        className,
      )}
    >
      {children}
    </span>
  );
}
