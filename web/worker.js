/* Treasure Hunt game worker.
 * Loads Pyodide off the main thread so the page stays responsive and the
 * heavy WebAssembly compile never blocks input or paint.
 * Protocol (postMessage):
 *   main -> worker: {type: 'init', seed: <int|null>}
 *   main -> worker: {type: 'submit', value: <string>}
 *   worker -> main: {type: 'ready'}            (engine started, first
 *                                               screen is static HTML)
 *   worker -> main: {type: 'outputs', outputs: [[kind, text], ...], state}
 *   worker -> main: {type: 'error', message}
 */
const PYODIDE_VERSION = 'v0.26.4';
const PYODIDE_CDN = `https://cdn.jsdelivr.net/pyodide/${PYODIDE_VERSION}/full/`;

let gameSubmit = null;
let gameState = null;
let t0 = 0;

async function boot(seed) {
  t0 = Date.now();
  importScripts(PYODIDE_CDN + 'pyodide.js');
  const pyodide = await loadPyodide({ indexURL: PYODIDE_CDN });
  const response = await fetch('../treasure_hunt.py');
  if (!response.ok) throw new Error('could not fetch treasure_hunt.py');
  const source = await response.text();
  pyodide.runPython(source + `
import json as _json
import random as _random
_seed = ${seed === null ? 'None' : seed}
_game = TreasureHunt(_random.Random(_seed)) if _seed is not None else TreasureHunt()
_game.start()  # first screen ships as static HTML; nothing to emit here
def game_submit(value):
    return _json.dumps(_game.submit(value))
def game_state():
    return _game.state
`);
  const globals = pyodide.globals;
  gameSubmit = globals.get('game_submit');
  gameState = globals.get('game_state');
  self.postMessage({ type: 'ready', loadMs: Date.now() - t0 });
}

self.onmessage = (event) => {
  const msg = event.data;
  if (msg.type === 'init') {
    boot(msg.seed).catch((err) => {
      console.error(err);
      self.postMessage({ type: 'error', message: String(err && err.message || err) });
    });
    return;
  }
  if (msg.type === 'submit' && gameSubmit) {
    try {
      const outputs = JSON.parse(gameSubmit(msg.value));
      self.postMessage({ type: 'outputs', outputs, state: gameState() });
    } catch (err) {
      self.postMessage({ type: 'error', message: String(err && err.message || err) });
    }
  }
};
