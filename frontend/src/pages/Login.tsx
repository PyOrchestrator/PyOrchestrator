import { useState } from "react";
import { useNavigate } from "react-router-dom";
import Button from "@/components/ui/Button";
import { FieldGroup, FieldLabel, Input } from "@/components/ui/Input";
import Panel from "@/components/ui/Panel";
import ThemeToggle from "@/components/ui/ThemeToggle";
import { useAuth } from "@/context/AuthContext";
import { useTranslation } from "@/context/LocaleContext";

export default function LoginPage() {
  const { t } = useTranslation();
  const [email, setEmail] = useState("admin@pyorchestrator.local");
  const [password, setPassword] = useState("admin");
  const [error, setError] = useState("");
  const { login } = useAuth();
  const navigate = useNavigate();

  const submit = async (e: React.FormEvent) => {
    e.preventDefault();
    try {
      await login(email, password);
      navigate("/");
    } catch (err) {
      setError(String(err));
    }
  };

  return (
    <div className="grid min-h-screen lg:grid-cols-2">
      <div className="hidden flex-col justify-between border-r border-line bg-surface p-12 lg:flex xl:p-16">
        <div>
          <div className="mb-16 flex items-center gap-3">
            <div className="flex size-8 items-center justify-center rounded-lg bg-cyan-400 text-xs font-extrabold text-on-accent">
              PO
            </div>
            <span className="text-sm font-bold text-foreground">PyOrchestrator</span>
          </div>
          <h2 className="max-w-md text-3xl font-bold leading-tight tracking-tight text-foreground xl:text-4xl">
            {t("login.headline")}
          </h2>
          <p className="mt-6 max-w-lg text-sm leading-relaxed text-muted">{t("login.description")}</p>
        </div>
        <p className="text-xs text-dim">{t("layout.brandTagline")}</p>
      </div>

      <div className="relative flex items-center justify-center bg-canvas px-6 py-12 sm:px-12 lg:px-16">
        <div className="absolute right-4 top-4 sm:right-6 sm:top-6">
          <ThemeToggle />
        </div>
        <div className="w-full max-w-md">
          <div className="mb-8 text-center lg:text-left">
            <h1 className="text-2xl font-bold text-foreground lg:hidden">PyOrchestrator</h1>
            <h1 className="hidden text-2xl font-bold text-foreground lg:block">{t("login.signIn")}</h1>
            <p className="mt-2 text-sm text-muted">{t("login.subtitle")}</p>
          </div>

          {error && (
            <div className="mb-6 rounded-lg bg-red-500/10 px-4 py-3 text-sm text-red-300 ring-1 ring-inset ring-red-500/20">
              {error}
            </div>
          )}

          <Panel bodyClassName="p-6 sm:p-8">
            <form onSubmit={submit} className="space-y-5">
              <FieldGroup>
                <FieldLabel htmlFor="email">{t("common.email")}</FieldLabel>
                <Input id="email" type="email" value={email} onChange={(e) => setEmail(e.target.value)} />
              </FieldGroup>
              <FieldGroup>
                <FieldLabel htmlFor="password">{t("common.password")}</FieldLabel>
                <Input id="password" type="password" value={password} onChange={(e) => setPassword(e.target.value)} />
              </FieldGroup>
              <Button type="submit" size="lg" className="w-full">
                {t("common.continue")}
              </Button>
            </form>
          </Panel>

          <p className="mt-6 text-center text-xs text-dim">{t("login.demoHint")}</p>
        </div>
      </div>
    </div>
  );
}
