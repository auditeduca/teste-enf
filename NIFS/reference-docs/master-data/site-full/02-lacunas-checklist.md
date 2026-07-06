# Lacunas — o que você pediu vs o que ainda falta

## ✅ Incluído no seu pedido

| Área | Módulo |
|------|--------|
| Simulados | M05 |
| Biblioteca | M06 |
| Artigos | M07 |
| Flashcards | M08 |
| Protocolos | M09 |
| Institucionais | M02 |
| Modulares (hubs) | M03 |
| Design tokens | M10 |
| APIs (NKP) | M12 |

## ⚠️ Você provavelmente está esquecendo

| Área | Por quê | Módulo |
|------|---------|--------|
| **Home** | Hero, SEO, dicas do dia | M01 |
| **Chrome** | Header, footer, mega-menu, cookies LGPD | M11 |
| **100 ferramentas** | Escalas/calculadoras — só APGAR 100% hoje | M04 |
| **Quizzes** | Ligados aos simulados | M05 (parcial) |
| **Mapas mentais + guias de bolso** | content-pending MMP/PKT | content-pending |
| **NANDA/NIC/NOC + trilhas** | Taxonomia clínica | M15 |
| **Medicamentos** | Hub `/medicamentos` | M16 |
| **Calculadoras trabalhistas** | `/calculadoras-trabalhistas` | M17 |
| **SBAR + currículo** | Wizards dedicados | *falta M19* |
| **Empregos + cursos** | Hubs scrape | *falta M20* |
| **i18n 30 idiomas** | Shards ~160k registros | M13 |
| **190 países** | locale-options + countries | M14 |
| **Build minificado** | `generate_website_pt.py` | M18 |
| **SEO/sitemap/hreflang** | Produção multi-locale | *falta M21* |
| **Assets/ícones AST** | Por ferramenta doc 14 | master-data |
| **Evidência Grau A** | Gate antes de published | doc 14 |
| **Aprovação humana doc 14** | entity_codes ainda PENDING_REVIEW | governance |

## Roadmap realista para “1 comando = 100% global”

1. **`--all --no-llm`** — valida estrutura + filas (hoje)
2. **`--all --llm --approve`** — gera content batches (FLA/SIM/PRT…)
3. **Replicar APGAR × 40 SCL** — ferramentas clínicas
4. **M13 + M14** — agente i18n massa (30×190)
5. **M18 build** — site pt-BR minificado
6. **Partições `by-locale/`** — rollout internacional

Sem aprovação humana + Grau A, “100% excelência” clínica **não** deve ir a produção automaticamente.
