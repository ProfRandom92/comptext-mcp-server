/**
 * Beispiele für die Verwendung des AgentWithMCP Interfaces
 * 
 * Diese Datei zeigt verschiedene Anwendungsfälle und Implementierungsbeispiele.
 */

import {
  AgentWithMCP,
  MCPConnection,
  AgentConfig,
  createDefaultMCPConnection,
  createDefaultAgentConfig,
  createAgentWithMCP,
  isAgentConnected,
  isAgentActive,
  MCPAuthType,
  MCPTransportType,
} from './agent-mcp';

// ============================================================================
// Beispiel 1: Einfacher Agent mit lokaler MCP-Verbindung (stdio)
// ============================================================================

const simpleConnection = createDefaultMCPConnection(
  'mcp-local-001',
  'Local CompText Server',
  'python -m comptext_mcp.server'
);

const simpleConfig = createDefaultAgentConfig(
  'Code Review Agent',
  'Automatisierter Agent für Code-Reviews mit CompText'
);

const simpleAgent: AgentWithMCP = createAgentWithMCP(
  'agent-001',
  simpleConfig,
  simpleConnection
);

console.log('Simple Agent created:', simpleAgent.config.name);

// ============================================================================
// Beispiel 2: Agent mit REST API Verbindung und API-Key Auth
// ============================================================================

const restConnection: MCPConnection = {
  id: 'mcp-rest-001',
  name: 'Remote CompText API',
  status: 'disconnected',
  config: {
    url: 'https://comptext-api.example.com',
    transport: 'http',
    timeout: 60000,
    maxReconnectAttempts: 5,
    reconnectDelay: 10000,
    heartbeatInterval: 30000,
    enableLogging: true,
    headers: {
      'Content-Type': 'application/json',
      'User-Agent': 'CompText-Agent/1.0',
    },
  },
  auth: {
    type: 'api_key',
    apiKey: process.env.COMPTEXT_API_KEY || 'your-api-key-here',
    customHeaders: {
      'X-API-Key': process.env.COMPTEXT_API_KEY || 'your-api-key-here',
    },
  },
  metrics: {
    successfulRequests: 0,
    failedRequests: 0,
    averageResponseTime: 0,
    uptime: 0,
    reconnectionAttempts: 0,
  },
};

const restAgentConfig: AgentConfig = {
  name: 'Security Audit Agent',
  description: 'Führt Sicherheitsaudits mit CompText durch',
  defaultAudience: 'audit',
  defaultMode: 'bundle_only',
  maxConcurrentRequests: 3,
  requestTimeout: 60000,
  enableAutoRetry: true,
  maxRetries: 5,
  tags: ['security', 'audit', 'production'],
};

const restAgent: AgentWithMCP = createAgentWithMCP(
  'agent-002',
  restAgentConfig,
  restConnection
);

// ============================================================================
// Beispiel 3: Agent mit OAuth-Authentifizierung
// ============================================================================

const oauthConnection: MCPConnection = {
  id: 'mcp-oauth-001',
  name: 'Enterprise CompText Server',
  status: 'disconnected',
  config: {
    url: 'wss://enterprise.comptext.example.com',
    transport: 'websocket',
    timeout: 30000,
    maxReconnectAttempts: 10,
    reconnectDelay: 5000,
    heartbeatInterval: 15000,
    enableLogging: true,
  },
  auth: {
    type: 'oauth',
    oauth: {
      clientId: 'comptext-client-123',
      clientSecret: process.env.OAUTH_CLIENT_SECRET || '',
      accessToken: 'current-access-token',
      refreshToken: 'refresh-token-here',
      tokenExpiry: new Date(Date.now() + 3600000), // 1 Stunde
    },
  },
  metrics: {
    successfulRequests: 0,
    failedRequests: 0,
    averageResponseTime: 0,
    uptime: 0,
    reconnectionAttempts: 0,
  },
};

const enterpriseConfig: AgentConfig = {
  name: 'Executive Report Agent',
  description: 'Generiert Executive-Level Reports mit CompText',
  defaultAudience: 'exec',
  defaultMode: 'bundle_only',
  maxConcurrentRequests: 10,
  requestTimeout: 120000,
  enableAutoRetry: true,
  maxRetries: 3,
  customInstructions: 'Focus on high-level insights and strategic recommendations',
  tags: ['executive', 'reports', 'enterprise'],
};

const enterpriseAgent: AgentWithMCP = createAgentWithMCP(
  'agent-003',
  enterpriseConfig,
  oauthConnection
);

// ============================================================================
// Beispiel 4: Agent-Status-Management
// ============================================================================

// Funktion zum Aktualisieren des Agent-Status
function updateAgentStatus(agent: AgentWithMCP, newStatus: AgentWithMCP['status']): void {
  agent.status = newStatus;
  agent.updatedAt = new Date();
  agent.lastActivity = new Date();
  
  console.log(`Agent ${agent.config.name} status updated to: ${newStatus}`);
}

// Funktion zum Aktualisieren der Verbindungs-Metriken
function updateConnectionMetrics(
  connection: MCPConnection,
  success: boolean,
  responseTime: number
): void {
  const metrics = connection.metrics;
  
  if (success) {
    metrics.successfulRequests++;
    metrics.lastSuccessfulRequest = new Date();
  } else {
    metrics.failedRequests++;
  }
  
  // Durchschnittliche Antwortzeit aktualisieren
  const totalRequests = metrics.successfulRequests + metrics.failedRequests;
  metrics.averageResponseTime = 
    (metrics.averageResponseTime * (totalRequests - 1) + responseTime) / totalRequests;
}

// Verwendung
updateAgentStatus(simpleAgent, 'active');
updateConnectionMetrics(simpleConnection, true, 150);

// ============================================================================
// Beispiel 5: Aufgaben-Tracking
// ============================================================================

function addTask(
  agent: AgentWithMCP,
  taskId: string,
  description: string,
  estimatedMinutes?: number
): void {
  if (!agent.activeTasks) {
    agent.activeTasks = [];
  }
  
  agent.activeTasks.push({
    id: taskId,
    description,
    startedAt: new Date(),
    estimatedCompletion: estimatedMinutes 
      ? new Date(Date.now() + estimatedMinutes * 60000)
      : undefined,
  });
  
  agent.status = 'busy';
  agent.lastActivity = new Date();
}

function completeTask(agent: AgentWithMCP, taskId: string, success: boolean): void {
  if (!agent.activeTasks) return;
  
  const taskIndex = agent.activeTasks.findIndex(t => t.id === taskId);
  if (taskIndex === -1) return;
  
  agent.activeTasks.splice(taskIndex, 1);
  
  // Metriken aktualisieren
  agent.metrics.totalRequests++;
  if (success) {
    agent.metrics.successfulRequests++;
  } else {
    agent.metrics.failedRequests++;
  }
  agent.metrics.lastUpdated = new Date();
  
  // Status aktualisieren
  agent.status = agent.activeTasks.length > 0 ? 'busy' : 'active';
  agent.lastActivity = new Date();
}

// Verwendung
addTask(restAgent, 'task-001', 'Security scan of main application', 15);
addTask(restAgent, 'task-002', 'Vulnerability assessment', 30);

// Nach Abschluss
completeTask(restAgent, 'task-001', true);

// ============================================================================
// Beispiel 6: Fehlerbehandlung
// ============================================================================

function handleConnectionError(
  connection: MCPConnection,
  errorMessage: string,
  errorCode?: string
): void {
  connection.status = 'error';
  connection.error = {
    message: errorMessage,
    code: errorCode,
    timestamp: new Date(),
  };
  
  connection.metrics.failedRequests++;
  connection.metrics.reconnectionAttempts++;
  
  console.error(`Connection error: ${errorMessage}`);
}

function addAgentError(
  agent: AgentWithMCP,
  errorMessage: string,
  context?: string
): void {
  if (!agent.errorHistory) {
    agent.errorHistory = [];
  }
  
  agent.errorHistory.unshift({
    timestamp: new Date(),
    message: errorMessage,
    context,
  });
  
  // Nur die letzten 10 Fehler behalten
  if (agent.errorHistory.length > 10) {
    agent.errorHistory = agent.errorHistory.slice(0, 10);
  }
  
  agent.status = 'error';
}

// Verwendung
handleConnectionError(
  oauthConnection,
  'OAuth token expired',
  'AUTH_TOKEN_EXPIRED'
);

addAgentError(
  enterpriseAgent,
  'Failed to generate report',
  'Timeout while waiting for CompText response'
);

// ============================================================================
// Beispiel 7: Wiederverbindung
// ============================================================================

async function reconnectAgent(agent: AgentWithMCP): Promise<boolean> {
  const connection = agent.mcpConnection;
  
  if (connection.metrics.reconnectionAttempts >= (connection.config.maxReconnectAttempts || 3)) {
    console.error('Max reconnection attempts reached');
    connection.status = 'error';
    return false;
  }
  
  connection.status = 'reconnecting';
  connection.metrics.reconnectionAttempts++;
  
  try {
    // Simuliere Wiederverbindung (in der Praxis würde hier die echte Verbindung aufgebaut)
    await new Promise(resolve => 
      setTimeout(resolve, connection.config.reconnectDelay || 5000)
    );
    
    connection.status = 'connected';
    connection.lastConnected = new Date();
    connection.lastActivity = new Date();
    connection.metrics.reconnectionAttempts = 0; // Reset bei erfolgreicher Verbindung
    
    agent.status = 'active';
    
    console.log('Reconnection successful');
    return true;
  } catch (error) {
    handleConnectionError(
      connection,
      `Reconnection failed: ${error}`,
      'RECONNECT_FAILED'
    );
    return false;
  }
}

// ============================================================================
// Beispiel 8: Agent-Monitoring Dashboard
// ============================================================================

interface AgentDashboard {
  agents: AgentWithMCP[];
  totalRequests: number;
  successRate: number;
  averageResponseTime: number;
  activeAgents: number;
  connectedAgents: number;
}

function createDashboard(agents: AgentWithMCP[]): AgentDashboard {
  const totalRequests = agents.reduce((sum, a) => sum + a.metrics.totalRequests, 0);
  const successfulRequests = agents.reduce((sum, a) => sum + a.metrics.successfulRequests, 0);
  const successRate = totalRequests > 0 ? (successfulRequests / totalRequests) * 100 : 0;
  
  const avgResponseTimes = agents.map(a => a.mcpConnection.metrics.averageResponseTime);
  const averageResponseTime = avgResponseTimes.reduce((sum, t) => sum + t, 0) / agents.length;
  
  const activeAgents = agents.filter(isAgentActive).length;
  const connectedAgents = agents.filter(isAgentConnected).length;
  
  return {
    agents,
    totalRequests,
    successRate,
    averageResponseTime,
    activeAgents,
    connectedAgents,
  };
}

// Verwendung
const allAgents = [simpleAgent, restAgent, enterpriseAgent];
const dashboard = createDashboard(allAgents);

console.log('=== Agent Dashboard ===');
console.log(`Total Agents: ${dashboard.agents.length}`);
console.log(`Active Agents: ${dashboard.activeAgents}`);
console.log(`Connected Agents: ${dashboard.connectedAgents}`);
console.log(`Total Requests: ${dashboard.totalRequests}`);
console.log(`Success Rate: ${dashboard.successRate.toFixed(2)}%`);
console.log(`Avg Response Time: ${dashboard.averageResponseTime.toFixed(2)}ms`);

// ============================================================================
// Beispiel 9: Batch-Operationen
// ============================================================================

async function disconnectAllAgents(agents: AgentWithMCP[]): Promise<void> {
  for (const agent of agents) {
    agent.status = 'disconnected';
    agent.mcpConnection.status = 'disconnected';
    agent.updatedAt = new Date();
  }
  console.log(`Disconnected ${agents.length} agents`);
}

async function healthCheckAll(agents: AgentWithMCP[]): Promise<Map<string, boolean>> {
  const results = new Map<string, boolean>();
  
  for (const agent of agents) {
    const isHealthy = isAgentConnected(agent) && agent.status !== 'error';
    results.set(agent.id, isHealthy);
  }
  
  return results;
}

// ============================================================================
// Export für Tests
// ============================================================================

export {
  simpleAgent,
  restAgent,
  enterpriseAgent,
  updateAgentStatus,
  updateConnectionMetrics,
  addTask,
  completeTask,
  handleConnectionError,
  addAgentError,
  reconnectAgent,
  createDashboard,
  disconnectAllAgents,
  healthCheckAll,
};
