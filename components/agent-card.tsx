'use client'

import { AgentWithMCP } from '@/types/agent-mcp'
import { Badge } from '@/components/ui/badge'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Activity, CheckCircle2, XCircle, AlertCircle, Zap } from 'lucide-react'

interface AgentCardProps {
  agent: AgentWithMCP
}

export function AgentCard({ agent }: AgentCardProps) {
  const statusConfig = {
    active: { icon: CheckCircle2, color: 'text-emerald-500', bg: 'bg-emerald-50', label: 'Aktiv' },
    idle: { icon: Activity, color: 'text-blue-500', bg: 'bg-blue-50', label: 'Bereit' },
    error: { icon: XCircle, color: 'text-red-500', bg: 'bg-red-50', label: 'Fehler' },
    initializing: { icon: AlertCircle, color: 'text-amber-500', bg: 'bg-amber-50', label: 'Initialisierung' },
  }

  const config = statusConfig[agent.status]
  const StatusIcon = config.icon

  const connectionStatusConfig = {
    connected: { color: 'bg-emerald-500', label: 'Verbunden' },
    connecting: { color: 'bg-amber-500', label: 'Verbinde...' },
    disconnected: { color: 'bg-red-500', label: 'Getrennt' },
    error: { color: 'bg-red-600', label: 'Verbindungsfehler' },
  }

  const connectionConfig = connectionStatusConfig[agent.mcpConnection.status]

  return (
    <Card className="hover:shadow-lg transition-shadow">
      <CardHeader>
        <div className="flex items-start justify-between">
          <div className="flex items-center gap-2">
            <div className={`p-2 rounded-lg ${config.bg}`}>
              <StatusIcon className={`h-5 w-5 ${config.color}`} />
            </div>
            <div>
              <CardTitle className="text-lg">{agent.name}</CardTitle>
              <CardDescription className="text-xs mt-1">
                ID: {agent.id.slice(0, 8)}
              </CardDescription>
            </div>
          </div>
        </div>
      </CardHeader>
      <CardContent className="space-y-4">
        <div className="flex items-center justify-between">
          <span className="text-sm text-slate-600">Status</span>
          <Badge variant="outline" className={config.bg}>
            {config.label}
          </Badge>
        </div>

        <div className="space-y-2">
          <div className="flex items-center justify-between text-sm">
            <span className="text-slate-600">MCP Verbindung</span>
            <div className="flex items-center gap-2">
              <div className={`h-2 w-2 rounded-full ${connectionConfig.color}`} />
              <span className="text-xs font-medium">{connectionConfig.label}</span>
            </div>
          </div>

          <div className="text-xs text-slate-500 bg-slate-50 rounded p-2 font-mono truncate">
            {agent.mcpConnection.url}
          </div>
        </div>

        {agent.mcpConnection.metrics && (
          <div className="grid grid-cols-2 gap-3 pt-3 border-t">
            <div className="space-y-1">
              <div className="flex items-center gap-1 text-xs text-slate-600">
                <Zap className="h-3 w-3" />
                <span>Anfragen</span>
              </div>
              <p className="text-lg font-semibold text-slate-900">
                {agent.mcpConnection.metrics.requestCount}
              </p>
            </div>
            <div className="space-y-1">
              <div className="text-xs text-slate-600">Erfolgsrate</div>
              <p className="text-lg font-semibold text-emerald-600">
                {agent.mcpConnection.metrics.successRate.toFixed(1)}%
              </p>
            </div>
          </div>
        )}

        {agent.config.capabilities && agent.config.capabilities.length > 0 && (
          <div className="pt-3 border-t">
            <div className="text-xs text-slate-600 mb-2">Fähigkeiten</div>
            <div className="flex flex-wrap gap-1">
              {agent.config.capabilities.slice(0, 3).map((cap) => (
                <Badge key={cap} variant="secondary" className="text-xs">
                  {cap}
                </Badge>
              ))}
              {agent.config.capabilities.length > 3 && (
                <Badge variant="secondary" className="text-xs">
                  +{agent.config.capabilities.length - 3}
                </Badge>
              )}
            </div>
          </div>
        )}
      </CardContent>
    </Card>
  )
}
