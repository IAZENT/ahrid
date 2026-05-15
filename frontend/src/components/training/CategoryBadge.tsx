import { CATEGORIES, type CategoryId } from "../../lib/categories";
import { cn } from "../../lib/utils";

type Size = "sm" | "md" | "lg";

const paddingBySize: Record<Size, string> = {
  sm: "px-2 py-0.5 text-2xs gap-1",
  md: "px-2.5 py-1 text-xs gap-1.5",
  lg: "px-3 py-1.5 text-sm gap-2",
};

const iconSize: Record<Size, number> = { sm: 12, md: 14, lg: 16 };

export function CategoryBadge({
  category, size = "md", showLabel = true, className,
}: {
  category: CategoryId | string;
  size?: Size;
  showLabel?: boolean;
  className?: string;
}) {
  const meta =
    CATEGORIES[category as CategoryId] ??
    ({
      id: category as CategoryId,
      displayName: category,
      icon: CATEGORIES.phishing_email.icon,
      colour: "#6B7280",
      description: "",
    });
  const Icon = meta.icon;
  return (
    <span
      className={cn(
        "inline-flex items-center rounded-full border font-medium",
        paddingBySize[size],
        className,
      )}
      style={{
        color: meta.colour,
        borderColor: `color-mix(in srgb, ${meta.colour} 40%, transparent)`,
        background: `color-mix(in srgb, ${meta.colour} 12%, transparent)`,
      }}
    >
      <Icon size={iconSize[size]} />
      {showLabel && <span>{meta.displayName}</span>}
    </span>
  );
}
