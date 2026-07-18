import { useTranslation, type Locale } from "@/context/LocaleContext";
import { cn } from "@/lib/cn";

const ORDER: Locale[] = ["en", "ru"];

export default function LanguageToggle({
  className,
  showLabel = false,
}: {
  className?: string;
  showLabel?: boolean;
}) {
  const { locale, setLocale, t } = useTranslation();

  const cycle = () => {
    const idx = ORDER.indexOf(locale);
    setLocale(ORDER[(idx + 1) % ORDER.length]!);
  };

  return (
    <button
      type="button"
      onClick={cycle}
      className={cn(
        "inline-flex items-center justify-center gap-1.5 rounded-md px-2 py-1.5 text-xs font-semibold uppercase tracking-wide text-muted transition-colors",
        "hover:bg-hover hover:text-cyan-400 focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-cyan-400",
        className,
      )}
      title={t("settings.localization.activeNow") + `: ${t(`settings.localization.${locale === "en" ? "english" : "russian"}`)}`}
      aria-label={t("settings.localization.subtitle")}
    >
      <span aria-hidden>{locale === "en" ? "EN" : "RU"}</span>
      {showLabel && <span className="normal-case tracking-normal">{t(`settings.localization.${locale === "en" ? "english" : "russian"}`)}</span>}
    </button>
  );
}
