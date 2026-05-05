#!/usr/bin/env node
// Node shim — spawns the bundled Python CLI with all forwarded args.
// Requires Python 3.10+ and the `homeharvest` package (auto-installed by postinstall).

const { spawn, spawnSync } = require('node:child_process');
const path = require('node:path');
const fs = require('node:fs');

const SCRIPT = path.join(__dirname, '..', 'src', 'goclaw_homeharvest', 'cli.py');

function resolvePython() {
  if (process.env.GOCLAW_HOMEHARVEST_PYTHON) return process.env.GOCLAW_HOMEHARVEST_PYTHON;
  const candidates = process.platform === 'win32' ? ['py', 'python', 'python3'] : ['python3', 'python'];
  for (const bin of candidates) {
    const r = spawnSync(bin, ['--version'], { stdio: 'ignore' });
    if (r.status === 0) return bin;
  }
  return null;
}

const py = resolvePython();
if (!py) {
  console.error('[goclaw-homeharvest] ERROR: Python 3.10+ not found in PATH.');
  console.error('Install Python from https://www.python.org/ or set GOCLAW_HOMEHARVEST_PYTHON to a python binary path.');
  process.exit(127);
}
if (!fs.existsSync(SCRIPT)) {
  console.error(`[goclaw-homeharvest] ERROR: bundled script missing at ${SCRIPT}`);
  process.exit(1);
}

const child = spawn(py, [SCRIPT, ...process.argv.slice(2)], { stdio: 'inherit' });
child.on('exit', (code, signal) => {
  if (signal) process.kill(process.pid, signal);
  else process.exit(code ?? 1);
});
child.on('error', (err) => {
  console.error(`[goclaw-homeharvest] ERROR: failed to spawn ${py}: ${err.message}`);
  process.exit(1);
});
