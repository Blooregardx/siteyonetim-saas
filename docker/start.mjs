import { configure } from './config.mjs';
import { gate } from './gate.mjs';
try { configure('runtime'); await gate(); await import('../server.js'); }
catch { console.error('SELFHOST_START_FAILED: check configuration, role and migration state'); process.exit(1); }
