import argparse
import json
import sys

from .scoring import CAPS, evaluate
from . import state, integrations


def build_parser():
    parser = argparse.ArgumentParser(prog="prompt-roast", description="Feedback local sobre a clareza de prompts.")
    commands = parser.add_subparsers(dest="command", required=True)
    commands.add_parser("hook", help=argparse.SUPPRESS)
    evaluation = commands.add_parser("evaluate", help="Calcular uma nota sem gravar histórico")
    evaluation.add_argument("--type", choices=("request", "question"), required=True)
    for number in range(1, 4):
        evaluation.add_argument(f"--p{number}", type=int, choices=range(4), required=True)
    evaluation.add_argument("--pattern", choices=CAPS, default="none")
    evaluation.add_argument("--butler", action="store_true")
    session = commands.add_parser("session", help="Criar uma sessão isolada")
    session_commands = session.add_subparsers(dest="session_command", required=True)
    new = session_commands.add_parser("new")
    new.add_argument("--agent", choices=state.AGENTS, required=True)
    new.add_argument("--project", default=".")
    record = commands.add_parser("record", help="Registrar avaliação em uma sessão")
    record.add_argument("--agent", choices=state.AGENTS, required=True)
    record.add_argument("--project", default=".")
    record.add_argument("--session", required=True)
    record.add_argument("--event", required=True)
    record.add_argument("--type", choices=("request", "question"), required=True)
    for number in range(1, 4):
        record.add_argument(f"--p{number}", type=int, choices=range(4), required=True)
    record.add_argument("--pattern", choices=CAPS, default="none")
    record.add_argument("--butler", action="store_true")
    score = commands.add_parser("score", help="Mostrar estatísticas da sessão")
    score.add_argument("--agent", choices=state.AGENTS, required=True)
    score.add_argument("--project", default=".")
    score.add_argument("--session", required=True)
    for name in ("reset", "savage"):
        command = commands.add_parser(name, help="Alterar a sessão atual")
        if name == "savage":
            command.add_argument("mode", choices=("on", "off"))
        command.add_argument("--agent", choices=state.AGENTS, required=True)
        command.add_argument("--project", default=".")
        command.add_argument("--session", required=True)
    for name in ("install", "uninstall", "doctor", "setup-local", "setup-global"):
        command = commands.add_parser(name, help="Gerenciar integração com agentes")
        command.add_argument("--agent", choices=(*state.AGENTS, "all"), required=True)
        if name in ("install", "uninstall", "doctor"):
            command.add_argument("--scope", choices=("local", "global"), required=True)
        command.add_argument("--project", default=".")
    return parser


def main():
    args = build_parser().parse_args()
    try:
        if args.command == "hook":
            import os
            from pathlib import Path
            root = os.environ.get("CLAUDE_PLUGIN_ROOT")
            if not root:
                raise ValueError("CLAUDE_PLUGIN_ROOT ausente")
            print(f"Aplique a skill PromptRoast às mensagens elegíveis. Leia {Path(root) / 'skills/prompt-roast/SKILL.md'}. Execute python3 '{Path(root) / 'runtime/prompt-roast.pyz'}'; agente claude.")
            return
        if args.command == "evaluate":
            result = evaluate(args.type, args.p1, args.p2, args.p3, args.pattern, args.butler)
        elif args.command in ("install", "setup-local", "setup-global"):
            scope = args.scope if args.command == "install" else args.command.removeprefix("setup-")
            result = integrations.install(args.agent, scope, args.project)
        elif args.command == "doctor":
            result = integrations.doctor(args.agent, args.scope, args.project)
        elif args.command == "uninstall":
            result = integrations.uninstall(args.agent, args.scope, args.project)
        elif args.command == "reset":
            result = state.reset(args.agent, args.project, args.session)
        elif args.command == "savage":
            result = state.savage(args.agent, args.project, args.session, args.mode == "on")
        elif args.command == "score":
            result = state.statistics(args.agent, args.project, args.session)
        elif args.command == "record":
            assessment = evaluate(args.type, args.p1, args.p2, args.p3, args.pattern, args.butler)
            result = state.record(args.agent, args.project, args.session, args.event, assessment)
        elif args.command == "session":
            result = state.new_session(args.agent, args.project)
        print(json.dumps(result, ensure_ascii=False))
    except (ValueError, OSError) as exc:
        print(f"Erro: {exc}", file=sys.stderr)
        raise SystemExit(1) from exc
