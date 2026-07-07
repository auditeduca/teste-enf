# Calculator Agents

Agentes para **validação**, **correção** e **geração** de páginas de calculadoras/escalas.

## APIs suportadas

Carregamento de `.env` (em ordem):

1. Variáveis já definidas no ambiente
2. `/workspace/.env`
3. `/workspace/NIFS/.env`
4. `CALENF_ENV_FILE` (caminho customizado)
5. `C:/Github/CALENF-NKD/.env` (legado Windows)

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

# Validar todas as calculadoras em NIFS/DELIVERY/html
python -m scripts.calculator_agents validate

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
```

## Agentes

| Agente | Módulo | LLM? |
|--------|--------|------|
| Validação | `validate.py` | Não |
| Correção | `correct.py` | Opcional (`--llm`) |
| Geração | `generate.py` | Opcional (`--draft --llm`) |
