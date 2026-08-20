# Criar o repositório GitHub `auditeduca/nis`

Este Cloud Agent **não consegue criar** um repositório GitHub novo: o token está limitado a `auditeduca/teste-enf`.

## Passos

1. No GitHub, na organização `auditeduca`, crie o repositório **`nis`**.
2. Deixe-o **vazio** (sem README, sem `.gitignore`, sem licença).
3. Privado é o recomendado até a licença NIFS estar definida.
4. Avise o agente (ou rode localmente):

```bash
git remote add nis https://github.com/auditeduca/nis.git
git push -u nis cursor/nis-greenfield-cd31:main
```

Arquivos canônicos deste start (o restante de `teste-enf` é legado):

- `README.md`, `AGENTS.md`, `CONTRIBUTING.md`, `LICENSE`, `pyproject.toml`, `.gitignore`
- `.cursor/environment.json`
- `.github/`
- `data/`
- `packages/`
- `apps/web/`
- `docs/`

## Alternativa

Mesclar este PR em `teste-enf` e tratar `teste-enf` como o repositório canônico, ignorando `reference-website/` e o dump NIFS no dia a dia.
