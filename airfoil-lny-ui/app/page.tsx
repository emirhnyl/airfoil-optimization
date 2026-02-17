"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";
import { Button, Card } from "@/components/ui";

const API = process.env.NEXT_PUBLIC_API_BASE || "http://localhost:8000";

export default function Home() {
  const [loading, setLoading] = useState(false);
  const [configName, setConfigName] = useState("baseline.yaml");
  const router = useRouter();

  const start = async () => {
    setLoading(true);
    try {
      const res = await fetch(`${API}/api/start`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ config_name: configName }),
      });
      const data = await res.json();
      if (!res.ok) throw new Error(data?.detail || "Start failed");
      router.push(`/run/${data.run_id}`);
    } catch (e: any) {
      alert(e.message || "Error");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="max-w-6xl mx-auto px-6 py-10">
      <div className="grid gap-6 lg:grid-cols-2 items-start">
        <div>
          <div className="inline-flex items-center gap-2 rounded-full border border-lny-line bg-white/5 px-3 py-1 text-xs text-white/80">
            <span className="h-2 w-2 rounded-full bg-lny-yellow" />
            Teknopark-grade MVP • XFOIL Pipeline
          </div>

          <h1 className="mt-4 text-4xl font-black leading-tight">
            Airfoil tasarımını <span className="text-lny-yellow">optimizasyon</span> ile hızlandır.
          </h1>
          <p className="mt-3 text-white/70">
            Parametrik profil → XFOIL poları → en iyi L/D → otomatik raporlar, 2D çizim ve 3D (3MF) çıktı.
          </p>

          <div className="mt-6 flex gap-3">
            <Button onClick={start} disabled={loading}>
              {loading ? "Running..." : "Start Optimization"}
            </Button>
            <Button href="/runs" variant="ghost">
              View Runs
            </Button>
          </div>

          <div className="mt-8 grid gap-3 sm:grid-cols-3">
            {[
              { t: "Optimization", d: "Bounds + constraints ile iteratif arama" },
              { t: "Polars", d: "CL/CD, CL-AoA, CD-AoA, L/D-AoA" },
              { t: "Exports", d: "SVG, DXF, 3MF + ZIP paket" },
            ].map((x) => (
              <div key={x.t} className="rounded-2xl border border-white/10 bg-white/[0.03] p-4">
                <div className="font-semibold">{x.t}</div>
                <div className="text-xs text-white/60 mt-1">{x.d}</div>
              </div>
            ))}
          </div>
        </div>

        <Card title="Run configuration" subtitle="Config dosyasını değiştirerek farklı senaryolar koşturabilirsin.">
          <div className="flex items-center gap-3">
            <div className="text-sm text-white/70 w-24">config</div>
            <input
              value={configName}
              onChange={(e) => setConfigName(e.target.value)}
              className="flex-1 rounded-2xl border border-white/10 bg-black/30 px-4 py-2 text-sm outline-none focus:border-lny-line"
              placeholder="baseline.yaml"
            />
          </div>

          <div className="mt-4 text-xs text-white/60">
            Çıktılar: <span className="text-white/80">2D (SVG/DXF)</span>,{" "}
            <span className="text-white/80">plots (PNG)</span>,{" "}
            <span className="text-white/80">3MF preview</span>,{" "}
            <span className="text-white/80">download_all.zip</span>
          </div>

          <div className="mt-5">
            <Button onClick={start} disabled={loading}>
              {loading ? "Running..." : "Run Now"}
            </Button>
          </div>
        </Card>
      </div>
    </div>
  );
}
