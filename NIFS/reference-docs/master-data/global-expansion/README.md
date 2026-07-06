# Expansão Global — Master Data

Programa `GLOBAL_EXPANSION`: cobertura mundial de países, idiomas, fusos horários, páginas regionais e quatro perfis de usuário com conteúdo customizado e evidência **Grau A**.

## Artefatos

| Arquivo | Descrição |
|---------|-----------|
| [`canonical.json`](../../../datasets/master-data/global-expansion/canonical.json) | Política de evidência, perfis, bindings |
| [`territory_timezones.json`](../../../datasets/master-data/global-expansion/territory_timezones.json) | 195 territórios + suplemento multi-fuso (US, BR, CA, …) |
| [`country_pages_registry.json`](../../../datasets/master-data/global-expansion/country_pages_registry.json) | 195 páginas `/regiao/{cc}/` (status `pending` até geração HTML) |
| [`user_profiles_registry.json`](../../../datasets/master-data/global-expansion/user_profiles_registry.json) | 4 perfis × 5 módulos — rotas, datasets, prontidão |
| [`locale_profile_matrix.json`](../../../datasets/master-data/global-expansion/locale_profile_matrix.json) | Perfis customizados por idioma (30 locales) |
| [`coverage_report.json`](../../../datasets/master-data/global-expansion/coverage_report.json) | Métricas de cobertura |

## Perfis de usuário

| Chave | Foco de conteúdo |
|-------|------------------|
| `estudante` | Simulados, flashcards, trilhas, quiz, calculadoras didáticas |
| `profissional` | Escalas, protocolos, calculadoras clínicas, medicamentos |
| `gestor` | Indicadores, staffing, SAE, SBAR, gestão clínica |
| `academico` | Biblioteca, artigos, NANDA/NIC/NOC, referências |

Persistência no site (`website/assets/js/user-profile.js`):

- Perfil: `ce-user-profile-v1`
- Geo (país, locale, fuso): `ce-user-geo-v1`
- Restauração automática em cada página via `restoreProfileFromStorage()` e `restoreGeoFromStorage()`
- Evento `ce:locale-selected` (mega-menu) sincroniza geo com `saveGeo()`

## Evidência Grau A

Busca de agentes prioriza PubMed, Cochrane, WHO e diretrizes internacionais peer-reviewed. Campos obrigatórios: `citation`, `doi_or_url`, `organization`, `year`. Publicação bloqueada se faltar evidência (`block_if_missing: true`).

## Comandos

```bash
# Regenerar registries + perfis + i18n
python scripts/global_expansion/build_registry.py

# Só perfis (4 × 5 módulos)
python scripts/global_expansion/build_user_profiles.py

# Validar (12 checks)
python scripts/global_expansion/validate_global.py

# Orquestrador completo (4 perfis, rebuild, dry-run sem LLM)
python scripts/global_expansion_agents/run_global.py --all --rebuild --no-llm

# Com DeepSeek para conteúdo por perfil
python scripts/global_expansion_agents/run_global.py --all --rebuild --llm
```

## API / Plataforma

- `GET /api/global-expansion/status`
- `POST /api/global-expansion/run`
- UI: `/global-expansion` na plataforma NKP

## Padrão de codificação

Segue doc [14](../../14-master-data-sequencia-revisao.md): `{CONCEITO}_{ARTEFATO}_{NNN}` — ex. `BR_PAGE_001`, `TERR_BR_TZ_001`, `PROFILE_STUDENT_001`.

## Próximos passos

1. Geração HTML das 195 páginas país (pipeline content-pending / site-full M-locales)
2. Tradução massiva i18n com LLM (300+ códigos `I18N_{LANG}_{PAGE}_001`)
3. Carreiras: expandir scaffolds → datasets publicados por país
4. Integrar `validate_global.py` no CI (`run_ci.py`)

## i18n mundial (30 idiomas)

| Artefato | Descrição |
|----------|-----------|
| `i18n_code_registry.json` | 300 códigos (30 langs × 10 tipos de página) |
| `country_audience_preferences.json` | Preferências home/carreira por país |
| `locale_profile_matrix.json` | Perfis customizados por idioma |
| `datasets/by-locale/manifest.json` | 30 locales no build |

Build expande `SITE_LOCALES` e `seo_lib.LOCALES` via `scripts/global_expansion/site_locales.py`.

Runtime: `user-profile.js` aplica perfil + `country-audience.json` conforme geo/locale persistidos.

## Carreiras globais

Ver [master-data/careers/README.md](../careers/README.md) — 780 itens, agentes dedicados, integração na UI `/global-expansion`.
