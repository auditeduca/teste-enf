# Memória do módulo — Legislação | Calculadoras de Enfermagem

## Estado atual

**Versão ativa:** `ROLLBACK-v4` / `CKO-Leitor-Regulatorio-Historico-Revertido-v4.zip`

A versão v5 foi **revertida** por solicitação do usuário. O baseline atual volta à v4.

## Princípios não negociáveis

- Produto público: **Calculadoras de Enfermagem**.
- Sequência de governança: **CKO-MD → CKO-REG → camadas especializadas → Projection → Renderer**.
- O Renderer não decide substância jurídica; recebe conteúdo/projeções validadas.
- Não inferir vigência, revogação, aplicabilidade, força normativa, caput, parágrafo, inciso, alínea ou texto jurídico ausente.
- Conteúdo legal integral só entra após aquisição da fonte oficial, evidência, hash e validação.
- Público sem login; estado pessoal (favoritos, leitura, notas) deve permanecer local quando possível.
- Header, footer, idioma e acessibilidade pertencem ao shell de produção e devem ser carregados de forma modular.

## Baseline visual/funcional atual — v4

A v4 recupera o leitor regulatório histórico, incluindo:

- busca global e busca na sidebar;
- 119 artigos na barra lateral, agrupados pelos 5 capítulos;
- cada artigo com nó estrutural `Caput`;
- hierarquia preparada para Preâmbulo → Livro → Título → Capítulo → Seção → Subseção → Artigo → Caput → Parágrafo → Inciso → Alínea → Item → Anexo;
- status de leitura e progresso por artigo;
- modos do reader para texto, alterações, comparação, timeline, relações, fontes e versões (estado da v4 histórica);
- ações por artigo: copiar, citar, link, comentar, salvar, ler depois;
- toolbar de seleção: marcar, sublinhar, comentar, copiar, citar, link do trecho;
- TTS, A-/A+, foco, impressão/PDF, link direto, exportação de notas, cesta e favorito;
- preview contextual e recursos derivados;
- 14 recursos derivados preservados: Checklist, Flashcards, Glossário, Guia de Bolso, Quiz, Slides, Simulado, Infográfico, Mapa Mental, Caso Clínico, Resumo, Questões Comentadas, Podcast e Vídeo.

## Estado epistemológico do Código de Ética no corpus recuperado

- `full_legal_text_status`: texto integral não materializado no corpus recuperado.
- O índice de 119 artigos é **didático**, não a redação legal oficial.
- Nós de `CAPUT` podem existir estruturalmente, mas texto permanece `PENDING_SOURCE_ACQUISITION`.
- Parágrafo/inciso/alínea/item ficam `UNKNOWN_UNTIL_SOURCE_ACQUISITION` até segmentação oficial.

## Cadeia de versões

- **BASE-COREN-v1** — `CKO-COREN-Legislacao-Nacional-v1.zip` — **BASE** — Base nacional do módulo COREN, hubs, índices, templates e seeds. — SHA-256 `cb3d459a0117f8ea901d2ceeb27d73e673c51b9517485beeb754be6c3c494e18`
- **FRONTEND-EXCELENCIA-v1** — `CKO-Legislacao-Frontend-Excelencia-v1.zip` — **BRANCH** — Exploração de front-end/qualidade visual do módulo de legislação. — SHA-256 `5c84109440a373b5f5564a423f24a6f1dfa58a6c8f667438f0e5194a7db22fc9`
- **LEITOR-v1** — `CKO-Legislacao-360-Preview-v1.zip` — **SUPERSEDED** — Primeiro preview 360; posteriormente identificado como não fiel ao HTML/runtime. — SHA-256 `1aed75dfb5f183d3a06ae3c7073004fd5e1fe8010389c911b33219723a46f1d6`
- **LEITOR-v2** — `CKO-Legislacao-360-Integrado-v2.zip` — **SUPERSEDED** — Integração do shell e 14 recursos reais; ainda não recuperava todos os recursos intrínsecos do leitor. — SHA-256 `2d430a62a5791a4992986ba4e5df71aafdb218a270686d06c5ff85be5b1fe1c6`
- **LEITOR-v3** — `CKO-Leitor-Regulatorio-Completo-v3.zip` — **SUPERSEDED** — Leitor regulatório com recursos intrínsecos + recursos derivados; posteriormente revisado contra histórico. — SHA-256 `107d388ea8181c72dae054afc0e152c697d44190e70bf4ae40be440c320698ff`
- **LEITOR-v4** — `CKO-Leitor-Regulatorio-Historico-v4.zip` — **CURRENT_CANONICAL_UI_BASELINE** — Reconstrução sobre baseline histórico: busca, sidebar com 119 artigos, caput, modos de leitura, ações por artigo e toolbar de seleção. — SHA-256 `adeb60fa43bde0290d7e4f41ad7b413132567d864723996eaca8a220d4c59cbd`
- **LEITOR-v5** — `CKO-Leitor-Regulatorio-Historico-v5.zip` — **REVERTED** — Alteração de hero/resumo/badges/progresso/visibilidade; revertida por solicitação do usuário. — SHA-256 `d89e0bf614bb357993258a0afca63171acc7fdc38dc2e0818068d285b7067f43`
- **ROLLBACK-v4** — `CKO-Leitor-Regulatorio-Historico-Revertido-v4.zip` — **CURRENT** — Rollback explícito para a v4; este é o estado atual do módulo nesta conversa. — SHA-256 `89a729c4500a3dc4d8a5b3c4550f96267305aff8c6727438b838ac366ca70fe3`

## Histórico decisório recente

- v1: preview 360 inicial; não foi considerado fiel ao renderer/HTML.
- v2: corrigiu integração do shell e incorporou as 14 páginas de recursos reais.
- v3: recuperou recursos intrínsecos do leitor regulatório.
- v4: nova varredura do histórico; restaurou busca, sidebar com artigos, caput e baseline histórico de 14/08.
- v5: alteração visual/UX posterior.
- rollback v4: usuário solicitou desfazer integralmente a última alteração; **estado atual**.

## Próxima regra de trabalho

Qualquer alteração futura deve gerar nova versão sem sobrescrever as anteriores. O arquivo atual deve permanecer reproduzível por hash.
