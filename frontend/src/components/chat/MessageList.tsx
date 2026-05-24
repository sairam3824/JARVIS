import { useEffect, useRef } from "react";
import type { ChatMessage } from "@/types/api";
import { cn } from "@/utils/cn";

export function MessageList({ messages }: { messages: ChatMessage[] }) {
  const bottomRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages]);

  return (
    <div className="space-y-4">
      {messages.map((message, index) => (
        <article
          key={`${message.role}-${index}`}
          className={cn(
            "max-w-3xl rounded-[24px] border px-4 py-3 backdrop-blur-xl",
            message.role === "user"
              ? "ml-auto border-hud-glow/30 bg-hud-glow/10 text-right"
              : message.role === "tool"
                ? "border-amber-300/20 bg-amber-200/5 text-amber-100"
                : "border-white/10 bg-white/5 text-slate-100",
          )}
        >
          <p className="mb-2 font-body text-[11px] uppercase tracking-[0.28em] text-slate-400">{message.role}</p>
          <p className={cn("font-body text-lg leading-7", message.pending && "after:ml-1 after:inline-block after:h-4 after:w-2 after:animate-pulse after:bg-hud-soft after:content-['']")}>
            {message.content || "Streaming response..."}
          </p>
        </article>
      ))}
      <div ref={bottomRef} />
    </div>
  );
}

