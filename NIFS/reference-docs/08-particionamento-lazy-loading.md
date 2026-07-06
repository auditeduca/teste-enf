# Particionamento e lazy loading — Plataforma Admin

Estratégia para reduzir peso de carregamento sem duplicar datasets clínicos globais (NANDA, NIC, NOC).

## Problema

Alguns envelopes são grandes (MasterEntity ~2000, EntityRelation ~5000, translations sharded ~160k). Carregar o JSON inteiro na API e renderizar tudo na UI degrada tempo de resposta e memória.

## Modelo de três camadas

| Camada | Escopo | Entidades | Armazenamento atual | Carregamento |
|--------|--------|-----------|---------------------|--------------|
| **Global** | Compartilhado entre países | MasterEntity, EntityRelation, Asset, Component, Section, PageTemplate | `datasets/master/`, `datasets/metadata/` | Hierarquia lazy (expandir nó → buscar filhos) + paginação 40 |
| **Locale** | Idioma / locale do site | Traduções, home, páginas i18n | `datasets/content/` (translations sharded) | Shard-by-shard via `iter_records()` |
| **Country** | País / jurisdição | ComplianceRule, ContentRequest | `datasets/by-country/{CC}/` | **Exige país** — lê só o arquivo do país (~15–65 registros) |

### País vs idioma

- **Idioma** controla apresentação (pt-BR, en, es…).
- **País** controla conformidade (LGPD→BR, HIPAA→US) e pipeline de conteúdo local.
- Conhecimento clínico NANDA permanece **global**; não duplicar por país.

## Lazy loading — API (`scripts/dataset_io.py`)

```
read_envelope_meta(path)   → só manifesto (count, shard_files)
iter_records(path)         → generator shard-a-shard
paginate_records(...)      → filtro + offset/limit em uma passagem
find_record(path, pk, id)  → GET unitário sem carregar tudo
record_count(path)         → usa campo count do manifesto
```

Endpoints:

- `GET /api/entities/{key}?limit=&offset=&parent=&country=` — paginação lazy
- `GET /api/scopes` — mapa de partições e países suportados
- `GET /api/stats` — contagens via manifesto (sem merge de shards)

## Lazy loading — UI (`platform/`)

| Mecanismo | Onde |
|-----------|------|
| Rotas `React.lazy` | Páginas de módulo carregadas ao navegar |
| Hierarquia fechada | Master Entities — filhos só ao expandir |
| Grupos fechados | Assets, Sections… — expandir grupo |
| Paginação 40 | Lista / grade / detalhes |
| Preview sob demanda | Painel lateral só com item selecionado |
| Escopo país | Reduz Compliance e Content Factory |

- `GET /api/scopes` — mapa de partições (strategy: `physical_v2`)
- `GET /api/scopes/{CC}` — contagens por entidade no país (ex. `/api/scopes/BR`)

## Separação física v2 (implementado)

```
datasets/by-country/
  manifest.json
  BR/
    compliance_rules.json   # LGPD, COFEN, ANVISA, FHIR…
    content_requests.json
  US/
    compliance_rules.json
    content_requests.json
  …
```

Bootstrap (gerar/atualizar partições a partir do global):

```bash
python scripts/bootstrap_country_partitions.py
```

A API resolve o path via `partition_lib.resolve_entity_path()` — fallback para o arquivo global se a partição não existir.

## Separação física v3 — locale (implementado)

```
datasets/by-locale/
  manifest.json
  pt-BR/
    home_page.json
    workflows.json
  en/
    home_page.json      # shell i18n (corpo pt-BR até tradução)
    workflows.json
  es/ … fr/ … de/ … it/ … ja/
```

Bootstrap:

```bash
python scripts/bootstrap_locale_partitions.py
```

Endpoints:

- `GET /api/content/home-preview?locale=pt-BR` — lê só `by-locale/{locale}/home_page.json`
- `GET /api/scopes/locale/en` — metadados da partição locale

A notificação de boas-vindas no dashboard usa o locale do escopo selecionado.

## Separação física v4 — traduções (implementado)

O manifesto global `content/translations.json` tem **160.776** registros em 9 shards (~20k cada). A UI admin **não** carrega mais esse arquivo inteiro.

Bootstrap (executar uma vez ou após regerar traduções):

```bash
python scripts/bootstrap_translation_locales.py
```

Gera `datasets/by-locale/{locale}/translations.json` com ~5,5k registros por idioma do site (7 locales).

Endpoints:

- `GET /api/entities/Translation?locale=en&limit=40` — paginação lazy no arquivo do locale
- `GET /api/translations/summary` — contagens por locale sem scan global

Módulo admin: **Traduções** (`/translations`) — agrupado por `content_scope`, paginação 40.

## Próximo passo (v5)

## Recomendações operacionais

1. Selecionar **país** antes de abrir Compliance ou Content Factory.
2. Master Entities: navegar pela **árvore**, não usar grade em datasets grandes.
3. Relations: preferir busca + tabela paginada; grafo com limite baixo.
4. Reiniciar API após alterações em `nkp_api.py` ou `dataset_io.py`.

## Referências

- [docs/07-plataforma-nkp.md](07-plataforma-nkp.md) — admin React e API
- `scripts/dataset_io.py` — sharding existente (translations)
- `platform/src/lib/dataScopes.js` — metadados espelhados na UI
