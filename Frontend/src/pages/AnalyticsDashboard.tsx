// src/pages/AnalyticsDashboard.tsx
import React, { useEffect, useState, useCallback } from "react";
import {
  Shield,
  BellRing,
  Video,
  UserSearch,
  Volume2,
  RefreshCw,
  DownloadCloud,
} from "lucide-react";

import {
  BarChart,
  Bar,
  XAxis,
  YAxis,
  Tooltip,
  ResponsiveContainer,
  LineChart,
  Line,
  CartesianGrid,
} from "recharts";

import { Card, CardHeader, CardTitle, CardContent } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";

// ================= Type Definitions =================
type SummaryResponse = {
  total_alerts_today: number;
  detected_criminals: number;
  active_cameras: number;
  safety_index: number;
  peak_hour: string;
  top_location: string;
};

type TrendResponse = {
  by_type: { _id: string; count: number }[];
  crowd_trend: { date: string; avg_people: number }[];
  hourly_today: { hour: string; count: number }[];
  top_subtypes: { _id: string; count: number }[];
};

type AlertRow = {
  _id: string;
  type: string[];
  sub_type?: string | null;
  person_name?: string | null;
  confidence?: number | null;
  date: string;
  time: string;
  location?: string;
  violence_detected?: boolean;
  people_count?: number;
};

type HeatRow = {
  hour: string;
  density: number;
};

type ReappearanceRow = {
  person_name: string;
  count: number;
};

// ================= Dashboard Component =================
const AnalyticsDashboard: React.FC = () => {
  const [summary, setSummary] = useState<SummaryResponse | null>(null);
  const [trends, setTrends] = useState<TrendResponse | null>(null);
  const [recentAlerts, setRecentAlerts] = useState<AlertRow[]>([]);
  const [voiceText, setVoiceText] = useState<string>("");
  const [voiceTextHindi, setVoiceTextHindi] = useState<string>("");
  const [heatmap, setHeatmap] = useState<HeatRow[]>([]);
  const [reappearances, setReappearances] = useState<ReappearanceRow[]>([]);
  const [loadingReport, setLoadingReport] = useState(false);

  // ================= FETCH FUNCTIONS =================
  const fetchSummary = useCallback(async () => {
    try {
      const res = await fetch("http://127.0.0.1:5000/analytics/summary");
      setSummary(await res.json());
    } catch (_) {}
  }, []);

  const fetchTrends = useCallback(async () => {
    try {
      const res = await fetch("http://127.0.0.1:5000/analytics/trends");
      setTrends(await res.json());
    } catch (_) {}
  }, []);

  const fetchAlerts = useCallback(async () => {
    try {
      const res = await fetch("http://127.0.0.1:5000/alerts/recent?limit=50");
      let data = await res.json();

      // filter weapon < 50% confidence
      data = data.filter((d: AlertRow) => {
        const isWeapon = d.type?.some((t) =>
          t.toLowerCase().includes("weapon")
        );
        if (isWeapon) {
          if (!d.confidence) return false;
          return d.confidence >= 0.5;
        }
        return true;
      });

      setRecentAlerts(data);
    } catch (_) {}
  }, []);

  const fetchVoice = useCallback(async () => {
    try {
      const res = await fetch("http://127.0.0.1:5000/analytics/voice_summary");
      const data = await res.json();
      setVoiceText(data.text || "");
    } catch (_) {}
  }, []);

  const fetchVoiceHindi = useCallback(async () => {
    try {
      const res = await fetch(
        "http://127.0.0.1:5000/analytics/voice_summary_hindi"
      );
      const data = await res.json();
      setVoiceTextHindi(data.text || "");
    } catch (_) {}
  }, []);

  const fetchHeatmap = useCallback(async () => {
    try {
      const res = await fetch("http://127.0.0.1:5000/analytics/heatmap");
      setHeatmap(await res.json());
    } catch (_) {}
  }, []);

  const fetchReappearances = useCallback(async () => {
    try {
      const res = await fetch("http://127.0.0.1:5000/analytics/reappearances");
      setReappearances(await res.json());
    } catch (_) {}
  }, []);

  // ================= INITIAL LOAD =================
  useEffect(() => {
    fetchSummary();
    fetchTrends();
    fetchAlerts();
    fetchVoice();
    fetchVoiceHindi();
    fetchHeatmap();
    fetchReappearances();
  }, []);

  // ================= AUTO REFRESH =================
  useEffect(() => {
    const iv1 = setInterval(fetchSummary, 30000);
    const iv2 = setInterval(fetchTrends, 60000);
    const iv3 = setInterval(fetchAlerts, 10000);
    return () => {
      clearInterval(iv1);
      clearInterval(iv2);
      clearInterval(iv3);
    };
  }, []);

  // ================= VOICE (HINGLISH) =================
  const speakHinglish = (text: string) => {
    if (!text) return;
    const utter = new SpeechSynthesisUtterance(text);
    utter.lang = "hi-IN";
    utter.rate = 1;
    speechSynthesis.cancel();
    speechSynthesis.speak(utter);
  };

  // ================= PDF REPORT =================
  const generatePdfReport = async () => {
    setLoadingReport(true);
    try {
      const res = await fetch(
        "http://127.0.0.1:5000/analytics/generate_report"
      );
      if (!res.ok) throw new Error("Download failed");

      const blob = await res.blob();
      const url = URL.createObjectURL(blob);

      const a = document.createElement("a");
      a.href = url;
      a.download = `Security_Report_${Date.now()}.pdf`;
      a.click();

      URL.revokeObjectURL(url);
    } catch (e) {
      alert("Failed to generate report.");
    }
    setLoadingReport(false);
  };

  // ================= UI =================
  return (
    <div className="min-h-screen bg-[#0f172a] text-white p-6 space-y-6">
      {/* HEADER */}
      <div className="flex items-start justify-between">
        <div>
          <h1 className="text-3xl font-bold">Security Analytics Dashboard</h1>
          <p className="text-sm text-slate-400">
            Real-time surveillance intelligence for weapons, criminals & crowd
            activity.
          </p>
        </div>

        <div className="flex gap-2">
          <Button
            variant="outline"
            size="sm"
            onClick={() => {
              fetchSummary();
              fetchTrends();
              fetchAlerts();
              fetchHeatmap();
              fetchReappearances();
              fetchVoiceHindi();
            }}
          >
            <RefreshCw className="h-4 w-4 mr-2" /> Refresh All
          </Button>

          <Button size="sm" onClick={generatePdfReport}>
            <DownloadCloud className="h-4 w-4 mr-2" />
            {loadingReport ? "Generating..." : "Download PDF"}
          </Button>
        </div>
      </div>

      {/* ========== ROW 1 — Summary Cards ========== */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        {/* Card 1 */}
        <Card className="bg-slate-900/60 border-slate-700">
          <CardHeader>
            <CardTitle className="text-sm flex items-center gap-2">
              <BellRing className="text-red-400 h-4 w-4" />
              Alerts Today
            </CardTitle>
          </CardHeader>
          <CardContent>
            <p className="text-3xl font-bold">
              {summary?.total_alerts_today ?? 0}
            </p>
          </CardContent>
        </Card>

        {/* Card 2 */}
        <Card className="bg-slate-900/60 border-slate-700">
          <CardHeader>
            <CardTitle className="text-sm flex items-center gap-2">
              <Video className="text-emerald-400 h-4 w-4" />
              Active Cameras
            </CardTitle>
          </CardHeader>
          <CardContent>
            <p className="text-3xl font-bold">
              {summary?.active_cameras ?? 0}
            </p>
          </CardContent>
        </Card>

        {/* Card 3 */}
        <Card className="bg-slate-900/60 border-slate-700">
          <CardHeader>
            <CardTitle className="text-sm flex items-center gap-2">
              <UserSearch className="text-yellow-300 h-4 w-4" />
              Criminals Today
            </CardTitle>
          </CardHeader>
          <CardContent>
            <p className="text-3xl font-bold">
              {summary?.detected_criminals ?? 0}
            </p>
          </CardContent>
        </Card>

        {/* Card 4 */}
        <Card className="bg-slate-900/60 border-slate-700">
          <CardHeader>
            <CardTitle className="text-sm flex items-center gap-2">
              <Shield className="text-sky-400 h-4 w-4" />
              Safety Index
            </CardTitle>
          </CardHeader>
          <CardContent>
            <p className="text-3xl font-bold">
              {summary ? `${summary.safety_index}%` : "0%"}
            </p>
          </CardContent>
        </Card>
      </div>

      {/* ========== ROW 2 — Charts ========== */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-4">
        {/* Chart 1 */}
        <Card className="bg-slate-900/60 border-slate-700">
          <CardHeader>
            <CardTitle className="text-sm">Alerts by Type (7 days)</CardTitle>
          </CardHeader>
          <CardContent className="h-64">
            <ResponsiveContainer>
              <BarChart data={trends?.by_type || []}>
                <XAxis dataKey="_id" stroke="#94a3b8" />
                <YAxis stroke="#94a3b8" />
                <Tooltip />
                <Bar dataKey="count" fill="#f97316" radius={[6, 6, 0, 0]} />
              </BarChart>
            </ResponsiveContainer>
          </CardContent>
        </Card>

        {/* Chart 2 */}
        <Card className="bg-slate-900/60 border-slate-700">
          <CardHeader>
            <CardTitle className="text-sm">Alerts Over Time (Today)</CardTitle>
          </CardHeader>
          <CardContent className="h-64">
            <ResponsiveContainer>
              <LineChart data={trends?.hourly_today || []}>
                <CartesianGrid strokeDasharray="3 3" stroke="#1f2937" />
                <XAxis dataKey="hour" stroke="#94a3b8" />
                <YAxis stroke="#94a3b8" />
                <Tooltip />
                <Line
                  type="monotone"
                  stroke="#38bdf8"
                  dataKey="count"
                  strokeWidth={2}
                />
              </LineChart>
            </ResponsiveContainer>
          </CardContent>
        </Card>
      </div>

      {/* ========== ROW 3 — Predictive Summary / Voice / Heatmap / Reappearance ========== */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-4">
        {/* Predictive Summary */}
        <Card className="bg-gradient-to-r from-indigo-500/20 to-sky-500/10 border-slate-700">
          <CardHeader>
            <CardTitle>AI Predictive Summary</CardTitle>
          </CardHeader>
          <CardContent className="space-y-2">
            <p>
              <strong>Peak Hour:</strong> {summary?.peak_hour || "—"}
            </p>
            <p>
              <strong>Top Location:</strong> {summary?.top_location || "—"}
            </p>

            <div className="flex gap-2 mt-3">
              <Button
                size="sm"
                onClick={() => {
                  fetchVoice();
                  speakHinglish(voiceText);
                }}
              >
                <Volume2 className="h-4 w-4 mr-2" /> Speak (English)
              </Button>

              <Button
                size="sm"
                variant="secondary"
                onClick={() => {
                  fetchVoiceHindi();
                  speakHinglish(voiceTextHindi);
                }}
              >
                <Volume2 className="h-4 w-4 mr-2" /> Speak (Hinglish)
              </Button>
            </div>

            <div className="mt-3 text-xs text-slate-300">
              <strong>Hinglish Text:</strong>
              <div className="mt-1">{voiceTextHindi || "Loading..."}</div>
            </div>
          </CardContent>
        </Card>

        {/* Heatmap + Reappearances */}
        <div className="space-y-4">
          {/* Heatmap */}
          <Card className="bg-slate-900/60 border-slate-700">
            <CardHeader>
              <CardTitle className="text-sm">Crowd Density (Today)</CardTitle>
            </CardHeader>
            <CardContent>
              {heatmap.length === 0 ? (
                <p className="text-xs text-slate-400">No data available.</p>
              ) : (
                heatmap.map((h, i) => (
                  <div
                    key={i}
                    className="p-2 bg-[#071026] rounded flex justify-between mb-2"
                  >
                    <span>Hour: {h.hour}</span>
                    <span>Avg: {h.density}</span>
                  </div>
                ))
              )}
            </CardContent>
          </Card>

          {/* Reappearances */}
          <Card className="bg-slate-900/60 border-slate-700">
            <CardHeader>
              <CardTitle className="text-sm">Person Reappearances</CardTitle>
            </CardHeader>
            <CardContent>
              {reappearances.length === 0 ? (
                <p className="text-xs text-slate-400">
                  No repeat appearances today.
                </p>
              ) : (
                reappearances.map((r) => (
                  <div
                    key={r.person_name}
                    className="p-2 bg-[#071026] rounded flex justify-between mb-2"
                  >
                    <span>{r.person_name}</span>
                    <Badge variant="destructive">{r.count}x</Badge>
                  </div>
                ))
              )}
            </CardContent>
          </Card>
        </div>
      </div>

      {/* ========== ROW 4 — Recent Alerts Table ========== */}
      <Card className="bg-slate-900/60 border-slate-700">
        <CardHeader className="flex justify-between items-center">
          <CardTitle className="text-sm">Recent Alerts (Last 50)</CardTitle>
          <span className="text-xs text-slate-400">
            {recentAlerts.length} rows
          </span>
        </CardHeader>

        <CardContent className="overflow-x-auto">
          <table className="w-full text-sm">
            <thead className="text-slate-300 text-left">
              <tr>
                <th className="pb-2">Type</th>
                <th className="pb-2">Sub-Type / Person</th>
                <th className="pb-2">Conf.</th>
                <th className="pb-2">People</th>
                <th className="pb-2">Violence</th>
                <th className="pb-2">Date</th>
                <th className="pb-2">Time</th>
                <th className="pb-2">Location</th>
              </tr>
            </thead>

            <tbody>
              {recentAlerts.map((a) => (
                <tr
                  key={a._id}
                  className="border-t border-slate-800/60 hover:bg-slate-800/40"
                >
                  <td>{a.type?.join(", ")}</td>
                  <td>{a.sub_type || a.person_name || "—"}</td>
                  <td>
                    {a.confidence
                      ? (a.confidence * 100).toFixed(0) + "%"
                      : "—"}
                  </td>
                  <td>{a.people_count ?? "—"}</td>

                  <td>
                    {a.violence_detected ? (
                      <Badge variant="destructive">Yes</Badge>
                    ) : (
                      <Badge variant="secondary">No</Badge>
                    )}
                  </td>

                  <td>{a.date}</td>
                  <td>{a.time}</td>
                  <td>{a.location || "—"}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </CardContent>
      </Card>
    </div>
  );
};

export default AnalyticsDashboard;
