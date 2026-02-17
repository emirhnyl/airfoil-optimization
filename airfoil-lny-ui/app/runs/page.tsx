export const dynamic = "force-dynamic";
const API = process.env.NEXT_PUBLIC_API_BASE || "http://localhost:8000";

export default async function RunsPage() {
  const res = await fetch(`${API}/api/runs`, { cache: "no-store" });
  const data = await res.json();
  const runs: string[] = data.runs || [];

  return (
    <div className="max-w-6xl mx-auto px-6 py-10">
      <h1 className="text-2xl font-bold mb-4">Runs</h1>

      <div className="grid gap-3">
        {runs.length === 0 ? (
          <div className="text-white/60">No runs yet.</div>
        ) : (
          runs.map((id) => (
            <a
              key={id}
              href={`/run/${id}`}
              className="rounded-2xl border border-white/10 bg-white/[0.03] p-4 hover:bg-white/[0.06] transition"
            >
              <div className="font-semibold">{id}</div>
              <div className="text-xs text-white/60 mt-1">Open details → downloads + 3D preview</div>
            </a>
          ))
        )}
      </div>
    </div>
  );
}
