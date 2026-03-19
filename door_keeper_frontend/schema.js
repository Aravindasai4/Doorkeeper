/**
 * Schema validation for DoorKeeper config
 * Lightweight Zod-like validation
 */

const ConfigSchema = {
  validate(data) {
    const errors = [];

    // Required: target
    if (!data.target || typeof data.target !== 'string') {
      errors.push('target is required and must be a string (URL or IP)');
    }

    // Optional: checks
    if (data.checks !== undefined) {
      if (typeof data.checks !== 'object' || Array.isArray(data.checks)) {
        errors.push('checks must be an object');
      } else {
        // Optional: checks.ports
        if (data.checks.ports !== undefined) {
          if (!Array.isArray(data.checks.ports)) {
            errors.push('checks.ports must be an array');
          } else if (!data.checks.ports.every(p => typeof p === 'number')) {
            errors.push('checks.ports must contain only numbers');
          }
        }

        // Optional: checks.httpSecurityHeaders
        if (data.checks.httpSecurityHeaders !== undefined && typeof data.checks.httpSecurityHeaders !== 'boolean') {
          errors.push('checks.httpSecurityHeaders must be a boolean');
        }

        // Optional: checks.robotsTxt
        if (data.checks.robotsTxt !== undefined && typeof data.checks.robotsTxt !== 'boolean') {
          errors.push('checks.robotsTxt must be a boolean');
        }
      }
    }

    // Optional: tags
    if (data.tags !== undefined) {
      if (!Array.isArray(data.tags)) {
        errors.push('tags must be an array');
      } else if (!data.tags.every(t => typeof t === 'string')) {
        errors.push('tags must contain only strings');
      }
    }

    // Optional: note
    if (data.note !== undefined && typeof data.note !== 'string') {
      errors.push('note must be a string');
    }

    return {
      valid: errors.length === 0,
      errors: errors
    };
  }
};

// Test configs for QA
const TEST_CONFIGS = {
  goodHttps: {
    target: "https://secure-app.com",
    checks: {
      ports: [443],
      httpSecurityHeaders: true,
      robotsTxt: true
    },
    tags: ["production", "secure"],
    note: "Production environment with good security"
  },
  
  noHttps: {
    target: "http://acme.co",
    checks: {
      ports: [80],
      httpSecurityHeaders: true
    },
    tags: ["insecure"],
    note: "HTTP only - no HTTPS enforcement"
  },
  
  robotsExposed: {
    target: "https://example.com",
    checks: {
      ports: [80, 443],
      httpSecurityHeaders: true,
      robotsTxt: true
    },
    tags: ["demo", "webapp"],
    note: "Site with exposed admin in robots.txt"
  }
};
