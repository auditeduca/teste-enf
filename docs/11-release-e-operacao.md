# Release e operação

## Pré-release

1. Validar JSONs (`engine.cli validate`).
2. Validar Python (`pytest`).
3. Verificar links relativos no HTML gerado.
4. Confirmar zero CDN no modo fetch.
5. Validar dual-render parity.
6. Rodar auditoria 360 (`engine.cli audit`).
7. Validar hash chain dos objetos.
8. Gerar release manifest.

## Produção

1. Publicar o pacote `render/fetch`.
2. Confirmar shell real.
3. Confirmar assets first-party.
4. QA de browser.
5. Verificar console/network.
6. Promover somente após gates humanos.

## Atualizações

Usar `VERSION_ON_CHANGE`. Nunca regenerar o canônico por rotina.

No v0.1 o manifest sai **HOLD**: completude SAE, thread regulatório e gates humanos não estão PASS.
