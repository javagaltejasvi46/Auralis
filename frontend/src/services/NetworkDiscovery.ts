/**
 * Fast Network Discovery Service
 * Uses UDP broadcast and quick IP testing for fast server discovery
 */

interface ServerInfo {
  ip: string;
  port: number;
  available: boolean;
  service?: string;
  version?: string;
}

interface BroadcastMessage {
  service: string;
  version: string;
  ip: string;
  api_port: number;
  ws_port: number;
  timestamp: number;
}

class NetworkDiscoveryService {
  private static instance: NetworkDiscoveryService;
  private discoveredServers: ServerInfo[] = [];
  private currentServerIP: string | null = null;

  static getInstance(): NetworkDiscoveryService {
    if (!NetworkDiscoveryService.instance) {
      NetworkDiscoveryService.instance = new NetworkDiscoveryService();
    }
    return NetworkDiscoveryService.instance;
  }

  /**
   * Test if a server is available at the given IP and port
   */
  private async testServer(ip: string, port: number, timeout: number = 2000): Promise<boolean> {
    try {
      const controller = new AbortController();
      const timeoutId = setTimeout(() => controller.abort(), timeout);

      const response = await fetch(`http://${ip}:${port}/health`, {
        method: 'GET',
        signal: controller.signal,
        headers: {
          'Accept': 'application/json',
        },
      });

      clearTimeout(timeoutId);
      return response.ok;
    } catch (error) {
      return false;
    }
  }

  /**
   * Quick discovery - try most common IPs first (FAST)
   */
  async quickDiscovery(): Promise<string | null> {
    console.log('⚡ Starting quick discovery...');
    
    // Get device's own IP to guess network range
    const deviceIP = await this.getDeviceIP();
    const networkBase = deviceIP ? deviceIP.substring(0, deviceIP.lastIndexOf('.')) : null;
    
    // Build smart IP list based on device's network
    const smartIPs: string[] = [];
    
    if (networkBase) {
      // Try IPs in same network range first
      smartIPs.push(
        `${networkBase}.1`,    // Router
        `${networkBase}.100`,  // Common server IPs
        `${networkBase}.101`,
        `${networkBase}.102`,
        `${networkBase}.10`,
        `${networkBase}.20`,
        `${networkBase}.50`
      );
    }
    
    // Add common network ranges
    const commonIPs = [
      '192.168.1.1', '192.168.1.100', '192.168.1.101',
      '192.168.0.1', '192.168.0.100', '192.168.0.101',
      '10.0.0.1', '10.0.0.100', '10.0.0.101',
      '172.16.0.1', '172.16.0.100',
      'localhost', '127.0.0.1'
    ];
    
    // Combine and deduplicate
    const allIPs = [...new Set([...smartIPs, ...commonIPs])];

    // Test IPs in parallel batches for speed
    const batchSize = 5;
    for (let i = 0; i < allIPs.length; i += batchSize) {
      const batch = allIPs.slice(i, i + batchSize);
      
      const promises = batch.map(async (ip) => {
        const available = await this.testServer(ip, 8002, 1500);
        return { ip, available };
      });
      
      const results = await Promise.all(promises);
      const found = results.find(r => r.available);
      
      if (found) {
        this.currentServerIP = found.ip;
        console.log(`✅ Quick discovery found server: ${found.ip}`);
        return found.ip;
      }
    }

    console.log('⚠️ Quick discovery failed');
    return null;
  }

  /**
   * Get device's IP address (approximate)
   */
  private async getDeviceIP(): Promise<string | null> {
    try {
      // This is a hack to get approximate device IP
      // Create a dummy connection to get local IP
      const pc = new RTCPeerConnection({
        iceServers: [{ urls: 'stun:stun.l.google.com:19302' }]
      });
      
      pc.createDataChannel('');
      const offer = await pc.createOffer();
      await pc.setLocalDescription(offer);
      
      return new Promise((resolve) => {
        pc.onicecandidate = (event) => {
          if (event.candidate) {
            const candidate = event.candidate.candidate;
            const match = candidate.match(/(\d+\.\d+\.\d+\.\d+)/);
            if (match && !match[1].startsWith('127.')) {
              pc.close();
              resolve(match[1]);
            }
          }
        };
        
        // Timeout after 2 seconds
        setTimeout(() => {
          pc.close();
          resolve(null);
        }, 2000);
      });
    } catch (error) {
      console.log('Could not get device IP:', error);
      return null;
    }
  }

  /**
   * Scan QR code for connection info
   */
  parseQRCode(qrData: string): boolean {
    try {
      const connectionInfo = JSON.parse(qrData);
      
      if (connectionInfo.service === 'auralis' && connectionInfo.ip) {
        this.currentServerIP = connectionInfo.ip;
        console.log(`📱 QR Code connection: ${connectionInfo.ip}`);
        return true;
      }
    } catch (error) {
      console.log('Invalid QR code data:', error);
    }
    
    return false;
  }

  /**
   * Get the current server IP (either discovered or manually set)
   */
  getCurrentServerIP(): string | null {
    return this.currentServerIP;
  }

  /**
   * Set the server IP manually
   */
  setServerIP(ip: string): void {
    this.currentServerIP = ip;
    console.log(`🔧 Manually set server IP: ${ip}`);
  }

  /**
   * Get the full API base URL
   */
  getAPIBaseURL(): string {
    const ip = this.currentServerIP || 'localhost';
    return `http://${ip}:8002`;
  }

  /**
   * Get the full WebSocket URL
   */
  getWebSocketURL(): string {
    const ip = this.currentServerIP || 'localhost';
    return `ws://${ip}:8003`;
  }

  /**
   * Test the current configuration
   */
  async testCurrentConfig(): Promise<boolean> {
    if (!this.currentServerIP) {
      return false;
    }
    
    return await this.testServer(this.currentServerIP, 8002);
  }

  /**
   * Full network scan (fallback - slower)
   */
  async fullScan(onProgress?: (progress: number, currentIP: string) => void): Promise<ServerInfo[]> {
    console.log('🔍 Starting full network scan...');
    
    // Only scan most common ranges to keep it reasonable
    const ranges = ['192.168.1', '192.168.0', '10.0.0'];
    const servers: ServerInfo[] = [];
    let totalIPs = 0;
    let scannedIPs = 0;
    
    // Count total IPs to scan (only 1-20 for speed)
    ranges.forEach(() => totalIPs += 20);
    
    for (const range of ranges) {
      const promises: Promise<{ ip: string; available: boolean }>[] = [];
      
      // Only scan first 20 IPs in each range for speed
      for (let i = 1; i <= 20; i++) {
        const ip = `${range}.${i}`;
        promises.push(
          this.testServer(ip, 8002, 1000).then(available => ({ ip, available }))
        );
      }
      
      const results = await Promise.all(promises);
      scannedIPs += 20;
      
      if (onProgress) {
        onProgress(Math.round((scannedIPs / totalIPs) * 100), range);
      }
      
      const availableServers = results
        .filter(r => r.available)
        .map(r => ({ ip: r.ip, port: 8002, available: true }));
      
      servers.push(...availableServers);
      
      // Stop if we found servers
      if (availableServers.length > 0) {
        this.currentServerIP = availableServers[0].ip;
        console.log(`✅ Full scan found server: ${this.currentServerIP}`);
        break;
      }
    }
    
    return servers;
  }
}

export default NetworkDiscoveryService;