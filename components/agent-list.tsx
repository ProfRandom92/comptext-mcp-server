'use client'

import { useState } from 'react'
import { AgentCard } from './agent-card'
import { AgentWithMCP } from '@/types/agent-mcp'
import { mockAgents } from '@/lib/mock-data'

export function AgentList() {
  const [agents] = useState<AgentWithMCP[]>(mockAgents)

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-2xl font-bold text-slate-900">Aktive Agenten</h2>
          <p className="text-sm text-slate-600 mt-1">
            {agents.length} Agent{agents.length !== 1 ? 'en' : ''} mit MCP-Verbindung
          </p>
        </div>
      </div>

      <div className="grid gap-6 md:grid-cols-2 lg:grid-cols-3">
        {agents.map((agent) => (
          <AgentCard key={agent.id} agent={agent} />
        ))}
      </div>
    </div>
  )
}
