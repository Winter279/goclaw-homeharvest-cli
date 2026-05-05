#!/usr/bin/env node
// Post-install hook — best-effort install of the `homeharvest` Python dependency.
// Failures are non-fatal; user can install manually with `pip install homeharvest`.

const { spawnSync } = require('node:child_process');

if (process.env.GOCLAW_HOMEHARVEST_SKIP_POSTINSTALL === '1') {
  console.log('[goclaw-homeharvest] Skipping postinstall (GOCLAW_HOMEHARVEST_SKIP_POSTINSTALL=1).');
  process.exit(0);
}

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
  console.warn('[goclaw-homeharvest] WARNING: Python 3.10+ not found. Install Python and run:');
  console.warn('    pip install "homeharvest>=0.4.10"');
  process.exit(0);
}

const check = spawnSync(py, ['-c', 'import homeharvest'], { stdio: 'ignore' });
if (check.status === 0) {
  console.log('[goclaw-homeharvest] homeharvest already installed — skipping pip install.');
  process.exit(0);
}

console.log('[goclaw-homeharvest] Installing Python dep "homeharvest" via pip...');
const attempts = [
  [py, ['-m', 'pip', 'install', '--quiet', '--user', 'homeharvest>=0.4.10']],
  [py, ['-m', 'pip', 'install', '--quiet', '--user', '--break-system-packages', 'homeharvest>=0.4.10']],
];

let ok = false;
for (const [cmd, args] of attempts) {
  const r = spawnSync(cmd, args, { stdio: 'inherit' });
  if (r.status === 0) { ok = true; break; }
}

if (!ok) {
  console.warn('[goclaw-homeharvest] WARNING: pip install failed. Install manually:');
  console.warn('    pip install "homeharvest>=0.4.10"');
  console.warn('    (or use a virtualenv / pipx)');
}

process.exit(0);
