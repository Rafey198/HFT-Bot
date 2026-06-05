"use client";
import { useEffect, useRef, useState } from "react";
import { Upload, Database, Sparkles } from "lucide-react";
import { api } from "@/lib/api";
import { DataReport } from "@/lib/types";
import { PageHeader } from "@/components/PageHeader";
import { Panel, Button, Spinner } from "@/components/ui/primitives";
import { SymbolPicker } from "@/components/SymbolPicker";
import { MetricCard } from "@/components/dashboard/MetricCard";
import { WarningBanner } from "@/components/dashboard/WarningBanner";

export default function DataCenterPage() {
  const [symbol, setSymbol] = useState("XAUUSD");
  const [timeframe, setTimeframe] = useState("M5");
  const [report, setReport] = useState<DataReport | null>(null);
  const [datasets, setDatasets] = useState<any[]>([]);
  const [preview, setPreview] = useState<any[]>([]);
  const [loading, setLoading] = useState(false);
  const [err, setErr] = useState("");
  const fileRef = useRef<HTMLInputElement>(null);

  const loadDatasets = async () => {
    try {
      const d: any = await api.datasets();
      setDatasets(d.datasets || []);
    } catch (e) { /* backend offline */ }
  };
  useEffect(() => { loadDatasets(); }, []);

  const genDemo = async (kind: string) => {
    setLoading(true); setErr("");
    try {
      const r: any = await api.generateDemo({ symbol, timeframe, years: 10, kind });
      setReport(r);
      await loadDatasets();
      await showPreview(r.dataset_id);
    } catch (e) { setErr((e as Error).message); } finally { setLoading(false); }
  };

  const onUpload = async (file: File) => {
    setLoading(true); setErr("");
    try {
      const r: any = await api.uploadCsv(file, symbol, timeframe === "M5" ? "" : timeframe);
      setReport(r);
      await loadDatasets();
      await showPreview(r.dataset_id);
    } catch (e) { setErr((e as Error).message); } finally { setLoading(false); }
  };

  const showPreview = async (id: string) => {
    try {
      const s: any = await api.dataSummary(id);
      setPreview(s.preview || []);
    } catch { /* ignore */ }
  };

  return (
    <div className="space-y-4 p-5">
      <PageHeader
        title="Data Center"
        subtitle="Upload tick/OHLCV CSV or generate simulated XAUUSD demo data."
        right={<SymbolPicker symbol={symbol} timeframe={timeframe} onSymbol={setSymbol} onTimeframe={setTimeframe} />}
      />

      <div className="grid grid-cols-1 gap-4 lg:grid-cols-2">
        <Panel title="Ingest Data">
          <div className="space-y-3">
            <input
              ref={fileRef}
              type="file"
              accept=".csv"
              className="hidden"
              onChange={(e) => e.target.files?.[0] && onUpload(e.target.files[0])}
            />
            <Button variant="gold" onClick={() => fileRef.current?.click()} disabled={loading}>
              <Upload size={15} /> Upload CSV
            </Button>
            <div className="text-xs text-terminal-muted">
              <p className="mb-1">Supported formats:</p>
              <code className="mono block rounded bg-terminal-panel px-2 py-1">timestamp,bid,ask,volume</code>
              <code className="mono mt-1 block rounded bg-terminal-panel px-2 py-1">timestamp,open,high,low,close,volume</code>
            </div>
            <div className="flex gap-2 border-t border-terminal-border pt-3">
              <Button onClick={() => genDemo("ohlcv")} disabled={loading}><Sparkles size={14} /> Demo OHLCV</Button>
              <Button onClick={() => genDemo("tick")} disabled={loading}><Sparkles size={14} /> Demo Ticks</Button>
              {loading && <Spinner />}
            </div>
            {err && <WarningBanner tone="danger">{err}</WarningBanner>}
          </div>
        </Panel>

        <Panel title="Data Quality Report">
          {report ? (
            <div className="space-y-3">
              <div className="grid grid-cols-2 gap-2 sm:grid-cols-3">
                <MetricCard label="Rows" value={report.rows.toLocaleString()} />
                <MetricCard label="Quality" value={`${report.data_quality_score}`} tone={report.data_quality_score > 80 ? "buy" : "gold"} />
                <MetricCard label="Kind" value={report.kind} />
                <MetricCard label="Missing" value={report.missing_candles} />
                <MetricCard label="Duplicates" value={report.duplicate_rows_removed} />
                <MetricCard label="Invalid" value={report.invalid_rows_removed} />
              </div>
              <div className="text-xs text-terminal-muted">
                <span className="mono">{report.start_date?.slice(0, 16)}</span> → <span className="mono">{report.end_date?.slice(0, 16)}</span>
              </div>
              {report.warnings?.map((w, i) => <WarningBanner key={i}>{w}</WarningBanner>)}
            </div>
          ) : (
            <div className="py-8 text-center text-sm text-terminal-muted">Upload or generate data to see the quality report.</div>
          )}
        </Panel>
      </div>

      {preview.length > 0 && (
        <Panel title="Preview (first rows)">
          <div className="overflow-x-auto">
            <table className="w-full text-left text-xs">
              <thead className="text-[10px] uppercase text-terminal-muted">
                <tr className="border-b border-terminal-border">
                  {Object.keys(preview[0]).map((k) => <th key={k} className="py-1.5 pr-3">{k}</th>)}
                </tr>
              </thead>
              <tbody>
                {preview.map((row, i) => (
                  <tr key={i} className="border-b border-terminal-border/40">
                    {Object.values(row).map((v, j) => <td key={j} className="mono py-1 pr-3 text-gray-300">{String(v).slice(0, 18)}</td>)}
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </Panel>
      )}

      <Panel title={`Datasets (${datasets.length})`}>
        <div className="overflow-x-auto">
          <table className="w-full text-left text-xs">
            <thead className="text-[10px] uppercase text-terminal-muted">
              <tr className="border-b border-terminal-border">
                <th className="py-1.5 pr-3">Symbol</th><th className="pr-3">TF</th><th className="pr-3">Kind</th>
                <th className="pr-3">Rows</th><th className="pr-3">Quality</th><th className="pr-3">Created</th>
              </tr>
            </thead>
            <tbody>
              {datasets.map((d) => (
                <tr key={d.id} className="border-b border-terminal-border/40 hover:bg-terminal-panel/40 cursor-pointer" onClick={() => showPreview(d.id)}>
                  <td className="py-1.5 pr-3 text-gold">{d.symbol}</td>
                  <td className="pr-3">{d.timeframe}</td>
                  <td className="pr-3">{d.kind}</td>
                  <td className="mono pr-3">{d.rows?.toLocaleString()}</td>
                  <td className="mono pr-3">{d.quality_score}</td>
                  <td className="mono pr-3 text-terminal-muted">{d.created_at?.slice(0, 16)}</td>
                </tr>
              ))}
            </tbody>
          </table>
          {!datasets.length && <div className="flex items-center gap-2 py-6 text-sm text-terminal-muted"><Database size={16} /> No datasets yet.</div>}
        </div>
      </Panel>
    </div>
  );
}
