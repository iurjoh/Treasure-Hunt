# Treasure Hunt

**Português (Brasil)** | [English](README.md)

Um jogo de terminal em Python, agora rodando **no navegador** - sem instalação, sem backend, funciona no celular e no desktop. A página carrega o próprio Python ([Pyodide](https://pyodide.org), WebAssembly) e joga exatamente o mesmo motor de jogo da versão de terminal.

> **Status (30/09/2026):** branch de revival, port web completo e testado.
> O deploy público no Cloudflare Pages (nível gratuito) está preparado, mas
> aguardando o aval do dono - este README será atualizado com
> a URL ativa quando o jogo for publicado.

## Jogar

### No navegador

Sirva a raiz do repositório com qualquer servidor de arquivos estáticos e abra
`web/index.html` - ou simplesmente visite o site ativo:

```bash
python3 -m http.server 8000
# depois abra http://localhost:8000/web/
```

O primeiro carregamento baixa o runtime Python do CDN da Pyodide
(alguns MB, cacheados pelo navegador depois). Tudo roda localmente
na sua aba; nada é enviado a lugar nenhum.

### No terminal

```bash
python3 run.py
```

Requer Python 3.8+. Sem dependências.

## O jogo

Você é um explorador caçando um baú de tesouro escondido em uma grade:

- Escolha uma dificuldade: Fácil (3x3), Média (5x5) ou Difícil (9x9).
- Você tem `int(size * 1.5)` palpites: 4, 7 ou 13 escavações.
- Cada escavação marca o mapa (`X`). Encontre o baú (`T`) antes de
  ficar sem palpites.
- Quando uma partida termina, você pode **rejogar o mesmo mapa** (mesma
  posição do tesouro), começar uma **nova aventura** (nova dificuldade,
  novo tesouro) ou sair.

## Capturas de tela

| | Antes (só terminal) | Depois (port web) |
|---|---|---|
| Desktop | ![CLI no desktop](assets/images/revival/before-cli-desktop.png) | ![Web no desktop](assets/images/revival/web-desktop-win.png) |
| Celular | não existia versão móvel | ![Web no celular](assets/images/revival/web-mobile-win.png) |

Mais: [gameplay](assets/images/revival/web-desktop-start.png),
[derrota](assets/images/revival/web-desktop-loss.png),
[replay do mesmo mapa](assets/images/revival/web-desktop-replay.png),
[início no celular](assets/images/revival/web-mobile-start.png),
[derrota no celular](assets/images/revival/web-mobile-loss.png).

## Revival: o que mudou (auditoria de 30/09/2026)

| Severidade | Problema | Correção |
|---|---|---|
| P0 | `UnicodeDecodeError`/crash ao imprimir a arte em terminais cp1252 (Windows) | `run.py` reconfigura stdout/stderr para UTF-8 com `errors="replace"`; a versão web renderiza no DOM, que é UTF-8 por natureza |
| P0 | "Reiniciar" silenciosamente começava uma partida **nova** em vez de rejogar a mesma | O menu pós-partida agora oferece `R` = rejogar o mesmo mapa (mesmo tamanho de tabuleiro e posição do tesouro), `N` = nova aventura, `Q` = sair |
| P0 | `EOF` (Ctrl+D) fechava o jogo com um traceback feio | `EOFError`/`KeyboardInterrupt` são capturados e encerram o jogo com despedida limpa, código de saída 0 |
| P2 | Wrappers `while True` desprotegidos, prompt duplo de reinício após cada partida | O fluxo do jogo agora é uma máquina de estados explícita (`name → level → row/col → menu → done`) compartilhada entre CLI e web |
| - | Nenhum teste automatizado no repositório | Suíte completa adicionada (ver abaixo) |
| - | Sobras de template Heroku/Node/Gitpod (`Procfile`, `index.js`, `package.json`, `views/`, `controllers/`) | Removidas; o projeto agora é Python puro + web estática |

### Arquitetura

A lógica do jogo fica em `treasure_hunt.py`, uma máquina de estados pura
sem `input()`/`print()` dentro. Três drivers a compartilham:

- `run.py` - o CLI de terminal.
- `web/` - o front-end do navegador (a Pyodide carrega o mesmo
  arquivo `treasure_hunt.py` e chama `start()`/`submit()`).
- `tests/` - a suíte automatizada.

Um motor, três drivers: o terminal, o navegador e os testes nunca
divergem.

## Testes

```bash
pip install -r requirements-dev.txt
python3 -m pytest tests/ -q
```

Suíte (70 testes):

- **30 vitórias roteirizadas** em todos os tamanhos de tabuleiro, nomes e posições do baú.
- **30 derrotas roteirizadas** que queimam todos os palpites e verificam o fluxo
  de derrota e a posição revelada do tesouro.
- **600 rodadas fuzzadas** em 9 classes de entrada (válida, não-numérica,
  vazia, negativa, fora do intervalo, coordenada repetida, espaços, números
  enormes, unicode) garantindo que o motor nunca quebra, nunca perde
  estado e nunca deixa lixo consumir um palpite.
- **Semântica de reinício**: rejogar o mesmo mapa mantém o mesmo
  tesouro; uma nova aventura pede dificuldade; sair encerra limpo.
- **Testes de subprocesso do CLI**: EOF no primeiro prompt e saídas no meio do jogo
  retornam 0 sem traceback; uma vitória completa com seed (`TREASURE_HUNT_SEED`)
  pelo `run.py` real.
- **End-to-end no navegador** (rodado manualmente com Playwright contra um
  servidor estático local): vitória, derrota, replay-do-mesmo-mapa, saída e
  entrada inválida em viewports de desktop (1280x800) e celular (390x844),
  verificando overflow horizontal.

### Ganchos determinísticos

- CLI: `TREASURE_HUNT_SEED=42 python3 run.py`
- Web: abra `web/index.html?seed=42`

Ambos posicionam o tesouro deterministicamente - usados pela suíte de testes.

## Deploy (Cloudflare Pages, gratuito)

O site é totalmente estático, então o nível gratuito basta - sem cartão, sem
faturamento:

1. Painel da Cloudflare → **Workers & Pages** → **Create** → **Pages**
   → **Connect to Git** (ou **Direct Upload** desta pasta).
2. Configuração de build: **sem comando de build**, diretório de saída = a
   raiz do repositório.
3. Deploy. O jogo fica em `https://<projeto>.pages.dev/`
   (o `index.html` da raiz redireciona para `web/`).

GitHub Pages funciona do mesmo jeito (servindo a raiz do repo).

## Estrutura do projeto

```
treasure_hunt.py   motor do jogo (máquina de estados, sem I/O)
run.py             ponto de entrada do terminal (seguro em UTF-8, seguro em EOF)
web/index.html     UI do navegador
web/app.js         carregador da Pyodide + renderizador
web/style.css      visual de terminal responsivo (celular + desktop)
index.html         redireciona para web/
tests/             suíte pytest (70 testes)
assets/images/     capturas de tela (revival/ guarda as do port web)
```

## Créditos

- Projeto original: Code Institute Portfolio Project 3 (CLI em Python),
  por [iurjoh](https://github.com/iurjoh).
- Citações na arte de fim de jogo: Doug Scott e Albert Einstein.
- Runtime no navegador: [Pyodide](https://pyodide.org) (CPython compilado para
  WebAssembly), carregada do CDN jsDelivr.

## Qualidade medida (site ativo, 30/09/2026, commit d855188)

Medido contra https://treasure-hunt-due.pages.dev/web/ com
Lighthouse 12 (Chromium headless), axe-core 4.10 e os validadores do W3C.
Cada linha do Lighthouse é a mediana de 3 execuções.

| Verificação | Resultado | Meta |
| --- | --- | --- |
| Lighthouse mobile, cache frio | Perf 100, A11y 100, Best Practices 100, SEO 100 | Perf >= 90, demais 100 |
| Lighthouse desktop, cache frio | Perf 100, A11y 100, Best Practices 100, SEO 100 | igual |
| Lighthouse mobile + desktop, cache quente | 100 / 100 / 100 / 100 | Perf >= 95 |
| axe-core (wcag2a/2aa/21a/21aa/22aa) em 4 estados do jogo | 0 violações, 0 incompletas | 0 violações |
| W3C Nu HTML (`/web/`, redirecionamento da raiz) | 0 erros | 0 erros |
| W3C CSS (`web/style.css`) | 0 erros (1 nota de depreciação em `word-break: break-word`, mantido por compatibilidade) | 0 erros |
| Jogo só por teclado (Tab/Enter, sem mouse) | caminho completo de vitória funciona; input com foco automático, anel de foco visível | precisa funcionar |
| Reflow em 320px e zoom 200%/400% | sem overflow horizontal | sem overflow |
| Tempo frio até jogável (boot da Pyodide, medido) | ~2,5-2,8 s no cabo; UI de terminal estática pinta imediatamente | - |
