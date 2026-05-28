# Agent Harness

Harness local para reduzir o copia/cola entre Orchestrator, Builder, QA e Security.

Ele usa seus prompts atuais como templates e cria um ciclo baseado em arquivos dentro de `.harness/runs/<run_id>/`.

## Arquivos ativos

Estes sao os arquivos canonicos do harness:

- `builder.md` — prompt base do Builder.
- `orchestrator.md` — contrato do Orchestrator, incluindo modo manual e modo CLI-assisted.
- `qa.md` — prompt base de QA com `QA_VERDICT`.
- `security.md` — prompt base de Security com `VERDICT`.
- `scripts/agent-loop.py` — loop local que gera prompts e, opcionalmente, chama CLIs.
- `scripts/agent-loop.sh` — wrapper para o Python.
- `agent-harness.config.example.json` — exemplo de configuracao para `opencode` + `copilot`.

Nao recrie arquivos duplicados como `builder 2.md`, `orchestrator 2.md` ou `qa 2.md`. Se precisar testar uma variante, use `.harness/runs/` ou outro arquivo temporario ignorado pelo git.

## Ideia

```text
Você descreve a tarefa
  ↓
Harness escolhe builder frontend/backend
  ↓
Gera prompt do builder
  ↓
Opcionalmente chama CLI do builder
  ↓
Coleta diff
  ↓
Gera prompts de QA e Security
  ↓
Você aprova o merge/commit
```

## Instalação rápida

Para habilitar execucao por CLI, crie a configuracao local:

```bash
cp harness/prompts/agent-harness.config.example.json harness/prompts/agent-harness.config.json
chmod +x harness/prompts/scripts/agent-loop.py harness/prompts/scripts/agent-loop.sh
```

Edite `agent-harness.config.json` para apontar para os comandos reais disponíveis na sua máquina.
O arquivo local `harness/prompts/agent-harness.config.json` é ignorado pelo git.

Se a configuracao local nao existir, `agent-loop.py` usa uma configuracao interna segura. Em `manual`, isso basta. Em `builder` ou `full`, configure os comandos explicitamente antes de confiar no loop.

## Instrucoes para futuros Orchestrators

1. Leia `CLAUDE.md`, `AGENTS.md`, `HANDOFF.md`, `STATUS.json` e `docs/architecture.md` antes de iniciar.
2. Escolha uma fatia atomica do `STATUS.json`.
3. Se o usuario pedir prompt handoff, siga `orchestrator.md` e entregue prompts para Builder, QA e Security.
4. Se o usuario pedir CLI-assisted, use `scripts/agent-loop.py` ou chamadas diretas equivalentes.
5. Em CLI-assisted, sempre limite o diff com `--diff-path` quando houver sujeira nao relacionada no worktree.
6. Aceite o slice somente com sensores obrigatorios verdes e QA/Security processados.
7. Atualize `HANDOFF.md`, `STATUS.json`, `docs/progress.md` e `docs/session-log.md`.
8. Nunca inclua `.harness/`, configuracao local, credenciais, logs ou artefatos gerados no commit.
9. Commit/push somente quando o humano pedir.

## Uso manual, seguro

Gera arquivos e prompts, mas não chama agentes automaticamente:

```bash
harness/prompts/scripts/agent-loop.py "Criar página de login com magic link" --mode manual
```

## Uso semi-automático

Chama o builder configurado, coleta diff e gera prompts de QA/security:

```bash
harness/prompts/scripts/agent-loop.py "Criar página de login com magic link" --mode builder
```

## Uso com builder específico

```bash
harness/prompts/scripts/agent-loop.py "Criar endpoint de checkout" --builder backend --mode builder
harness/prompts/scripts/agent-loop.py "Ajustar formulário de cadastro" --builder frontend --mode builder
```

## Uso com diff limitado

Use `--diff-path` para evitar que QA/Security revisem sujeira não relacionada no working tree:

```bash
harness/prompts/scripts/agent-loop.py "Implementar back-010" --mode full --builder backend \
  --diff-path api/app/services/csv_io.py \
  --diff-path api/app/services/bibtex_io.py \
  --diff-path api/app/routers/export.py \
  --diff-path api/tests/test_export.py \
  --diff-path STATUS.json \
  --diff-path HANDOFF.md \
  --diff-path docs/progress.md \
  --diff-path docs/session-log.md
```

## Saída

Cada execução cria:

```text
.harness/runs/<timestamp>/
  task.md
  builder.prompt.md
  builder.output.md
  diff.patch
  qa.prompt.md
  qa.output.md
  security.prompt.md
  security.output.md
  final-report.md
```

## Gates humanos recomendados

- Antes de iniciar: você define a tarefa.
- Depois do builder: você revisa o diff rapidamente.
- Depois de QA/security: você decide se mergeia ou volta para builder.
