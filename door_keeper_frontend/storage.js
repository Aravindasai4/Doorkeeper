/**
 * localStorage management for recent scans
 */

const STORAGE_KEY = 'doorkeeper_recent_scans';
const MAX_SCANS = 10;

const ScanStorage = {
  // Load all recent scans
  load() {
    try {
      const data = localStorage.getItem(STORAGE_KEY);
      return data ? JSON.parse(data) : [];
    } catch (error) {
      console.error('Failed to load scans from localStorage:', error);
      return [];
    }
  },

  // Save a new scan
  save(scanResult) {
    try {
      const scans = this.load();
      
      // Add to beginning
      scans.unshift(scanResult);
      
      // Keep only last MAX_SCANS
      const trimmed = scans.slice(0, MAX_SCANS);
      
      localStorage.setItem(STORAGE_KEY, JSON.stringify(trimmed));
      return true;
    } catch (error) {
      console.error('Failed to save scan to localStorage:', error);
      return false;
    }
  },

  // Get a specific scan by ID
  get(scanId) {
    const scans = this.load();
    return scans.find(s => s.id === scanId);
  },

  // Delete a scan by ID
  delete(scanId) {
    try {
      const scans = this.load();
      const filtered = scans.filter(s => s.id !== scanId);
      localStorage.setItem(STORAGE_KEY, JSON.stringify(filtered));
      return true;
    } catch (error) {
      console.error('Failed to delete scan:', error);
      return false;
    }
  },

  // Clear all scans
  clear() {
    try {
      localStorage.removeItem(STORAGE_KEY);
      return true;
    } catch (error) {
      console.error('Failed to clear scans:', error);
      return false;
    }
  }
};
