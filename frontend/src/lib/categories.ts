import {
  Database,
  Key,
  Lock,
  Mail,
  MessageSquare,
  Phone,
  Usb,
  Users,
  type LucideIcon,
} from "lucide-react";

export const CATEGORY_IDS = [
  "phishing_email",
  "smishing",
  "vishing",
  "physical_security",
  "password_hygiene",
  "usb_baiting",
  "social_engineering",
  "data_handling",
] as const;

export type CategoryId = (typeof CATEGORY_IDS)[number];

export interface CategoryMeta {
  id: CategoryId;
  displayName: string;
  icon: LucideIcon;
  colour: string; // hex, master doc Phase 9
  description: string;
}

export const CATEGORIES: Record<CategoryId, CategoryMeta> = {
  phishing_email: {
    id: "phishing_email",
    displayName: "Phishing Email",
    icon: Mail,
    colour: "#3B82F6",
    description: "Spot malicious emails before they trick you.",
  },
  smishing: {
    id: "smishing",
    displayName: "Smishing (SMS)",
    icon: MessageSquare,
    colour: "#8B5CF6",
    description: "Recognise scam texts and fake links.",
  },
  vishing: {
    id: "vishing",
    displayName: "Vishing (Voice)",
    icon: Phone,
    colour: "#F97316",
    description: "Defend against phone-based social engineering.",
  },
  physical_security: {
    id: "physical_security",
    displayName: "Physical Security",
    icon: Lock,
    colour: "#EF4444",
    description: "Tailgating, badges, and office perimeter.",
  },
  password_hygiene: {
    id: "password_hygiene",
    displayName: "Password Hygiene",
    icon: Key,
    colour: "#EAB308",
    description: "Strong passwords, MFA, and storage.",
  },
  usb_baiting: {
    id: "usb_baiting",
    displayName: "USB Baiting",
    icon: Usb,
    colour: "#EC4899",
    description: "Handle unknown USB devices safely.",
  },
  social_engineering: {
    id: "social_engineering",
    displayName: "Social Engineering",
    icon: Users,
    colour: "#14B8A6",
    description: "Pretexts, urgency, and authority ploys.",
  },
  data_handling: {
    id: "data_handling",
    displayName: "Data Handling",
    icon: Database,
    colour: "#22C55E",
    description: "Classification, sharing, and retention.",
  },
};
