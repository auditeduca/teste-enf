# Calculator Agents

Agentes para **validação**, **correção** e **geração** de páginas de calculadoras/escalas.

## APIs suportadas

Carregamento de `.env` (em ordem, via `scripts/env_paths.py`):

1. Variáveis já definidas no ambiente
2. `CALENF_ENV_FILE` (caminho customizado)
3. `.env` na raiz do repositório
4. `NIFS/.env`
5. `C:/Github/CALENF-NKD/.env` (legado Windows)
6. `C:/Users/leivi/Downloads/nkos-site-i18n-completo-v1/.env` (legado Windows)
7. Espelho WSL do caminho acima (`/mnt/c/Users/...`)
8. `~/.calenf/.env`

Chaves usadas:

| Variável | Uso |
|----------|-----|
| `DEEPSEEK_API_KEY` | Revisão clínica, geração de JSON, tradução |
| `ANTHROPIC_API_KEY` | Revisão clínica densa (via llm_router) |
| `GROQ_API_KEY` | Checks rápidos (opcional) |
| `NKOS_NO_LLM=1` | Desativa todas as chamadas LLM |

## Comandos

```bash
# Status das APIs
python -m scripts.calculator_agents status

# Validar todas as calculadoras (após `bash scripts/ready.sh`)
python -m scripts.calculator_agents validate

# Publicar + validar + segurança (comando único)
bash scripts/ready.sh

# Validar páginas específicas
python -m scripts.calculator_agents validate imc glasgow apgar

# Corrigir (sync JSON + footer)
python -m scripts.calculator_agents correct imc glasgow

# Corrigir com revisão clínica via DeepSeek/Claude
python -m scripts.calculator_agents correct imc --llm

# Gerar HTML a partir de reference-website/data/tools/{slug}.json
python -m scripts.calculator_agents generate braden

# Gerar JSON + HTML via LLM (rascunho)
python -m scripts.calculator_agents generate nova-escala --draft --llm \
  --name "Nova Escala" --description "Descrição clínica"

# Pipeline completo
python -m scripts.calculator_agents pipeline imc apgar --llm

# Orquestrador de segurança (pre-deploy)
python -m scripts.calculator_agents orchestrate --mode pre_deploy
python -m scripts.calculator_agents orchestrate imc glasgow --dry-run
```

Relatórios salvos em `artifacts/security/orchestration_*.json`.

## DAG do orquestrador de segurança

```
security_scan → validate → correct → security_scan → validate
```

Verificações de segurança:
- Vazamento de secrets (API keys, tokens)
- Padrões JS inseguros (`eval`, `new Function`)
- Landmarks de acessibilidade (skip-link, main, header, a11y)
- Seções bloqueadas (CIP, disclaimer)
- Estrutura tool-config + partials-loader

Gate `pre_deploy`: 0 critical, 0 high, 0 erros de validação.

## Agentes

| Agente | Módulo | LLM? |
|--------|--------|------|
| Validação | `validate.py` | Não |
| Correção | `correct.py` | Opcional (`--llm`) |
| Geração | `generate.py` | Opcional (`--draft --llm`) |
