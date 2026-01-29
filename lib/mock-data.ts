export interface SimplifiedAgentWithMCP {
  id: string
  name: string
  status: 'active' | 'idle' | 'error' | 'initializing'
  mcpConnection: {
    status: 'connected' | 'connecting' | 'disconnected' | 'error'
    url: string
    metrics?: {
      requestCount: number
      successRate: number
    }
  }
  config: {
    capabilities?: string[]
  }
}

export const mockAgents: SimplifiedAgentWithMCP[] = [
  {
    id: 'agent-001-mcp-demo',
    name: 'CompText Parser',
    status: 'active',
    mcpConnection: {
      status: 'connected',
      url: 'mcp://localhost:3000/comptext',
      metrics: {
        requestCount: 1247,
        successRate: 99.2
      }
    },
    config: {
      capabilities: ['parse', 'validate', 'transform', 'optimize']
    }
  },
  {
    id: 'agent-002-mcp-demo',
    name: 'Context Manager',
    status: 'active',
    mcpConnection: {
      status: 'connected',
      url: 'mcp://localhost:3000/context',
      metrics: {
        requestCount: 856,
        successRate: 98.7
      }
    },
    config: {
      capabilities: ['cache', 'retrieve', 'update']
    }
  },
  {
    id: 'agent-003-mcp-demo',
    name: 'DSL Compiler',
    status: 'idle',
    mcpConnection: {
      status: 'connected',
      url: 'mcp://localhost:3000/compiler',
      metrics: {
        requestCount: 423,
        successRate: 97.5
      }
    },
    config: {
      capabilities: ['compile', 'optimize', 'validate']
    }
  }
]
