# Arquitetura de 21 camadas

Modelo interno desta aplicação. Não é nível ISO.

A tabela mestra e o status **deste** v0.1 estão em `data/layers-21.json`.

| Código | Nome | Função | Status v0.1 |
|---|---|---|---|
| 00-foundation | Fundação | HTML5, CSS, JS, schemas | PARTIAL |
| 01-nkos | Núcleo de conhecimento | Objetos clínicos/educacionais | PARTIAL (5 pilotos) |
| 02-nis | Motor | sum / expression | PARTIAL |
| 03-knowledge-graph | Grafo | Relações | SPECIFIED |
| 04-ontology | Ontologia | Vocabulário formal | SPECIFIED |
| 05-terminology | Terminologia | NANDA/NIC/NOC e afins | HOLD |
| 06-knowledge | Base de conhecimento | Claims e conteúdo | PARTIAL |
| 07-evidence | Evidência | Fontes e hashes | PARTIAL |
| 08-assurance | Asseguração | Fail closed | PARTIAL |
| 09-reasoning | Raciocínio | Faixas e SAE | PARTIAL |
| 10-learning | Aprendizado | Quiz / simulado | PARTIAL |
| 11-safety | Segurança | Disclaimer, HOLD | PARTIAL |
| 12-validation-units | Unidades | min/max/step | PARTIAL |
| 13-library-os | Biblioteca | Downloads | SPECIFIED |
| 14-search-discovery | Busca | Catálogo | SPECIFIED |
| 15-product-session | Sessão | Preferências | SPECIFIED |
| 16-offline-export | Export | Print | SPECIFIED |
| 17-designos | Design System | Tokens navy | PARTIAL |
| 18-studio | Studio | Editor | SPECIFIED (inspector only) |
| 19-qa-release | QA | pytest + audit | PARTIAL |
| 20-ai-interop | IA | Agentes | SPECIFIED |

Nenhuma camada está declarada completa para publicação clínica.
