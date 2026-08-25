# Estrutura de diretórios

Árvore desta aplicação:

- `/docs/constitution` — constituição operacional
- `/cko_core` `/cko_md` `/cko_reg` `/cko_assurance` — registries Day Zero
- `/engine` — lógica canônica, bootstrap, renderer e CLI (`bootstrap`, `validate`, `build`, `audit`, `serve`)
- `/validators` — schema (via engine), completude clínica, paridade dual-render, release gate
- `/schemas` — contratos Draft-07 (tool, regulatory event, trust, evidence, capability, release)
- `/templates` — resource contracts e cópia dos tokens
- `/data` — catálogo, camadas 21 (corte de produto), changesets, candidatos em `data/tools`
- `/regulatory` — Regulatory Core e lineage (vazio de snapshots no v0.1)
- `/past-exams` — fábrica de provas (especificada)
- `/monitoring` — monitor regulatório (especificado)
- `/admin` — contrato admin↔frontend; superfícies geradas em `render/*/admin.html` e `inspector.html`
- `/assets` — CSS/JS locais
- `/public` — `output.css` gerado
- `/render/inline` — preview com CSS embutido
- `/render/fetch` — produção com CSS via link first-party
- `/audit` — trilha, 360 e release manifest gerados
- `/reports` — estado atual gerado
- `/integrated` — pacote de release futuro
- `/docs` — esta documentação
- `/tests` — pytest

Não há runtime fora desses diretórios.
