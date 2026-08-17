import { Fragment } from "react";
import { cn } from "../../utils/cn";

type Props = {
  text: string;
  as?: "h1" | "h2" | "p" | "span" | "div";
  className?: string;
  lineClassName?: string;
};

/**
 * Splits text into masked reveal lines. Each line renders a full
 * <span class="reveal-mask"><span class="line-inner">…</span></span> pair.
 * A visually-hidden full string is kept for screen readers; the split spans
 * are aria-hidden so the reader never hears fragments.
 */
export default function TextReveal({
  text,
  as: Tag = "span",
  className,
  lineClassName,
}: Props) {
  const lines = text.split("\n");

  return (
    <Tag className={cn(className)}>
      <span className="sr-only">{text}</span>
      <span aria-hidden className="block">
        {lines.map((line, i) => (
          <Fragment key={i}>
            {i > 0 && <br />}
            <span className={cn("reveal-mask block", lineClassName)}>
              <span className="line-inner block will-change-transform">
                {line || " "}
              </span>
            </span>
          </Fragment>
        ))}
      </span>
    </Tag>
  );
}