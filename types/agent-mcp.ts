/**
 * TypeScript Interface für Agent mit CompText MCP Integration
 * 
 * Dieses Interface definiert die Struktur eines Objekts, das einen Agenten
 * mit einer Verbindung zum CompText MCP Server kombiniert.
 */

/**
 * Status-Typen für den Agenten
 */
export type AgentStatus = 
  | 'idle'           // Bereit, aber nicht aktiv
  | 'active'         // Aktiv und verarbeitet Anfragen
  | 'busy'           // Beschäftigt mit einer Aufgabe
  | 'error'          // Fehlerzustand
  | 'disconnected'   // Nicht verbunden
  | 'suspended';     // Pausiert

/**
 * Status-Typen für die MCP-Verbindung
 */
export type MCPConnectionStatus =
  | 'connected'      // Erfolgreich verbunden
  | 'connecting'     // Verbindungsaufbau läuft
  | 'disconnected'   // Nicht verbunden
  | 'error'          // Verbindungsfehler
  | 'reconnecting'   // Wiederverbindung läuft
  | 'timeout';       // Zeitüberschreitung

/**
 * Authentifizierungs-Typen für MCP-Verbindungen
 */
export type MCPAuthType =
  | 'none'           // Keine Authentifizierung
  | 'api_key'        // API-Schlüssel
  | 'oauth'          // OAuth 2.0
  | 'basic'          // Basic Auth (Benutzername/Passwort)
  | 'token';         // Bearer Token

/**
 * Transport-Typen für MCP-Verbindungen
 */
export type MCPTransportType =
  | 'stdio'          // Standard Input/Output
  | 'http'           // HTTP/REST API
  | 'websocket'      // WebSocket
  | 'grpc';          // gRPC

/**
 * Audience-Profile für CompText
 */
export type ComptextAudience = 'dev' | 'audit' | 'exec';

/**
 * CompText Compiler Modi
 */
export type ComptextMode = 'bundle_only' | 'allow_inline_fallback';

/**
 * Authentifizierungs-Daten für MCP-Verbindungen
 */
export interface MCPAuthData {
  /** Typ der Authentifizierung */
  type: MCPAuthType;
  
  /** API-Schlüssel (wenn type='api_key') */
  apiKey?: string;
  
  /** Benutzername (wenn type='basic') */
  username?: string;
  
  /** Passwort (wenn type='basic') */
  password?: string;
  
  /** Bearer Token (wenn type='token') */
  token?: string;
  
  /** OAuth-Konfiguration (wenn type='oauth') */
  oauth?: {
    clientId: string;
    clientSecret: string;
    refreshToken?: string;
    accessToken?: string;
    tokenExpiry?: Date;
  };
  
  /** Zusätzliche benutzerdefinierte Header */
  customHeaders?: Record<string, string>;
}

/**
 * Verbindungs-Metriken für Monitoring
 */
export interface MCPConnectionMetrics {
  /** Anzahl erfolgreicher Anfragen */
  successfulRequests: number;
  
  /** Anzahl fehlgeschlagener Anfragen */
  failedRequests: number;
  
  /** Durchschnittliche Antwortzeit in Millisekunden */
  averageResponseTime: number;
  
  /** Letzte erfolgreiche Anfrage */
  lastSuccessfulRequest?: Date;
  
  /** Letzter Fehler */
  lastError?: {
    timestamp: Date;
    message: string;
    code?: string;
  };
  
  /** Uptime in Sekunden */
  uptime: number;
  
  /** Anzahl der Wiederverbindungsversuche */
  reconnectionAttempts: number;
}

/**
 * Konfiguration für die MCP-Verbindung
 */
export interface MCPConnectionConfig {
  /** Basis-URL oder Pfad zum MCP-Server */
  url: string;
  
  /** Transport-Typ */
  transport: MCPTransportType;
  
  /** Timeout in Millisekunden */
  timeout?: number;
  
  /** Anzahl der Wiederverbindungsversuche */
  maxReconnectAttempts?: number;
  
  /** Verzögerung zwischen Wiederverbindungsversuchen (ms) */
  reconnectDelay?: number;
  
  /** Heartbeat-Intervall in Millisekunden */
  heartbeatInterval?: number;
  
  /** Aktiviere Request-Logging */
  enableLogging?: boolean;
  
  /** Custom Request Headers */
  headers?: Record<string, string>;
}

/**
 * MCP-Verbindung zum CompText Server
 */
export interface MCPConnection {
  /** Eindeutige ID der Verbindung */
  id: string;
  
  /** Name der Verbindung (beschreibend) */
  name: string;
  
  /** Aktueller Status der Verbindung */
  status: MCPConnectionStatus;
  
  /** Verbindungskonfiguration */
  config: MCPConnectionConfig;
  
  /** Authentifizierungs-Daten */
  auth: MCPAuthData;
  
  /** Zeitstempel der letzten Verbindung */
  lastConnected?: Date;
  
  /** Zeitstempel der letzten Aktivität */
  lastActivity?: Date;
  
  /** Server-Version (CompText MCP Server) */
  serverVersion?: string;
  
  /** Verfügbare MCP-Tools auf dem Server */
  availableTools?: string[];
  
  /** Verbindungs-Metriken */
  metrics: MCPConnectionMetrics;
  
  /** Fehler-Details (falls status='error') */
  error?: {
    message: string;
    code?: string;
    timestamp: Date;
    stackTrace?: string;
  };
  
  /** Zusätzliche Metadaten */
  metadata?: Record<string, unknown>;
}

/**
 * Agent-Konfiguration
 */
export interface AgentConfig {
  /** Name des Agenten */
  name: string;
  
  /** Beschreibung/Zweck des Agenten */
  description?: string;
  
  /** Standard Audience-Profil für CompText */
  defaultAudience: ComptextAudience;
  
  /** Standard Compiler-Modus */
  defaultMode: ComptextMode;
  
  /** Maximale gleichzeitige Anfragen */
  maxConcurrentRequests?: number;
  
  /** Request-Timeout in Millisekunden */
  requestTimeout?: number;
  
  /** Aktiviere automatische Wiederholungen bei Fehlern */
  enableAutoRetry?: boolean;
  
  /** Maximale Anzahl von Wiederholungen */
  maxRetries?: number;
  
  /** Custom Prompts oder Anweisungen */
  customInstructions?: string;
  
  /** Tags zur Kategorisierung */
  tags?: string[];
}

/**
 * Agent-Metriken für Performance-Tracking
 */
export interface AgentMetrics {
  /** Anzahl verarbeiteter Anfragen */
  totalRequests: number;
  
  /** Anzahl erfolgreicher Anfragen */
  successfulRequests: number;
  
  /** Anzahl fehlgeschlagener Anfragen */
  failedRequests: number;
  
  /** Durchschnittliche Verarbeitungszeit (ms) */
  averageProcessingTime: number;
  
  /** Gesamte Token-Ersparnis durch CompText */
  totalTokensSaved?: number;
  
  /** Letzte Aktualisierung der Metriken */
  lastUpdated: Date;
}

/**
 * Haupt-Interface: Agent mit MCP-Verbindung
 * 
 * Kombiniert einen Agenten mit einer Verbindung zum CompText MCP Server.
 * Dieses Interface ermöglicht die vollständige Verwaltung und Überwachung
 * eines Agenten, der mit dem CompText-System interagiert.
 */
export interface AgentWithMCP {
  /** Eindeutige ID des Agenten */
  id: string;
  
  /** Agent-Konfiguration */
  config: AgentConfig;
  
  /** Aktueller Status des Agenten */
  status: AgentStatus;
  
  /** MCP-Verbindung zum CompText Server */
  mcpConnection: MCPConnection;
  
  /** Zeitstempel der Erstellung */
  createdAt: Date;
  
  /** Zeitstempel der letzten Aktualisierung */
  updatedAt: Date;
  
  /** Zeitstempel der letzten Aktivität */
  lastActivity?: Date;
  
  /** Agent-Metriken */
  metrics: AgentMetrics;
  
  /** Aktuelle laufende Aufgaben */
  activeTasks?: Array<{
    id: string;
    description: string;
    startedAt: Date;
    estimatedCompletion?: Date;
  }>;
  
  /** Fehler-Historie (letzte N Fehler) */
  errorHistory?: Array<{
    timestamp: Date;
    message: string;
    context?: string;
  }>;
  
  /** Zusätzliche benutzerdefinierte Eigenschaften */
  customProperties?: Record<string, unknown>;
  
  /** Versionsinformation */
  version?: string;
}

/**
 * Factory-Funktionen und Hilfsfunktionen
 */

/**
 * Erstellt eine Standard-MCP-Verbindung
 */
export const createDefaultMCPConnection = (
  id: string,
  name: string,
  url: string
): MCPConnection => ({
  id,
  name,
  status: 'disconnected',
  config: {
    url,
    transport: 'stdio',
    timeout: 30000,
    maxReconnectAttempts: 3,
    reconnectDelay: 5000,
    heartbeatInterval: 60000,
    enableLogging: true,
  },
  auth: {
    type: 'none',
  },
  metrics: {
    successfulRequests: 0,
    failedRequests: 0,
    averageResponseTime: 0,
    uptime: 0,
    reconnectionAttempts: 0,
  },
});

/**
 * Erstellt eine Standard-Agent-Konfiguration
 */
export const createDefaultAgentConfig = (
  name: string,
  description?: string
): AgentConfig => ({
  name,
  description,
  defaultAudience: 'dev',
  defaultMode: 'bundle_only',
  maxConcurrentRequests: 5,
  requestTimeout: 30000,
  enableAutoRetry: true,
  maxRetries: 3,
  tags: [],
});

/**
 * Erstellt einen neuen Agenten mit MCP-Verbindung
 */
export const createAgentWithMCP = (
  id: string,
  config: AgentConfig,
  mcpConnection: MCPConnection
): AgentWithMCP => ({
  id,
  config,
  status: 'idle',
  mcpConnection,
  createdAt: new Date(),
  updatedAt: new Date(),
  metrics: {
    totalRequests: 0,
    successfulRequests: 0,
    failedRequests: 0,
    averageProcessingTime: 0,
    lastUpdated: new Date(),
  },
  activeTasks: [],
  errorHistory: [],
});

/**
 * Type Guards
 */

/**
 * Prüft, ob der Agent verbunden ist
 */
export const isAgentConnected = (agent: AgentWithMCP): boolean => {
  return agent.mcpConnection.status === 'connected';
};

/**
 * Prüft, ob der Agent aktiv ist
 */
export const isAgentActive = (agent: AgentWithMCP): boolean => {
  return agent.status === 'active' || agent.status === 'busy';
};

/**
 * Prüft, ob die Verbindung einen Fehler hat
 */
export const hasConnectionError = (connection: MCPConnection): boolean => {
  return connection.status === 'error' && connection.error !== undefined;
};
