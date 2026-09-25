from __future__ import annotations

import argparse
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def pipeline(include_history: bool = False) -> list[list[str]]:
    scripts = [
        "coletar_2006_wikitext.py",
        "coletar_2002_uol.py",
        "coletar_fundamentos.py",
        "preparar_dados.py",
        "ajustes_literatura.py",
        "rodar_modelos.py",
        "avaliar_historico.py",
        "avaliar_janelas.py",
        "avaliar_previsao_viva.py",
        "avaliar_rolling.py",
        "prever.py",
        "bayesiano_dinamico.py",
        "gerar_ensemble.py",
        "gerar_pendencias.py",
    ]
    if include_history:
        scripts.append("registrar_historico_previsoes.py")
    scripts.append("auditar_fontes.py")
    return [[sys.executable, str(ROOT / "scripts" / name)] for name in scripts]


def main() -> None:
    parser = argparse.ArgumentParser(description="Atualiza bases, modelos, testes e HTML do painel.")
    parser.add_argument("--registrar-historico", action="store_true", help="salva uma nova fotografia datada da previsao")
    parser.add_argument("--sem-testes", action="store_true", help="nao roda pytest")
    parser.add_argument("--sem-render", action="store_true", help="nao renderiza o relatorio Quarto")
    args = parser.parse_args()

    commands = pipeline(include_history=args.registrar_historico)
    if not args.sem_testes:
        commands.append([sys.executable, "-m", "pytest", "-q"])
    if not args.sem_render:
        commands.append(["quarto", "render", str(ROOT / "reports" / "relatorio-modelo-eleitoral.qmd"), "--to", "html"])

    for command in commands:
        print("$ " + " ".join(command), flush=True)
        subprocess.run(command, cwd=ROOT, check=True)


if __name__ == "__main__":
    main()
