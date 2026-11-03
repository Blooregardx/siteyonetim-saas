import { configure } from './config.mjs';
import { gate } from './gate.mjs';
try { configure('runtime'); await gate(); const r = await fetch('http://127.0.0.1:3000/demo', {signal: AbortSignal.timeout(5000)}); if (!r.ok) process.exit(1); }
catch { process.exit(1); }
