#!/usr/bin/env python3
"""Aplica a marca GomoDesk no código-fonte do RustDesk antes de compilar.

Uso (na raiz do código do RustDesk):
    python <repo>/marca/preparar.py --marca <repo>/marca [--saida-env $GITHUB_ENV]

Faz:
  1. nome do programa, empresa e links (arquivos de recurso do Windows, Cargo.toml, telas);
  2. servidor e chave pública padrão (libs/hbb_common/src/config.rs);
  3. ícones e logos (res/, flutter/assets/, ícone do executável);
  4. libera o arquivo de configuração do cliente (custom_.txt) e remove avisos do RustDesk oficial
     (patches em ../patches, adaptados do rdgen — GPL-3);
  5. gera custom_.txt (configuração do cliente em base64) na pasta atual.

Cada troca confere se o texto original existe: se o RustDesk mudar, a compilação para com um erro
claro em vez de gerar um cliente pela metade.
"""
import argparse
import base64
import json
import re
import shutil
import subprocess
import sys
from pathlib import Path

RAIZ = Path.cwd()


def falhar(msg: str) -> None:
    sys.exit(f"ERRO ao aplicar a marca: {msg}")


def trocar(arquivo: str, antigo: str, novo: str, obrigatorio: bool = True, regex: bool = False, todas: bool = True):
    p = RAIZ / arquivo
    if not p.exists():
        if obrigatorio:
            falhar(f"arquivo não encontrado: {arquivo}")
        return 0
    texto = p.read_text(encoding="utf-8")
    if regex:
        novo_texto, n = re.subn(antigo, novo, texto, count=0 if todas else 1)
    else:
        n = texto.count(antigo)
        novo_texto = texto.replace(antigo, novo) if todas else texto.replace(antigo, novo, 1)
    if n == 0 and obrigatorio:
        falhar(f"texto não encontrado em {arquivo}: {antigo!r}")
    if n:
        p.write_text(novo_texto, encoding="utf-8")
    print(f"  {arquivo}: {n} troca(s) de {antigo[:60]!r}")
    return n


def copiar(origem: Path, destino: str) -> None:
    d = RAIZ / destino
    d.parent.mkdir(parents=True, exist_ok=True)
    shutil.copyfile(origem, d)
    print(f"  {destino} <- {origem.name}")


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--marca", required=True, type=Path)
    ap.add_argument("--saida-env", type=Path, help="arquivo GITHUB_ENV para exportar variáveis")
    a = ap.parse_args()
    m = json.loads((a.marca / "marca.json").read_text(encoding="utf-8"))
    arq = a.marca / "arquivos"
    patches = a.marca.parent / "patches"
    nome, prefixo, empresa = m["nome"], m["prefixo"], m["empresa"]

    if not (RAIZ / "libs/hbb_common/src/config.rs").exists():
        falhar("rode na raiz do código do RustDesk (com os submódulos).")

    print("1. Nome, empresa e links")
    for cargo in ("Cargo.toml", "libs/portable/Cargo.toml"):
        trocar(cargo, 'description = "RustDesk Remote Desktop"', f'description = "{nome}"')
        trocar(cargo, 'ProductName = "RustDesk"', f'ProductName = "{nome}"')
        trocar(cargo, 'FileDescription = "RustDesk Remote Desktop"', f'FileDescription = "{nome}"')
        trocar(cargo, 'OriginalFilename = "rustdesk.exe"', f'OriginalFilename = "{nome}.exe"')
        trocar(cargo, "Purslane Tech Pte. Ltd.", empresa, obrigatorio=False)
        trocar(cargo, "Purslane Ltd", empresa, obrigatorio=False)
    trocar("libs/portable/src/main.rs", 'const APP_PREFIX: &str = "rustdesk";', f'const APP_PREFIX: &str = "{prefixo}";')
    rc = "flutter/windows/runner/Runner.rc"
    trocar(rc, '"RustDesk Remote Desktop"', f'"{nome}"')
    trocar(rc, '"rustdesk.exe"', f'"{nome}.exe"', obrigatorio=False)
    trocar(rc, '"RustDesk"', f'"{nome}"', obrigatorio=False)
    trocar(rc, "Purslane Tech Pte. Ltd.", empresa, obrigatorio=False)
    trocar(rc, "Purslane Ltd", empresa, obrigatorio=False)
    for f in ("flutter/lib/desktop/pages/desktop_setting_page.dart", "src/main.rs"):
        trocar(f, "Purslane Tech Pte. Ltd.", empresa, obrigatorio=False)
        trocar(f, "Purslane Ltd", empresa, obrigatorio=False)
    trocar("flutter/lib/common.dart", "launchUrl(Uri.parse('https://rustdesk.com'));",
           f"launchUrl(Uri.parse('{m['site']}'));", obrigatorio=False)
    trocar("flutter/lib/desktop/pages/desktop_setting_page.dart", "launchUrlString('https://rustdesk.com');",
           f"launchUrlString('{m['site']}');", obrigatorio=False)
    for f in ("flutter/lib/desktop/pages/desktop_home_page.dart", "flutter/lib/mobile/pages/connection_page.dart"):
        trocar(f, "https://rustdesk.com/download", m["pagina_download"], obrigatorio=False)
    # aviso de "nova versão do RustDesk" (levaria ao download do RustDesk oficial)
    trocar("flutter/lib/desktop/pages/desktop_home_page.dart", "updateUrl.isNotEmpty", "false")

    print("2. Servidor e chave pública padrão")
    cfg = "libs/hbb_common/src/config.rs"
    trocar(cfg, '"rs-ny.rustdesk.com"', f'"{m["servidor"]}"')
    trocar(cfg, r'pub const RS_PUB_KEY: &str = "[^"]*";', f'pub const RS_PUB_KEY: &str = "{m["chave_publica"]}";', regex=True)
    porta = int(m.get("porta", 21116))
    for nome_const, valor in (("RENDEZVOUS_PORT", porta), ("RELAY_PORT", porta + 1),
                              ("WS_RENDEZVOUS_PORT", porta + 2), ("WS_RELAY_PORT", porta + 3)):
        trocar(cfg, rf"pub const {nome_const}: i32 = \d+;", f"pub const {nome_const}: i32 = {valor};", regex=True)

    print("3. Ícones e logos")
    for f in ("icon.png", "mac-icon.png", "icon.ico", "tray-icon.ico", "32x32.png", "64x64.png", "128x128.png",
              "128x128@2x.png"):
        copiar(arq / f, f"res/{f}")
    copiar(arq / "app_icon.ico", "flutter/windows/runner/resources/app_icon.ico")
    copiar(arq / "icon.svg", "flutter/assets/icon.svg")
    copiar(arq / "icon_asset.png", "flutter/assets/icon.png")
    copiar(arq / "logo_light.png", "flutter/assets/logo_light.png")
    copiar(arq / "logo_dark.png", "flutter/assets/logo_dark.png")
    b64 = base64.b64encode((arq / "ui_128.png").read_bytes()).decode()
    trocar("src/ui.rs", r"iVBORw0KGgoAAAANSUhEUgAAAIAAAACACAYAAADDPmHL[A-Za-z0-9+/=]+", b64, regex=True, obrigatorio=False)

    print("4. Patches (adaptados do rdgen, GPL-3)")
    r = subprocess.run([sys.executable, str(patches / "allowCustom.py")], cwd=RAIZ)
    if r.returncode != 0:
        falhar("allowCustom.py não aplicou")
    r = subprocess.run(["git", "apply", str(patches / "removeSetupServerTip.diff")], cwd=RAIZ)
    if r.returncode != 0:
        falhar("removeSetupServerTip.diff não aplicou")

    print("5. Configuração do cliente (custom_.txt)")
    conteudo = base64.b64encode(json.dumps(m["configuracao_cliente"], ensure_ascii=True).encode("ascii")).decode()
    (RAIZ / "custom_.txt").write_text(conteudo, encoding="ascii")
    print("  custom_.txt gerado")

    if a.saida_env:
        with open(a.saida_env, "a", encoding="utf-8") as f:
            f.write(f"APP_NOME={nome}\nVERSAO_RUSTDESK={m['versao_rustdesk']}\n"
                    f"VERSAO_GOMODESK={m['versao_rustdesk']}-g{m.get('revisao', 1)}\n")
    print("Marca aplicada.")


if __name__ == "__main__":
    main()
