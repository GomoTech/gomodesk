# GomoDesk

Cliente de acesso remoto da **Gomo Tech**, baseado no [RustDesk](https://github.com/rustdesk/rustdesk) (código aberto, AGPL-3.0).

O GomoDesk é o RustDesk com:

- nome, ícone e logo da Gomo Tech;
- servidor de acesso remoto da Gomo Tech (`desk.gomox.com.br`) e sua chave pública já configurados;
- atualização automática para o RustDesk oficial desligada (o GomoDesk é atualizado pelo instalador da Gomo Tech);
- descoberta na rede local desligada.

Ele é instalado nos PCs dos clientes junto com o **GomoDesk Agente**, que informa o ID de acesso e a situação do
computador ao painel **GomoCentral** da Gomo Tech.

## Baixar

Versões compiladas: [Releases](https://github.com/GomoTech/gomodesk/releases).

## Como é feito

Nada do código do RustDesk fica copiado aqui. A compilação (GitHub Actions) baixa o RustDesk na versão indicada
em `marca/marca.json` e aplica as alterações deste repositório:

| Pasta | O que tem |
| --- | --- |
| `marca/marca.json` | nome, empresa, servidor, chave pública, versão do RustDesk e configurações do cliente |
| `marca/preparar.py` | aplica a marca no código do RustDesk (cada troca confere se o texto original existe) |
| `marca/arquivos/` | ícones e logos do GomoDesk |
| `patches/` | ajustes adaptados do [rdgen](https://github.com/bryangerlach/rdgen) (GPL-3.0) |
| `.github/workflows/` | compilação para Windows, baseada no fluxo oficial do RustDesk 1.5.3 e no rdgen |

Para compilar uma versão nova: altere `marca/marca.json` (por exemplo, `versao_rustdesk` ou `revisao`) e envie
para a branch `main`, ou rode **Actions → Compilar GomoDesk (Windows) → Run workflow**.

## Código-fonte e licença

O GomoDesk é distribuído sob a **GNU Affero General Public License v3.0** (veja `LICENSE`), a mesma do RustDesk.
O código-fonte correspondente a cada versão é o RustDesk na versão indicada no release mais as alterações
deste repositório naquele commit.

RustDesk © Purslane Ltd e colaboradores. rdgen © Bryan Gerlach e colaboradores.
GomoDesk e a marca Gomo Tech © Gomo Tech — contato@gomox.com.br — (11) 94745-1702.
