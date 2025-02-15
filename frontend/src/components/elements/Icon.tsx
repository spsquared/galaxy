import type React from "react";
import {
  ClipboardDocumentIcon as ClipboardDocumentIcon24,
  HomeIcon as HomeIcon24,
  MapIcon as MapIcon24,
  TrophyIcon as TrophyIcon24,
  ChartBarIcon as ChartBarIcon24,
  ClockIcon as ClockIcon24,
  UserGroupIcon as UserGroupIcon24,
  ArrowUpTrayIcon as ArrowUpTrayIcon24,
  PlayCircleIcon as PlayCircleIcon24,
  ChevronDownIcon as ChevronDownIcon24,
  CheckIcon as CheckIcon24,
  InformationCircleIcon as InformationCircleIcon24,
  Bars3Icon as Bars3Icon24,
  XMarkIcon as XMarkIcon24,
  EyeIcon as EyeIcon24,
  EyeSlashIcon as EyeSlashIcon24,
  ShieldCheckIcon as ShieldCheckIcon24,
  QuestionMarkCircleIcon as QuestionMarkCircleIcon24,
  LightBulbIcon as LightBulbIcon24,
  ChevronLeftIcon as ChevronLeftIcon24,
  ChevronRightIcon as ChevronRightIcon24,
  ComputerDesktopIcon as ComputerDesktopIcon24,
  UserCircleIcon as UserCircleIcon24,
  UserPlusIcon as UserPlusIcon24,
} from "@heroicons/react/24/outline";

import {
  ClipboardDocumentIcon as ClipboardDocumentIcon20,
  HomeIcon as HomeIcon20,
  MapIcon as MapIcon20,
  TrophyIcon as TrophyIcon20,
  ChartBarIcon as ChartBarIcon20,
  ClockIcon as ClockIcon20,
  UserGroupIcon as UserGroupIcon20,
  ArrowUpTrayIcon as ArrowUpTrayIcon20,
  PlayCircleIcon as PlayCircleIcon20,
  ChevronDownIcon as ChevronDownIcon20,
  CheckIcon as CheckIcon20,
  InformationCircleIcon as InformationCircleIcon20,
  Bars3Icon as Bars3Icon20,
  XMarkIcon as XMarkIcon20,
  EyeIcon as EyeIcon20,
  EyeSlashIcon as EyeSlashIcon20,
  ShieldCheckIcon as ShieldCheckIcon20,
  QuestionMarkCircleIcon as QuestionMarkCircleIcon20,
  LightBulbIcon as LightBulbIcon20,
  ChevronLeftIcon as ChevronLeftIcon20,
  ChevronRightIcon as ChevronRightIcon20,
  ComputerDesktopIcon as ComputerDesktopIcon20,
  UserCircleIcon as UserCircleIcon20,
  UserPlusIcon as UserPlusIcon20,
} from "@heroicons/react/20/solid";

const icons24 = {
  clipboard_document: ClipboardDocumentIcon24,
  home: HomeIcon24,
  map: MapIcon24,
  trophy: TrophyIcon24,
  chart_bar: ChartBarIcon24,
  clock: ClockIcon24,
  user_group: UserGroupIcon24,
  arrow_up_tray: ArrowUpTrayIcon24,
  play_circle: PlayCircleIcon24,
  chevron_down: ChevronDownIcon24,
  check: CheckIcon24,
  information_circle: InformationCircleIcon24,
  bars_3: Bars3Icon24,
  x_mark: XMarkIcon24,
  eye: EyeIcon24,
  eye_slash: EyeSlashIcon24,
  shield_check: ShieldCheckIcon24,
  question_mark_circle: QuestionMarkCircleIcon24,
  light_bulb: LightBulbIcon24,
  chevron_left: ChevronLeftIcon24,
  chevron_right: ChevronRightIcon24,
  computer_desktop: ComputerDesktopIcon24,
  user_circle: UserCircleIcon24,
  user_plus: UserPlusIcon24,
};

const icons20 = {
  clipboard_document: ClipboardDocumentIcon20,
  home: HomeIcon20,
  map: MapIcon20,
  trophy: TrophyIcon20,
  chart_bar: ChartBarIcon20,
  clock: ClockIcon20,
  user_group: UserGroupIcon20,
  arrow_up_tray: ArrowUpTrayIcon20,
  play_circle: PlayCircleIcon20,
  chevron_down: ChevronDownIcon20,
  check: CheckIcon20,
  information_circle: InformationCircleIcon20,
  bars_3: Bars3Icon20,
  x_mark: XMarkIcon20,
  eye: EyeIcon20,
  eye_slash: EyeSlashIcon20,
  shield_check: ShieldCheckIcon20,
  question_mark_circle: QuestionMarkCircleIcon20,
  light_bulb: LightBulbIcon20,
  chevron_left: ChevronLeftIcon20,
  chevron_right: ChevronRightIcon20,
  computer_desktop: ComputerDesktopIcon20,
  user_circle: UserCircleIcon20,
  user_plus: UserPlusIcon20,
};

export type IconName = keyof typeof icons24;

export interface IconProps {
  name: IconName;
  size?: "sm" | "md" | "xs" | "lg";
  className?: string;
}

const sizeToClass = {
  xs: "h-4 w-4",
  sm: "h-5 w-5",
  md: "h-6 w-6",
  lg: "h-7 w-7",
};

const Icon: React.FC<IconProps> = ({
  name,
  size = "md",
  className = "",
}: IconProps) => {
  const IconComponent =
    size === "md" || size === "lg" ? icons24[name] : icons20[name];
  return <IconComponent className={`${sizeToClass[size]} ${className}`} />;
};

export default Icon;
