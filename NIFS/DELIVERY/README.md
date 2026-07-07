# Calculadoras de Enfermagem — DELIVERY

Bundle pronto para publicação estática.

## Estrutura

```
NIFS/DELIVERY/
├── index.html          # páginas na raiz (produção)
├── imc.html
├── css/
├── js/
├── partials/
├── html/               # fonte espelhada (opcional, dev)
└── manifest.json
```

## Deixar tudo pronto (um comando)

```bash
bash scripts/ready.sh
```

Isso executa: publicar HTML → orquestrador de segurança → validação → status APIs.

## Preview local

```bash
cd NIFS/DELIVERY
python3 -m http.server 8765
# http://localhost:8765/imc.html
```

## APIs (opcional)

```bash
cp .env.example .env
# Edite DEEPSEEK_API_KEY=...
```

Windows: use `C:\Github\CALENF-NKD\.env` — detectado automaticamente.

## Agentes

```bash
python -m scripts.calculator_agents orchestrate --mode pre_deploy
python -m scripts.calculator_agents validate
python -m scripts.calculator_agents correct imc --llm
```

Ver `scripts/calculator_agents/README.md`.
