# Workflow de aprovação

## Fluxo visual

```
Buscar → Gerar → Revisar → Validar → [Aprovar | Rejeitar] → Gravar dataset
```

| Status | Significado |
|--------|-------------|
| `running` | Agentes em execução |
| `awaiting_approval` | Pronto para revisão humana |
| `approved` | Aprovado (transitório) |
| `applied` | Gravado em datasets + backup `_archive_temp` |
| `rejected` | Rejeitado — não grava |

## Modos

- **Individual:** um `pending_id` da fila
- **Em massa:** lote por tipo (FLA, SIM…) com limite 1–20

## Segurança

- Outputs sanitizados — **sem** `api_key`, tokens `sk-*` ou Bearer
- Prompts proíbem credenciais no JSON gerado

## API

| Método | Rota |
|--------|------|
| GET | `/api/content-pending/workflow` |
| POST | `/api/content-pending/workflow/run` |
| POST | `/api/content-pending/workflow/approve` |
| POST | `/api/content-pending/workflow/reject` |
| POST | `/api/content-pending/archive/prepare` |

## Roadmap (30 idiomas × 190 países)

Fase atual: workflow PT + master-data. Próximo: agente M11 i18n (espelho APGAR) + build minificado por locale.
