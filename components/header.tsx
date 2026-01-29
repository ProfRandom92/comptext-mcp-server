export function Header() {
  return (
    <header className="border-b bg-card shadow-sm">
      <div className="container mx-auto px-4 py-6">
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-3xl font-bold text-foreground">
              CompText MCP Agent Manager
            </h1>
            <p className="mt-1 text-sm text-muted-foreground">
              Verwalte Agenten mit Model Context Protocol Verbindungen
            </p>
          </div>
          <div className="flex items-center gap-2">
            <div className="h-2 w-2 rounded-full bg-emerald-500 animate-pulse" />
            <span className="text-sm text-muted-foreground">System Online</span>
          </div>
        </div>
      </div>
    </header>
  )
}
