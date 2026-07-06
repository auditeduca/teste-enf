# Site Full — comando único zero→100%

Orquestrador de agentes para **todo o site**, espelhando o piloto APGAR.

## Comando único

```bash
# Listar módulos + lacunas
python scripts/site_agents/run_site_full.py --list

# Zero→100% determinístico (sem LLM)
python scripts/site_agents/run_site_full.py --all --no-llm

# Com DeepSeek + auto-aprovação content + build
python scripts/site_agents/run_site_full.py --all --llm --approve --build

# Só simulados + flashcards
python scripts/site_agents/run_site_full.py --modules M05_simulados,M08_flashcards --llm --bulk-limit 10
```

## Módulos (M01–M18)

| ID | Área |
|----|------|
| M01 | Home |
| M02 | Institucionais |
| M03 | Hubs modulares |
| M04 | Ferramentas clínicas (100) |
| M05 | Simulados |
| M06 | Biblioteca |
| M07 | Artigos |
| M08 | Flashcards |
| M09 | Protocolos |
| M10 | Design tokens (read-only) |
| M11 | Chrome nav/footer |
| M12 | API NKP |
| M13 | i18n 30 idiomas |
| M14 | 190 países |
| M15 | NANDA/NIC/NOC/trilhas |
| M16 | Medicamentos |
| M17 | Calculadoras trabalhistas |
| M18 | Build `website/pt/` |

## App

- Rota: `/site-full`
- API: `POST /api/site-full/run`

Ver [02-lacunas-checklist.md](02-lacunas-checklist.md) — o que você listou **e** o que ainda falta.
