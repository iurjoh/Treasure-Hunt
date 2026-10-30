/* Treasure Hunt game worker.
 * Loads Pyodide off the main thread so the page stays responsive and the
 * heavy WebAssembly compile never blocks input or paint.
 * Protocol (postMessage):
 *   main -> worker: {type: 'init', seed: <int|null>, lang: <'en'|'pt'|null>}
 *   main -> worker: {type: 'submit', value: <string>}
 *   worker -> main: {type: 'ready', loadMs, lang, startOutputs}
 *                                               (engine's first screen;
 *                                                without ?lang it equals the
 *                                                static HTML paint)
 *   worker -> main: {type: 'outputs', outputs: [[kind, text], ...], state, lang}
 *   worker -> main: {type: 'error', message}
 */
const PYODIDE_VERSION = 'v0.26.4';
const PYODIDE_CDN = `https://cdn.jsdelivr.net/pyodide/${PYODIDE_VERSION}/full/`;

let gameSubmit = null;
let gameState = null;
let gameLang = null;
let t0 = 0;

async function boot(seed, lang) {
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
_lang = ${lang === null ? 'None' : `'${lang}'`}
_kwargs = {}
if _seed is not None:
    _kwargs['rng'] = _random.Random(_seed)
if _lang is not None:
    _kwargs['lang'] = _lang
_game = TreasureHunt(**_kwargs)
_start_outputs = _game.start()  # without ?lang, first screen ships as static HTML
def game_submit(value):
    return _json.dumps(_game.submit(value))
def game_state():
    return _game.state
def game_lang():
    return _game.lang or ''
def game_start_outputs():
    return _json.dumps(_start_outputs)
`);
  const globals = pyodide.globals;
  gameSubmit = globals.get('game_submit');
  gameState = globals.get('game_state');
  gameLang = globals.get('game_lang');
  const gameStartOutputs = globals.get('game_start_outputs');
  self.postMessage({
    type: 'ready',
    loadMs: Date.now() - t0,
    lang: gameLang(),
    startOutputs: JSON.parse(gameStartOutputs()),
  });
}

self.onmessage = (event) => {
  const msg = event.data;
  if (msg.type === 'init') {
    boot(msg.seed, msg.lang || null).catch((err) => {
      console.error(err);
      self.postMessage({ type: 'error', message: String(err && err.message || err) });
    });
    return;
  }
  if (msg.type === 'submit' && gameSubmit) {
    try {
      const outputs = JSON.parse(gameSubmit(msg.value));
      self.postMessage({ type: 'outputs', outputs, state: gameState(), lang: gameLang() });
    } catch (err) {
      self.postMessage({ type: 'error', message: String(err && err.message || err) });
    }
  }
};
