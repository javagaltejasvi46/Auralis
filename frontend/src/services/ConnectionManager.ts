/**
 * Connection Manager
 * Manages API connections with automatic server discovery and fallback
 */

import NetworkDiscoveryService from './NetworkDiscovery';
import { API_BASE_URL, WS_BASE_URL } from '../config';

interface ConnectionState {
  isConnected: boolean;
  serverIP: string | null;
  lastChecked: Date | null;
  error: string | null;
}

class ConnectionManager {
  private static instance: ConnectionManager;
  private networkDiscovery: NetworkDiscoveryService;
  private connectionState: ConnectionState = {
    isConnected: false,
    serverIP: null,
    lastChecked: null,
    error: null,
  };
  private listeners: ((state: ConnectionState) => void)[] = [];

  static getInstance(): ConnectionManager {
    if (!ConnectionManager.instance) {
      ConnectionManager.instance = new ConnectionManager();
    }
    return ConnectionManager.instance;
  }

  constructor() {
    this.networkDiscovery = NetworkDiscoveryService.getInstance();
  }

  /**
   * Initialize connection - try multiple methods (FAST)
   */
  async initialize(): Promise<boolean> {
    console.log('🚀 Initializing connection manager...');

    // Method 1: Try the configured IP first (if valid)
    const configuredIP = this.extractIPFromURL(API_BASE_URL);
    if (configuredIP && configuredIP !== 'localhost' && !configuredIP.startsWith('10.157')) {
      console.log(`🔧 Trying configured IP: ${configuredIP}`);
      this.networkDiscovery.setServerIP(configuredIP);
      
      if (await this.testConnection()) {
        return true;
      }
    }

    // Method 2: Quick discovery (FAST - only tests common IPs)
    console.log('⚡ Quick discovery (5 seconds max)...');
    const quickIP = await this.networkDiscovery.quickDiscovery();
    if (quickIP && await this.testConnection()) {
      return true;
    }

    // Method 3: Show manual connection option immediately
    this.updateConnectionState({
      isConnected: false,
      serverIP: null,
      lastChecked: new Date(),
      error: 'Server not found. Please connect manually or scan QR code.',
    });

    return false;
  }

  /**
   * Full scan (only when user explicitly requests it)
   */
  async fullScan(onProgress?: (progress: number, currentIP: string) => void): Promise<boolean> {
    console.log('🔍 Starting full network scan...');
    
    this.updateConnectionState({
      isConnected: false,
      serverIP: null,
      lastChecked: new Date(),
      error: 'Scanning network...',
    });

    const servers = await this.networkDiscovery.fullScan(onProgress);

    if (servers.length > 0) {
      return await this.testConnection();
    }

    this.updateConnectionState({
      isConnected: false,
      serverIP: null,
      lastChecked: new Date(),
      error: 'No server found. Please connect manually.',
    });

    return false;
  }

  /**
   * Test the current connection
   */
  async testConnection(): Promise<boolean> {
    try {
      const baseURL = this.networkDiscovery.getAPIBaseURL();
      console.log(`🧪 Testing connection to: ${baseURL}`);

      const response = await fetch(`${baseURL}/health`, {
        method: 'GET',
        timeout: 5000,
      });

      if (response.ok) {
        const serverIP = this.networkDiscovery.getCurrentServerIP();
        this.updateConnectionState({
          isConnected: true,
          serverIP,
          lastChecked: new Date(),
          error: null,
        });
        console.log(`✅ Connected to Auralis server: ${serverIP}`);
        return true;
      }
    } catch (error) {
      console.log(`❌ Connection test failed: ${error}`);
    }

    this.updateConnectionState({
      isConnected: false,
      serverIP: this.networkDiscovery.getCurrentServerIP(),
      lastChecked: new Date(),
      error: 'Server not responding',
    });

    return false;
  }

  /**
   * Get the current API base URL
   */
  getAPIBaseURL(): string {
    return this.networkDiscovery.getAPIBaseURL();
  }

  /**
   * Get the current WebSocket URL
   */
  getWebSocketURL(): string {
    return this.networkDiscovery.getWebSocketURL();
  }

  /**
   * Get connection state
   */
  getConnectionState(): ConnectionState {
    return { ...this.connectionState };
  }

  /**
   * Add connection state listener
   */
  addListener(listener: (state: ConnectionState) => void): void {
    this.listeners.push(listener);
  }

  /**
   * Remove connection state listener
   */
  removeListener(listener: (state: ConnectionState) => void): void {
    const index = this.listeners.indexOf(listener);
    if (index > -1) {
      this.listeners.splice(index, 1);
    }
  }

  /**
   * Manually set server IP
   */
  async setServerIP(ip: string): Promise<boolean> {
    console.log(`🔧 Manually setting server IP: ${ip}`);
    this.networkDiscovery.setServerIP(ip);
    return await this.testConnection();
  }

  /**
   * Retry connection
   */
  async retry(): Promise<boolean> {
    console.log('🔄 Retrying connection...');
    return await this.initialize();
  }

  /**
   * Extract IP from URL
   */
  private extractIPFromURL(url: string): string | null {
    try {
      const match = url.match(/\/\/([^:]+):/);
      return match ? match[1] : null;
    } catch {
      return null;
    }
  }

  /**
   * Update connection state and notify listeners
   */
  private updateConnectionState(newState: Partial<ConnectionState>): void {
    this.connectionState = { ...this.connectionState, ...newState };
    this.listeners.forEach(listener => listener(this.connectionState));
  }
}

export default ConnectionManager;