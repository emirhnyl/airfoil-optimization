import "./globals.css";

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="tr">
      <body>
        <div className="min-h-screen flex flex-col">
          <header className="border-b border-lny-line bg-lny-gray/40 backdrop-blur">
            <div className="max-w-6xl mx-auto px-6 py-4 flex items-center justify-between">
              <a href="/" className="flex items-center gap-3">
                <div className="h-9 w-9 rounded-xl bg-lny-yellow text-black font-black grid place-items-center">
                  LnY
                </div>
                <div className="leading-tight">
                  <div className="font-semibold">LnY Airfoil Optimization</div>
                  <div className="text-xs text-white/60">XFOIL • Optimization • 2D/3D Exports</div>
                </div>
              </a>

              <nav className="flex items-center gap-3">
                <a className="text-sm text-white/80 hover:text-white" href="/runs">Runs</a>
                <a className="text-sm text-white/80 hover:text-white" href="http://localhost:8000/docs" target="_blank">
                  API Docs
                </a>
              </nav>
            </div>
          </header>

          <main className="flex-1">{children}</main>

          <footer className="border-t border-lny-line">
            <div className="max-w-6xl mx-auto px-6 py-6 text-xs text-white/60 flex items-center justify-between">
              <span>© {new Date().getFullYear()} LnY Ar-Ge • Airfoil Optimization Platform</span>
              <span>Teknopark-grade commercialization</span>
            </div>
          </footer>
        </div>
      </body>
    </html>
  );
}
