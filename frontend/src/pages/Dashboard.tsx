import { useCallback, useEffect, useMemo, useState } from "react";
import { ArrowTopRightOnSquareIcon } from "@heroicons/react/20/solid";
import PageContainer, { Col, PageContent, PageGrid } from "@/components/layout/PageContainer";
import PageHeader from "@/components/layout/PageHeader";
import ActivityChart from "@/components/ui/ActivityChart";
import { StatusRow } from "@/components/ui/Badge";
import LoadGauge from "@/components/ui/LoadGauge";
import MetricBars from "@/components/ui/MetricBars";
import MetricsStrip, { MetricFooter, MetricInline, type MetricItem } from "@/components/ui/MetricsStrip";
import Panel from "@/components/ui/Panel";
import { useLiveQuery } from "@/hooks/useLiveQuery";
import { api } from "@/api/client";
import { useTranslation } from "@/context/LocaleContext";

interface Stats {
  total_scripts: number;
  active_scripts: number;
  stopped_scripts: number;
  errors_24h: number;
  completed_tasks: number;
  active_cron_jobs: number;
  running_now: number;
}

interface Script {
  script_type: string;
}

export default function Dashboard() {
  const { t } = useTranslation();
  const [history, setHistory] = useState<number[]>(Array.from({ length: 32 }, (_, i) => 3 + (i % 7)));

  const fetchDashboard = useCallback(
    () =>
      Promise.all([
        api<Stats>("/api/v1/dashboard/stats"),
        api<Script[]>("/api/v1/scripts"),
      ]),
    [],
  );

  const { data, reload, refreshing, lastUpdated } = useLiveQuery(fetchDashboard, []);

  const stats = data?.[0] ?? null;
  const scripts = data?.[1] ?? [];

  useEffect(() => {
    if (stats) {
      setHistory((prev) => [
        ...prev.slice(-47),
        Math.max(stats.running_now * 2 + 1, stats.completed_tasks % 15, 1),
      ]);
    }
  }, [stats]);

  const s = stats ?? {
    total_scripts: 0,
    active_scripts: 0,
    stopped_scripts: 0,
    errors_24h: 0,
    completed_tasks: 0,
    active_cron_jobs: 0,
    running_now: 0,
  };

  const metrics = useMemo<MetricItem[]>(
    () => [
      { label: t("dashboard.metrics.totalAssets"), value: s.total_scripts, hint: t("dashboard.metrics.totalAssetsHint"), tone: "accent" },
      { label: t("dashboard.metrics.active"), value: s.active_scripts, hint: t("dashboard.metrics.activeHint"), tone: "success" },
      { label: t("dashboard.metrics.running"), value: s.running_now, hint: t("dashboard.metrics.runningHint"), tone: "accent" },
      { label: t("dashboard.metrics.completed"), value: s.completed_tasks, hint: t("dashboard.metrics.completedHint"), tone: "default" },
      { label: t("dashboard.metrics.scheduled"), value: s.active_cron_jobs, hint: t("dashboard.metrics.scheduledHint"), tone: "default" },
      { label: t("dashboard.metrics.errors24h"), value: s.errors_24h, hint: t("dashboard.metrics.errors24hHint"), tone: s.errors_24h > 0 ? "danger" : "default" },
    ],
    [s, t],
  );

  const distribution = useMemo(() => {
    const counts = { script: 0, bot: 0 };
    scripts.forEach((sc) => {
      counts[sc.script_type as keyof typeof counts] += 1;
    });
    return [
      { label: t("common.script"), value: counts.script, color: "#22d3ee" },
      { label: t("common.bots"), value: counts.bot, color: "#34d399" },
      { label: t("common.cronJobs"), value: s.active_cron_jobs, color: "#818cf8" },
      { label: t("common.stopped"), value: s.stopped_scripts, color: "#71717a" },
    ];
  }, [scripts, s, t]);

  const loadPct = s.active_scripts > 0 ? Math.round((s.running_now / s.active_scripts) * 100) : 0;

  return (
    <PageContainer>
      <PageHeader
        title={t("nav.overview")}
        subtitle={t("dashboard.subtitle")}
        onRefresh={reload}
        refreshing={refreshing}
        lastUpdated={lastUpdated}
      />

      <PageContent>
        <MetricsStrip items={metrics} />

        <PageGrid className="items-stretch">
          <Col span={8}>
            <Panel
              className="h-full"
              title={t("dashboard.throughput.title")}
              subtitle={t("dashboard.throughput.subtitle")}
              flush
              bodyClassName="flex flex-1 flex-col px-5 pb-5 pt-4"
            >
              <div className="min-h-[280px] flex-1">
                <ActivityChart data={history} height={280} />
              </div>
              <MetricFooter>
                <MetricInline label={t("dashboard.metrics.completed")} value={s.completed_tasks} />
                <MetricInline label={t("dashboard.metrics.running")} value={s.running_now} />
                <MetricInline label={t("common.stopped")} value={s.stopped_scripts} />
                <MetricInline label={t("dashboard.throughput.capacity")} value={`${loadPct}%`} />
              </MetricFooter>
            </Panel>
          </Col>

          <Col span={4}>
            <Panel className="h-full" title={t("dashboard.load.title")} bodyClassName="flex flex-1 items-center justify-center py-4">
              <LoadGauge
                size={220}
                value={s.running_now}
                max={Math.max(s.active_scripts, 1)}
                label={t("dashboard.load.capacityUsed", { pct: loadPct })}
              />
            </Panel>
          </Col>

          <Col span={4}>
            <Panel className="h-full" title={t("dashboard.health.title")} bodyClassName="flex flex-1 flex-col">
              <StatusRow label={t("dashboard.health.activeScripts")} value={s.active_scripts} tone="success" />
              <StatusRow label={t("dashboard.health.runningSandboxes")} value={s.running_now} tone={s.running_now > 0 ? "accent" : "neutral"} />
              <StatusRow label={t("dashboard.health.scheduledTasks")} value={s.active_cron_jobs} tone="neutral" />
              <StatusRow label={t("dashboard.health.failures24h")} value={s.errors_24h} tone={s.errors_24h > 0 ? "danger" : "success"} />
            </Panel>
          </Col>

          <Col span={4}>
            <Panel className="h-full" title={t("dashboard.assetMix.title")} subtitle={t("dashboard.assetMix.subtitle")} bodyClassName="flex flex-1 flex-col justify-center">
              <MetricBars items={distribution} />
            </Panel>
          </Col>

          <Col span={4}>
            <Panel className="h-full" title={t("dashboard.observability.title")} bodyClassName="flex flex-1 flex-col justify-between">
              <p className="text-sm leading-relaxed text-muted">{t("dashboard.observability.description")}</p>
              <a
                href="http://localhost:3000"
                target="_blank"
                rel="noreferrer"
                className="inline-flex w-fit items-center gap-2 rounded-lg bg-cyan-400/10 px-4 py-2.5 text-sm font-semibold text-cyan-400 ring-1 ring-inset ring-cyan-400/20 transition-colors hover:bg-cyan-400/15"
              >
                {t("dashboard.observability.openGrafana")}
                <ArrowTopRightOnSquareIcon className="size-4" />
              </a>
            </Panel>
          </Col>
        </PageGrid>
      </PageContent>
    </PageContainer>
  );
}
