/**
 * Mock scan engine - deterministic results based on input
 */

// Simple hash function for deterministic ID generation
function simpleHash(str) {
  let hash = 0;
  for (let i = 0; i < str.length; i++) {
    const char = str.charCodeAt(i);
    hash = ((hash << 5) - hash) + char;
    hash = hash & hash;
  }
  return Math.abs(hash).toString(36);
}

function generateScanId(config) {
  const configStr = JSON.stringify(config);
  const hash = simpleHash(configStr);
  return 'scan-' + hash;
}

function generateTimestamp(config) {
  const configStr = JSON.stringify(config);
  const hash = simpleHash(configStr);
  const baseTime = 1700000000000;
  const offset = (hash.charCodeAt(0) || 0) * 100000;
  return new Date(baseTime + offset).toISOString();
}

async function runMockScan(config) {
  // Simulate network delay (deterministic based on target length)
  const delay = 1500 + (config.target ? (config.target.length % 5) * 100 : 0);
  await new Promise(resolve => setTimeout(resolve, delay));

  const findings = [];
  const target = config.target || '';
  const checks = config.checks || {};
  const ports = checks.ports || [];
  const httpSecurityHeaders = checks.httpSecurityHeaders !== false; // default true
  const robotsTxt = checks.robotsTxt || false;

  // Rule 1: HTTPS enforcement
  if (ports.includes(80) && !ports.includes(443)) {
    findings.push({
      id: 'find-https-enforcement',
      check: 'port',
      title: 'HTTPS not enforced',
      severity: 'high',
      detail: 'Port 80 (HTTP) is open but port 443 (HTTPS) is not configured',
      recommendation: 'Enable HTTPS on port 443 and redirect all HTTP traffic to HTTPS'
    });
  }

  // Rule 2: Only HTTP (no HTTPS at all)
  if (target.startsWith('http://') && !target.startsWith('https://')) {
    findings.push({
      id: 'find-http-protocol',
      check: 'port',
      title: 'Site uses HTTP instead of HTTPS',
      severity: 'high',
      detail: 'The target URL uses unencrypted HTTP protocol',
      recommendation: 'Migrate to HTTPS and obtain a valid SSL/TLS certificate'
    });
  }

  // Rule 3: Security headers checks (deterministic based on target and ports)
  if (httpSecurityHeaders) {
    const headerIssues = [
      {
        title: 'Missing Content-Security-Policy',
        detail: 'No Content-Security-Policy header detected',
        recommendation: 'Add CSP header to prevent XSS attacks: "Content-Security-Policy: default-src \'self\'"'
      },
      {
        title: 'Missing Strict-Transport-Security',
        detail: 'HSTS header not configured',
        recommendation: 'Add HSTS header: "Strict-Transport-Security: max-age=31536000; includeSubDomains"'
      },
      {
        title: 'Missing X-Frame-Options',
        detail: 'X-Frame-Options header not set',
        recommendation: 'Add X-Frame-Options header to prevent clickjacking: "X-Frame-Options: DENY"'
      }
    ];

    // Deterministic: number of header issues based on target length and port count
    const targetLen = (target || '').length;
    const portCount = ports.length;
    const numIssues = Math.min(3, Math.max(1, (targetLen + portCount) % 3 + 1));
    
    for (let i = 0; i < numIssues; i++) {
      const issue = headerIssues[i];
      findings.push({
        id: 'find-header-' + i,
        check: 'header',
        title: issue.title,
        severity: 'medium',
        detail: issue.detail,
        recommendation: issue.recommendation
      });
    }
  }

  // Rule 4: Robots.txt exposure
  if (robotsTxt) {
    findings.push({
      id: 'find-robots-exposure',
      check: 'robots',
      title: '/admin exposed in robots.txt',
      severity: 'low',
      detail: 'Administrative paths are disclosed in robots.txt file',
      recommendation: 'Remove sensitive paths from robots.txt or use proper authentication'
    });
  }

  // Rule 5: Insecure ports
  const insecurePorts = [21, 23, 3389, 5900];
  const foundInsecure = ports.filter(p => insecurePorts.includes(p));
  if (foundInsecure.length > 0) {
    findings.push({
      id: 'find-insecure-ports',
      check: 'port',
      title: 'Insecure ports detected',
      severity: 'high',
      detail: `Insecure ports open: ${foundInsecure.join(', ')}`,
      recommendation: 'Close or secure these ports with proper authentication and encryption'
    });
  }

  // Determine summary
  let summary = 'pass';
  if (target.toLowerCase().includes('example')) {
    summary = 'warn'; // Force warn for example.com
  } else if (findings.some(f => f.severity === 'high')) {
    summary = 'fail';
  } else if (findings.some(f => f.severity === 'medium')) {
    summary = 'warn';
  }

  return {
    id: generateScanId(config),
    startedAt: generateTimestamp(config),
    target: target,
    summary: summary,
    findings: findings,
    meta: {
      tags: config.tags || [],
      note: config.note || ''
    },
    originalConfig: config
  };
}
