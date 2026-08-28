# NIFS Compiler

Gera artefatos em `NIFS/DELIVERY/` a partir de fontes editáveis. **Não edite** arquivos com `"_generated": { "do_not_edit": true }`.

## Fontes editáveis

| Tipo | Caminho |
|------|---------|
| CKO v3 | `NIFS/DELIVERY/js/modules/data/cko/CKO-APGAR-001.json` |
| UI / perfis (particularizador) | `NIFS/DELIVERY/js/modules/data/cko/overlays/CKO-APGAR-ui.json` |
| Datasets globais | `NIFS/reference-datasets/` |
| Ontologia Apgar | `NIFS/reference-datasets/ontology/apgar_edges.json` |

## Artefatos gerados (não editar)

| Artefato | Gerado por |
|----------|------------|
| `js/bundles/clinical-terminology.pt-BR.json` | `compiler/clinical.py` |
| `js/bundles/tools-catalog.json` | `compiler/clinical.py` |
| `js/modules/data/apgar-cko.json` | `compiler/tools/apgar.py` |
| `js/modules/data/apgar-edges.json` | `compiler/tools/apgar.py` |
| `js/bundles/edges-apgar.json` | `compiler/tools/apgar.py` |
| `build-manifest.json` | `compiler/manifest.py` |

## Comandos

```bash
python3 -m compiler.build_all          # tudo
python3 -m compiler.build_tool --tool apgar
python3 -m compiler.verify           # _generated + hashes
bash scripts/ready.sh                # gate completo
```

Wrappers legados em `scripts/` delegam ao compiler.
