# TypeScript Interfaces für CompText MCP Integration

## Übersicht

Dieses Verzeichnis enthält TypeScript-Interfaces für die Integration von Agenten mit dem CompText MCP Server. Die Interfaces ermöglichen eine typsichere und flexible Verwaltung von Agenten und ihren MCP-Verbindungen.

## Dateien

- **`agent-mcp.ts`** - Haupt-Interface-Definitionen
- **`agent-mcp.example.ts`** - Umfassende Verwendungsbeispiele
- **`README.md`** - Diese Dokumentation

## Hauptkomponenten

### 1. AgentWithMCP

Das zentrale Interface, das einen Agenten mit einer MCP-Verbindung kombiniert.

```typescript
interface AgentWithMCP {
  id: string;
  config: AgentConfig;
  status: AgentStatus;
  mcpConnection: MCPConnection;
  createdAt: Date;
  updatedAt: Date;
  metrics: AgentMetrics;
  // ... weitere Eigenschaften
}
```

### 2. MCPConnection

Definiert die Verbindung zum CompText MCP Server.

```typescript
interface MCPConnection {
  id: string;
  name: string;
  status: MCPConnectionStatus;
  config: MCPConnectionConfig;
  auth: MCPAuthData;
  metrics: MCPConnectionMetrics;
  // ... weitere Eigenschaften
}
```

### 3. AgentConfig

Konfiguration für Agent-Verhalten und Einstellungen.

```typescript
interface AgentConfig {
  name: string;
  description?: string;
  defaultAudience: ComptextAudience;  // 'dev' | 'audit' | 'exec'
  defaultMode: ComptextMode;          // 'bundle_only' | 'allow_inline_fallback'
  maxConcurrentRequests?: number;
  // ... weitere Eigenschaften
}
```

## Unterstützte Funktionen

### Status-Typen

#### AgentStatus
- `idle` - Bereit, aber nicht aktiv
- `active` - Aktiv und verarbeitet Anfragen
- `busy` - Beschäftigt mit einer Aufgabe
- `error` - Fehlerzustand
- `disconnected` - Nicht verbunden
- `suspended` - Pausiert

#### MCPConnectionStatus
- `connected` - Erfolgreich verbunden
- `connecting` - Verbindungsaufbau läuft
- `disconnected` - Nicht verbunden
- `error` - Verbindungsfehler
- `reconnecting` - Wiederverbindung läuft
- `timeout` - Zeitüberschreitung

### Authentifizierungs-Typen

Das Interface unterstützt verschiedene Authentifizierungsmethoden:

- **`none`** - Keine Authentifizierung (lokal)
- **`api_key`** - API-Schlüssel basierte Auth
- **`oauth`** - OAuth 2.0
- **`basic`** - Basic Authentication
- **`token`** - Bearer Token

### Transport-Typen

Verschiedene Transport-Mechanismen für MCP-Verbindungen:

- **`stdio`** - Standard Input/Output (lokal)
- **`http`** - HTTP/REST API
- **`websocket`** - WebSocket-Verbindung
- **`grpc`** - gRPC

## Verwendungsbeispiele

### Einfacher Agent erstellen

```typescript
import {
  createDefaultMCPConnection,
  createDefaultAgentConfig,
  createAgentWithMCP,
} from './agent-mcp';

// 1. MCP-Verbindung erstellen
const connection = createDefaultMCPConnection(
  'mcp-001',
  'Local Server',
  'python -m comptext_mcp.server'
);

// 2. Agent-Konfiguration erstellen
const config = createDefaultAgentConfig(
  'Code Review Agent',
  'Automatisierter Code-Review Agent'
);

// 3. Agent erstellen
const agent = createAgentWithMCP('agent-001', config, connection);
```

### Agent mit API-Verbindung

```typescript
const apiConnection: MCPConnection = {
  id: 'mcp-api-001',
  name: 'Remote API',
  status: 'disconnected',
  config: {
    url: 'https://api.comptext.example.com',
    transport: 'http',
    timeout: 60000,
  },
  auth: {
    type: 'api_key',
    apiKey: process.env.API_KEY,
  },
  metrics: {
    successfulRequests: 0,
    failedRequests: 0,
    averageResponseTime: 0,
    uptime: 0,
    reconnectionAttempts: 0,
  },
};
```

### Status-Management

```typescript
import { isAgentConnected, isAgentActive } from './agent-mcp';

if (isAgentConnected(agent)) {
  console.log('Agent ist verbunden');
}

if (isAgentActive(agent)) {
  console.log('Agent ist aktiv');
}
```

### Metriken aktualisieren

```typescript
function updateMetrics(agent: AgentWithMCP, success: boolean, time: number) {
  agent.metrics.totalRequests++;
  
  if (success) {
    agent.metrics.successfulRequests++;
  } else {
    agent.metrics.failedRequests++;
  }
  
  // Durchschnittliche Verarbeitungszeit aktualisieren
  const total = agent.metrics.totalRequests;
  agent.metrics.averageProcessingTime = 
    (agent.metrics.averageProcessingTime * (total - 1) + time) / total;
  
  agent.metrics.lastUpdated = new Date();
}
```

### Aufgaben-Tracking

```typescript
// Aufgabe hinzufügen
agent.activeTasks = agent.activeTasks || [];
agent.activeTasks.push({
  id: 'task-001',
  description: 'Security Scan',
  startedAt: new Date(),
  estimatedCompletion: new Date(Date.now() + 30 * 60000), // 30 Minuten
});

agent.status = 'busy';

// Aufgabe abschließen
const taskIndex = agent.activeTasks.findIndex(t => t.id === 'task-001');
if (taskIndex !== -1) {
  agent.activeTasks.splice(taskIndex, 1);
  agent.status = agent.activeTasks.length > 0 ? 'busy' : 'active';
}
```

### Fehlerbehandlung

```typescript
function handleError(agent: AgentWithMCP, error: string, context?: string) {
  agent.errorHistory = agent.errorHistory || [];
  agent.errorHistory.unshift({
    timestamp: new Date(),
    message: error,
    context,
  });
  
  // Nur die letzten 10 Fehler behalten
  if (agent.errorHistory.length > 10) {
    agent.errorHistory = agent.errorHistory.slice(0, 10);
  }
  
  agent.status = 'error';
  agent.updatedAt = new Date();
}
```

## CompText-spezifische Features

### Audience-Profile

Das Interface unterstützt die drei Audience-Profile von CompText:

- **`dev`** - Entwickler-Modus (detailliert, technisch)
- **`audit`** - Audit-Modus (Compliance, Security)
- **`exec`** - Executive-Modus (High-Level, Business-fokussiert)

```typescript
const agentConfig: AgentConfig = {
  name: 'Security Agent',
  defaultAudience: 'audit',  // Audit-fokussiert
  defaultMode: 'bundle_only',
  // ...
};
```

### Compiler-Modi

- **`bundle_only`** - Nur Bundle-basierte Commands (Standard)
- **`allow_inline_fallback`** - Erlaubt Inline-Commands als Fallback

```typescript
const agentConfig: AgentConfig = {
  name: 'Dev Agent',
  defaultMode: 'bundle_only',  // Strikt Bundle-basiert
  // ...
};
```

## Best Practices

### 1. Immer Type Guards verwenden

```typescript
if (isAgentConnected(agent) && isAgentActive(agent)) {
  // Sicher zu verwenden
  processRequest(agent);
}
```

### 2. Metriken regelmäßig aktualisieren

```typescript
// Nach jeder Operation
updateMetrics(agent, success, responseTime);
agent.updatedAt = new Date();
agent.lastActivity = new Date();
```

### 3. Fehler-Historie pflegen

```typescript
// Fehler protokollieren
handleError(agent, 'Connection timeout', 'Retry attempt 3/5');

// Fehler-Historie begrenzen (max 10 Einträge)
if (agent.errorHistory.length > 10) {
  agent.errorHistory = agent.errorHistory.slice(0, 10);
}
```

### 4. Wiederverbindungs-Logik implementieren

```typescript
async function reconnect(connection: MCPConnection): Promise<boolean> {
  if (connection.metrics.reconnectionAttempts >= 
      (connection.config.maxReconnectAttempts || 3)) {
    return false;
  }
  
  connection.status = 'reconnecting';
  connection.metrics.reconnectionAttempts++;
  
  try {
    // Verbindungsaufbau
    await connectToMCP(connection);
    
    connection.status = 'connected';
    connection.lastConnected = new Date();
    connection.metrics.reconnectionAttempts = 0;
    return true;
  } catch (error) {
    connection.status = 'error';
    return false;
  }
}
```

### 5. Monitoring-Dashboard erstellen

```typescript
function createDashboard(agents: AgentWithMCP[]) {
  return {
    totalAgents: agents.length,
    activeAgents: agents.filter(isAgentActive).length,
    connectedAgents: agents.filter(isAgentConnected).length,
    totalRequests: agents.reduce((sum, a) => sum + a.metrics.totalRequests, 0),
    successRate: calculateSuccessRate(agents),
  };
}
```

## Integration mit CompText MCP Server

### Verfügbare Tools abfragen

```typescript
// Nach erfolgreicher Verbindung
agent.mcpConnection.availableTools = [
  'list_modules',
  'get_module',
  'get_command',
  'search',
  'get_by_tag',
  'get_by_type',
  'get_statistics',
  'nl_to_comptext',
];
```

### Server-Version tracken

```typescript
agent.mcpConnection.serverVersion = '1.0.0';
```

## Erweiterbarkeit

Das Interface ist bewusst flexibel gestaltet und unterstützt Custom Properties:

```typescript
// Custom Agent Properties
agent.customProperties = {
  team: 'security',
  region: 'eu-west-1',
  costCenter: 'SEC-001',
};

// Custom Connection Metadata
agent.mcpConnection.metadata = {
  datacenter: 'Frankfurt',
  environment: 'production',
};
```

## TypeScript-Konfiguration

Für optimale Nutzung empfohlen:

```json
{
  "compilerOptions": {
    "strict": true,
    "strictNullChecks": true,
    "noImplicitAny": true,
    "esModuleInterop": true,
    "target": "ES2020",
    "module": "commonjs"
  }
}
```

## Weitere Ressourcen

- [CompText MCP Server Documentation](../README.md)
- [MCP Protocol Specification](https://modelcontextprotocol.io)
- [Beispiele](./agent-mcp.example.ts)

## Lizenz

MIT License - siehe [LICENSE](../LICENSE)
