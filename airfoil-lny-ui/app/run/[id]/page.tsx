import ThreeMFViewer from "@/components/ThreeMFViewer";
import { Button, Card } from "@/components/ui";

export const dynamic = "force-dynamic";
const API = process.env.NEXT_PUBLIC_API_BASE || "http://localhost:8000";

export default async function RunPage({ params }: { params: { id: string } }) {
  const runId = params.id;

  const expRes = await fetch(`${API}/api/run/${runId}/exports`, { cache: "no-store" });
  const exp = await expRes.json();
  const files: string[] = exp.files || [];

  const fileUrl = (rel: string) => `${API}/api/run/${runId}/file?rel=${encodeURIComponent(rel)}`;
  const has = (rel: string) => files.includes(rel);

  return (
    <div className="max-w-6xl mx-auto px-6 py-10">
      <div className="flex items-center justify-between gap-4 flex-wrap">
        <div>
          <h1 className="text-2xl font-bold">Run</h1>
          <div className="text-sm text-white/60">{runId}</div>
        </div>
        <div className="flex gap-2 flex-wrap">
          <Button href={fileUrl("download_all.zip")} download>Download All (ZIP)</Button>
          <Button href="/runs" variant="ghost">Back</Button>
        </div>
      </div>

      <div className="mt-6 grid gap-6 lg:grid-cols-2">
        <Card title="Downloads" subtitle="Tüm çıktılar ayrı ayrı indirilebilir.">
          <div className="flex gap-2 flex-wrap">
            <Button href={fileUrl("exports/airfoil.svg")} download variant="ghost">SVG</Button>
            <Button href={fileUrl("exports/airfoil.dxf")} download variant="ghost">DXF</Button>
            <Button href={fileUrl("exports/airfoil.3mf")} download variant="ghost">3MF</Button>
            <Button href={fileUrl("exports/polar.json")} download variant="ghost">polar.json</Button>
          </div>

          <div className="mt-4 flex gap-2 flex-wrap">
            {["cl_vs_cd.png", "cl_vs_aoa.png", "cd_vs_aoa.png", "ld_vs_aoa.png"].map((p) => (
              <Button key={p} href={fileUrl(`exports/${p}`)} download variant="ghost">
                {p}
              </Button>
            ))}
          </div>
        </Card>

        <Card title="3D Preview" subtitle="3MF dosyası sayfa içinde görüntülenir.">
          {has("exports/airfoil.3mf") ? (
            <ThreeMFViewer url={fileUrl("exports/airfoil.3mf")} />
          ) : (
            <div className="text-white/60">3MF not found.</div>
          )}
        </Card>
      </div>

      <Card title="Plots" subtitle="XFOIL poları üzerinden üretilen grafikler.">
        <div className="mt-2 grid gap-3 sm:grid-cols-2 lg:grid-cols-4">
          {["cl_vs_cd.png", "cl_vs_aoa.png", "cd_vs_aoa.png", "ld_vs_aoa.png"].map((p) => (
            <div key={p} className="rounded-2xl border border-white/10 bg-black/20 p-2">
              <img
                src={fileUrl(`exports/${p}`)}
                alt={p}
                className="w-full rounded-xl border border-white/5"
              />
              <div className="text-xs text-white/60 mt-2">{p}</div>
            </div>
          ))}
        </div>
      </Card>
    </div>
  );
}
