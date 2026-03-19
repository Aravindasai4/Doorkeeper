/**
 * DoorKeeper Frontend - Standalone Demo
 * No backend required - all validation and scanning is client-side
 */

function doorkeeper() {
  return {
    // State
    configJson: '',
    jsonStatus: { valid: false, error: '' },
    schemaStatus: { valid: false, error: '' },
    scanning: false,
    currentResult: null,
    recentScans: [],
    saveToRecent: true,
    toasts: [],
    isDarkMode: false,
    showRawJson: false,
    uploadedFileName: '',
    findingsFilter: 'all',

    // Computed
    get canRunScan() {
      return this.jsonStatus.valid && this.schemaStatus.valid && !this.scanning;
    },

    // Computed
    get filteredFindings() {
      if (!this.currentResult || !this.currentResult.findings) return [];
      if (this.findingsFilter === 'all') return this.currentResult.findings;
      return this.currentResult.findings.filter(f => f.severity === this.findingsFilter);
    },

    // Initialization
    init() {
      this.loadRecentScans();
      this.loadSampleConfig();
      this.loadThemePreference();
      console.log('🚪 DoorKeeper Frontend Loaded (Standalone Mode)');
    },

    // Theme toggle
    toggleTheme() {
      this.isDarkMode = !this.isDarkMode;
      localStorage.setItem('darkMode', this.isDarkMode);
    },

    loadThemePreference() {
      const saved = localStorage.getItem('darkMode');
      this.isDarkMode = saved === 'true';
    },

    // JSON Validation
    validateJson() {
      if (!this.configJson.trim()) {
        this.jsonStatus = { valid: false, error: '' };
        this.schemaStatus = { valid: false, error: '' };
        return;
      }

      try {
        const parsed = JSON.parse(this.configJson);
        this.jsonStatus = { valid: true, error: '', data: parsed };
        
        // Validate schema
        const validation = ConfigSchema.validate(parsed);
        if (validation.valid) {
          this.schemaStatus = { valid: true, error: '' };
        } else {
          this.schemaStatus = { 
            valid: false, 
            error: validation.errors.join('; ') 
          };
        }
      } catch (error) {
        this.jsonStatus = { 
          valid: false, 
          error: error.message 
        };
        this.schemaStatus = { valid: false, error: '' };
      }
    },

    // Format JSON
    formatJson() {
      if (!this.jsonStatus.valid) {
        this.showToast('Invalid JSON - cannot format', 'error');
        return;
      }

      try {
        const parsed = JSON.parse(this.configJson);
        this.configJson = JSON.stringify(parsed, null, 2);
        this.showToast('JSON formatted', 'success');
      } catch (error) {
        this.showToast('Format failed: ' + error.message, 'error');
      }
    },

    // Load sample config
    loadSampleConfig() {
      const sample = {
        target: "https://example.com",
        checks: {
          ports: [80, 443],
          httpSecurityHeaders: true,
          robotsTxt: true
        },
        tags: ["demo", "webapp"],
        note: "Sandbox run"
      };
      this.configJson = JSON.stringify(sample, null, 2);
      this.validateJson();
    },

    // Load test preset
    loadPreset(presetName) {
      if (!TEST_CONFIGS[presetName]) {
        this.showToast('Preset not found', 'error');
        return;
      }
      this.configJson = JSON.stringify(TEST_CONFIGS[presetName], null, 2);
      this.validateJson();
      this.showToast(`Loaded preset: ${presetName}`, 'info');
    },

    // Run scan
    async runScan() {
      if (!this.canRunScan) {
        if (!this.jsonStatus.valid) {
          this.showToast('Invalid JSON', 'error');
        } else {
          this.showToast('Schema error: ' + this.schemaStatus.error, 'error');
        }
        return;
      }

      try {
        this.scanning = true;
        const config = JSON.parse(this.configJson);
        
        // Run mock scan
        const result = await runMockScan(config);
        this.currentResult = result;
        
        // Save to recent if enabled
        if (this.saveToRecent) {
          ScanStorage.save(result);
          this.loadRecentScans();
          this.showToast('Saved to Recent', 'success');
        }

        // Scroll to results
        setTimeout(() => {
          const resultsSection = document.querySelector('.results-section');
          if (resultsSection) {
            resultsSection.scrollIntoView({ behavior: 'smooth' });
          }
        }, 100);

      } catch (error) {
        console.error('Scan failed:', error);
        this.showToast('Scan failed: ' + error.message, 'error');
      } finally {
        this.scanning = false;
      }
    },

    // Recent scans management
    loadRecentScans() {
      this.recentScans = ScanStorage.load();
    },

    viewScan(scanId) {
      const scan = ScanStorage.get(scanId);
      if (scan) {
        this.currentResult = scan;
        setTimeout(() => {
          const resultsSection = document.querySelector('.results-section');
          if (resultsSection) {
            resultsSection.scrollIntoView({ behavior: 'smooth' });
          }
        }, 100);
      }
    },

    rerunScan(scanId) {
      const scan = ScanStorage.get(scanId);
      if (scan) {
        // Use the original config if available, otherwise reconstruct
        const config = scan.originalConfig || {
          target: scan.target,
          ...scan.meta
        };
        this.configJson = JSON.stringify(config, null, 2);
        this.validateJson();
        this.runScan();
      }
    },

    deleteScan(scanId) {
      if (ScanStorage.delete(scanId)) {
        this.loadRecentScans();
        this.showToast('Deleted', 'success');
        
        // Clear current result if it was the deleted scan
        if (this.currentResult?.id === scanId) {
          this.currentResult = null;
        }
      } else {
        this.showToast('Delete failed', 'error');
      }
    },

    // Copy report to clipboard
    copyReport() {
      if (!this.currentResult) return;
      
      const reportJson = JSON.stringify(this.currentResult, null, 2);
      navigator.clipboard.writeText(reportJson).then(() => {
        this.showToast('Report copied to clipboard', 'success');
      }).catch(() => {
        this.showToast('Failed to copy', 'error');
      });
    },

    // Toast notifications
    showToast(message, type = 'info') {
      const id = Date.now() + Math.random();
      const toast = { id, message, type, visible: true };
      this.toasts.push(toast);

      // Auto-remove after 3 seconds
      setTimeout(() => {
        const index = this.toasts.findIndex(t => t.id === id);
        if (index > -1) {
          this.toasts[index].visible = false;
          setTimeout(() => {
            this.toasts = this.toasts.filter(t => t.id !== id);
          }, 300);
        }
      }, 3000);
    },

    // Keyboard shortcuts
    handleKeyboard(event) {
      const isMac = navigator.platform.toUpperCase().indexOf('MAC') >= 0;
      const modifier = isMac ? event.metaKey : event.ctrlKey;

      // Ctrl/Cmd + Enter: Run Scan
      if (modifier && event.key === 'Enter') {
        event.preventDefault();
        if (this.canRunScan) {
          this.runScan();
        }
      }

      // Ctrl/Cmd + Shift + F: Format JSON
      if (modifier && event.shiftKey && event.key === 'F') {
        event.preventDefault();
        this.formatJson();
      }
    },

    // File upload handlers
    handleFileSelect(event) {
      const file = event.target.files[0];
      if (file && file.type === 'application/json') {
        this.uploadedFileName = file.name;
        const reader = new FileReader();
        reader.onload = (e) => {
          this.configJson = e.target.result;
          this.validateJson();
          this.showToast('Configuration loaded', 'success');
        };
        reader.readAsText(file);
      } else {
        this.showToast('Please select a valid JSON file', 'error');
      }
    },

    handleFileDrop(event) {
      const file = event.dataTransfer.files[0];
      if (file && file.type === 'application/json') {
        this.uploadedFileName = file.name;
        const reader = new FileReader();
        reader.onload = (e) => {
          this.configJson = e.target.result;
          this.validateJson();
          this.showToast('Configuration loaded', 'success');
        };
        reader.readAsText(file);
      } else {
        this.showToast('Please drop a valid JSON file', 'error');
      }
    },

    // Utility functions
    truncate(str, maxLen) {
      if (!str) return '';
      return str.length > maxLen ? str.substring(0, maxLen) + '…' : str;
    },

    formatDate(isoString) {
      if (!isoString) return '';
      const date = new Date(isoString);
      return date.toLocaleString(undefined, { 
        month: 'short', 
        day: 'numeric', 
        hour: '2-digit', 
        minute: '2-digit' 
      });
    }
  };
}
