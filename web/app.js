/* Treasure Hunt web front-end (main thread).
 * Talks to worker.js, which runs the same treasure_hunt.py engine as the
 * CLI inside Pyodide. URL hook for tests: ?seed=42 makes the treasure
 * deterministic.
 */
(() => {
  const screen = document.getElementById('screen');
  const status = document.getElementById('status');
  const controls = document.getElementById('controls');
  const entry = document.getElementById('entry');
  const send = document.getElementById('send');

  const CLASS_FOR = {
    art: 'line art',
    board: 'line board',
    prompt: 'line prompt',
    error: 'line error',
    success: 'line success',
    text: 'line text',
  };

  function scrollDown() {
    requestAnimationFrame(() => window.scrollTo(0, document.body.scrollHeight));
  }

  /* ASCII art is authored for an 80-column terminal. Computed font-size
   * stays 13px (legible); blocks wider than the screen are scaled down
   * with a transform so they keep fitting narrow phones. */
  function fitArt(el) {
    el.style.transform = '';
    el.style.height = '';
    el.style.overflow = '';
    const avail = el.clientWidth;
    const need = el.scrollWidth;
    if (avail > 0 && need > avail) {
      const s = Math.max(avail / need, 0.3);
      el.style.transformOrigin = 'left top';
      el.style.transform = 'scale(' + s + ')';
      el.style.height = (el.scrollHeight * s) + 'px';
      el.style.overflow = 'hidden';
    }
  }

  function fitAllArt() {
    screen.querySelectorAll('.art').forEach(fitArt);
  }

  window.addEventListener('resize', fitAllArt);

  function render(outputs) {
    const arts = [];
    for (const [kind, text] of outputs) {
      const div = document.createElement('div');
      div.className = CLASS_FOR[kind] || 'line text';
      div.textContent = text;
      screen.appendChild(div);
      if (kind === 'art') arts.push(div);
    }
    if (arts.length) requestAnimationFrame(() => arts.forEach(fitArt));
    scrollDown();
  }

  // Fit the static intro art shipped in index.html.
  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', fitAllArt);
  } else {
    fitAllArt();
  }

  function echo(value) {
    const div = document.createElement('div');
    div.className = 'line echo';
    div.textContent = '> ' + value;
    screen.appendChild(div);
    scrollDown();
  }

  function fail(message) {
    status.textContent = message;
    status.style.color = '#f85149';
  }

  const seedParam = new URLSearchParams(location.search).get('seed');
  const seed = seedParam === null ? null : parseInt(seedParam, 10);
  const t0 = performance.now();
  let worker;
  try {
    worker = new Worker('worker.js');
  } catch (err) {
    fail('Could not start the game worker: ' + err.message);
    return;
  }

  worker.onmessage = (event) => {
    const msg = event.data;
    if (msg.type === 'ready') {
      window.__timeToPlayable = Math.round(performance.now() - t0);
      status.textContent = '';
      entry.disabled = false;
      send.disabled = false;
      entry.focus();
      return;
    }
    if (msg.type === 'outputs') {
      render(msg.outputs);
      refresh(msg.state);
      return;
    }
    if (msg.type === 'error') {
      fail('Could not load the game. Check your connection and reload. (' + msg.message + ')');
    }
  };

  worker.onerror = (event) => {
    fail('Could not load the game. Check your connection and reload.');
    console.error(event.message);
  };

  function refresh(state) {
    entry.inputMode = (state === 'row' || state === 'col') ? 'numeric' : 'text';
    if (state === 'done') {
      entry.disabled = true;
      send.disabled = true;
      status.textContent = 'Game over. Reload the page to play again.';
    }
    entry.focus();
  }

  controls.addEventListener('submit', (event) => {
    event.preventDefault();
    if (entry.disabled) return;
    const value = entry.value;
    entry.value = '';
    echo(value);
    worker.postMessage({ type: 'submit', value });
  });

  worker.postMessage({ type: 'init', seed });
})();
