# Contribuir

1. Identidade nova: registrar em MD (`business_key`) antes de REG e antes de `data/tools`.
2. Candidatos de domínio: `data/tools/{slug}.json`.
3. Depois de editar JSON: `python3 -m engine.cli bootstrap` e `python3 -m engine.cli build`.
4. Não editar `render/**` na mão.
5. Não marcar `published` sem evidência e aprovador.
6. Não introduzir CDN. Não inventar UUID/hash/cláusula.
7. Admin não grava fórmula. Frontend não grava canônico.
8. Testes em `tests/`.
9. Changesets em `data/changesets/`.
