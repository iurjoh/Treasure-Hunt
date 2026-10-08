# Treasure-Hunt - jogo Python no navegador

**Português (Brasil)** | [English](README.md)

Jogo Python de caça ao tesouro em grade, com port web Pyodide. Terminal e navegador compartilham engine.

Projeto acadêmico público com demo ao vivo.

**Source / Código:** https://github.com/iurjoh/Treasure-Hunt

**Inspected commit / Commit inspecionado:** `e5d1f48d40cc936cab7f459922984a7839d461a2`

**Live demo:** https://treasure-hunt-due.pages.dev/web/

Captura mobile preparada em 08/10/2026; upload no repositório pendente. Sem imagem embutida até o asset existir.

Captura mobile: 390x844, 08/10/2026. Upload no repositório ainda pendente.

## Ideia e planejamento

Permitir testar PP3 sem instalar Python. Preservar regras, criar adapter web e corrigir replay, entrada inválida e encerramento.

## Funcionalidades e limites

Grades Easy/Medium/Hard (3x3,5x5,9x9), 4/7/13 tentativas, repetir mapa, nova aventura e sair. Nome/estado locais da sessão.

## Arquitetura

treasure_hunt.py engine; run.py CLI; web/index.html/adapter carregam Python/WebAssembly via CDN Pyodide. Sem backend próprio, mas há requests externos do runtime.

## Design e capturas

Página escura inspirada em terminal, texto colorido/input inferior. Captura nova usa nome inventado Ada. Não descrevê-la como rodada completa testada.

## Histórico do build

PP3 Python CLI original; setembro de 2026: estados explícitos, UTF-8, EOF limpo/adapter web compartilhado. Documentação de 1º de outubro registra URL. Capturas antigas só históricas até inspeção individual.

## Desempenho

Runtime Python baixa pela rede na primeira visita. Sem nova medição de download/tempo/Lighthouse; abertura fria e falha CDN exigem revisão.

## Segurança e privacidade

Usar nomes inventados em evidências. Gameplay local, mas CDN contata terceiros. Não afirmar ausência de rede/offline completo sem testar.

## Evidência de testes

08/10/2026: 70 testes pytest passaram na main inspecionada. Navegador carregou Pyodide, aceitou Ada/Easy e chegou à primeira linha. Pixels móveis inspecionados. Vitória/derrota/replay e suite web desktop não repetidos.

## Executar localmente

```sh
python3 run.py
python3 -m pytest -q
python3 -m http.server 8000
```

Instalar pytest só no ambiente de desenvolvimento; jogo usa biblioteca padrão. Servidor estático abre /web/.

## Estágio atual e identidade da release

Motor Python e port web estão no `main`, não apenas em branch de revival. A página `/web/` abriu em 08/10/2026. SHA exato do deploy não confirmado; o commit inspecionado acima não comprova paridade com o host. Registrar essa correspondência e uma rodada completa no navegador antes de verificar nova release. Pyodide é dependência externa de primeira carga; recuperação de falha CDN e jogo totalmente offline não confirmados.

## Publicação e roadmap

Rodadas/replay completos na web; falha CDN/abertura fria; revisar direitos/conteúdo de capturas antigas; tablet/desktop e correspondência source/deploy.

Nenhuma configuração de host/custo/branch alterada ou reconferida. Página acessível não prova paridade source/deploy.

## Créditos e licença

Code Institute PP3, autor Iuri Johansson, runtime Pyodide. Citações finais atribuídas a Doug Scott/Albert Einstein no registro anterior, sem reverificação.

Sem LICENSE na raiz inspecionada. Não anunciar MIT antes de conferir direitos autorais/terceiros e aprovar licença. Nenhuma licença alterada.


## Atribuições originais preservadas

### Credits

- Original project: Code Institute Portfolio Project 3 (Python CLI),
  by [iurjoh](https://github.com/iurjoh).
- Quotes in the end-game art: Doug Scott and Albert Einstein.
- Browser runtime: [Pyodide](https://pyodide.org) (CPython compiled to
  WebAssembly), loaded from the jsDelivr CDN.
