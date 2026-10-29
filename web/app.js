/* Treasure Hunt web front-end (main thread).
 * Talks to worker.js, which runs the same treasure_hunt.py engine as the
 * CLI inside Pyodide.
 * URL hooks for tests and shareable links:
 *   ?seed=42       makes the treasure deterministic
 *   ?lang=pt|en    skips the language selector (greeting included)
 * Without ?lang, the first screen asks the language BEFORE the welcome
 * text; after the choice the page chrome (button, aria labels, status
 * lines, <html lang>) switches to the chosen language.
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

  // Page chrome only; every in-game string comes from the engine.
  const UI_STRINGS = {
    en: {
      send: 'Send',
      answer: 'Your answer',
      gameOver: 'Game over. Reload the page to play again.',
      loadFail: 'Could not load the game. Check your connection and reload.',
      workerFail: 'Could not start the game worker: ',
    },
    pt: {
      send: 'Enviar',
      answer: 'Sua resposta',
      gameOver: 'Fim de jogo. Recarregue a página para jogar de novo.',
      loadFail: 'Não foi possível carregar o jogo. Verifique sua conexão e recarregue.',
      workerFail: 'Não foi possível iniciar o jogo: ',
    },
  };
  let ui = null; // null until the player picks a language

  function applyLang(lang) {
    if (!UI_STRINGS[lang]) return;
    ui = UI_STRINGS[lang];
    document.documentElement.lang = lang === 'pt' ? 'pt-BR' : 'en';
    send.textContent = ui.send;
    entry.setAttribute('aria-label', ui.answer);
  }

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

  const params = new URLSearchParams(location.search);
  const seedParam = params.get('seed');
  const seed = seedParam === null ? null : parseInt(seedParam, 10);
  const langParam = (params.get('lang') || '').toLowerCase().replace('_', '-');
  const lang = langParam === 'en' ? 'en'
    : (langParam === 'pt' || langParam === 'pt-br') ? 'pt'
    : null;

  const t0 = performance.now();
  let worker;
  try {
    worker = new Worker('worker.js');
  } catch (err) {
    fail((ui || UI_STRINGS.en).workerFail + err.message);
    return;
  }

  worker.onmessage = (event) => {
    const msg = event.data;
    if (msg.type === 'ready') {
      window.__timeToPlayable = Math.round(performance.now() - t0);
      if (msg.lang) applyLang(msg.lang);
      if (lang !== null) {
        // ?lang= skipped the selector: the static paint shows the language
        // menu, so replace it with the engine's real first screen.
        screen.textContent = '';
        render(msg.startOutputs);
      }
      status.textContent = '';
      entry.disabled = false;
      send.disabled = false;
      entry.focus();
      return;
    }
    if (msg.type === 'outputs') {
      if (msg.lang) applyLang(msg.lang);
      render(msg.outputs);
      refresh(msg.state);
      return;
    }
    if (msg.type === 'error') {
      fail((ui || UI_STRINGS.en).loadFail + ' (' + msg.message + ')');
    }
  };

  worker.onerror = (event) => {
    fail((ui || UI_STRINGS.en).loadFail);
    console.error(event.message);
  };

  function refresh(state) {
    entry.inputMode = (state === 'row' || state === 'col') ? 'numeric' : 'text';
    if (state === 'done') {
      entry.disabled = true;
      send.disabled = true;
      status.textContent = (ui || UI_STRINGS.en).gameOver;
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

  worker.postMessage({ type: 'init', seed, lang });
})();
