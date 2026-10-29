"""Instalação reversível de recursos e instruções dos agentes."""
import hashlib
import json
import os
from pathlib import Path
import tempfile

START = b"<!-- prompt-roast:start -->"
END = b"<!-- prompt-roast:end -->"


def digest(data):
    return hashlib.sha256(data).hexdigest()


def check_path(path):
    path = Path(path).absolute()
    for part in (path, *path.parents):
        if part.is_symlink():
            raise ValueError(f"link simbólico não é permitido no destino: {part}")
    return path


def block_content(old, block):
    if old.count(START) != old.count(END) or old.count(START) > 1:
        raise ValueError("marcadores PromptRoast inválidos ou duplicados")
    if old.count(START):
        start = old.index(START)
        end = old.index(END) + len(END)
        if end <= start:
            raise ValueError("ordem dos marcadores PromptRoast inválida")
        return old[:start] + block + old[end:]
    separator = b"\n" if old and not old.endswith(b"\n") else b""
    return old + separator + block + b"\n"


def remove_block(old, expected, separator_added=False, before_hash=None):
    if old.count(START) != 1 or old.count(END) != 1:
        raise ValueError("marcadores PromptRoast inválidos ou ausentes")
    start, end = old.index(START), old.index(END) + len(END)
    if end <= start or old[start:end] != expected:
        raise ValueError("bloco PromptRoast foi modificado")
    # Remove apenas o bloco; não modificar regras escritas pelo usuário.
    suffix = old[end + 1:] if old[end:end + 1] == b"\n" else old[end:]
    prefix = old[:start]
    if separator_added and prefix.endswith(b"\n") and digest(prefix[:-1]) == before_hash:
        prefix = prefix[:-1]
    return prefix + suffix


def atomic_write(path, data):
    path = check_path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    check_path(path)
    fd, temp = tempfile.mkstemp(prefix=".prompt-roast-", dir=path.parent)
    try:
        if path.exists() and hasattr(os, "fchmod"):
            os.fchmod(fd, path.stat().st_mode & 0o777)
        with os.fdopen(fd, "wb") as out:
            out.write(data)
            out.flush()
            os.fsync(out.fileno())
        os.replace(temp, path)
    finally:
        if os.path.exists(temp):
            os.unlink(temp)


def load_manifest(path):
    path = check_path(path)
    if not path.exists():
        return {"version": 1, "files": {}, "agents": []}
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (ValueError, UnicodeError) as exc:
        raise ValueError("manifesto inválido; instalação preservada") from exc
    if not isinstance(data, dict) or data.get("version") != 1 or not isinstance(data.get("files"), dict) or not isinstance(data.get("agents"), list):
        raise ValueError("manifesto inválido; instalação preservada")
    return data


def save_manifest(path, data):
    atomic_write(path, json.dumps(data, ensure_ascii=False, indent=2).encode())


def _layout(agent, scope, project, runtime, skill_text, framework, package=b""):
    import shlex
    import sys
    from .state import AGENTS
    if agent not in AGENTS or scope not in ("local", "global"):
        raise ValueError("agente ou escopo inválido")
    home = Path.home()
    base = Path(project).expanduser().absolute() if scope == "local" else home
    global_scope = scope == "global"
    shared = home / ".agents/skills/prompt-roast" if global_scope else base / ".agents/skills/prompt-roast"
    invocation = f"{shlex.quote(sys.executable)} {shlex.quote(str(runtime))}"
    command_instruction = f"O comando Python é `{invocation}`."
    if sys.platform == "win32":
        ps_python = "'" + sys.executable.replace("'", "''") + "'"
        ps_runtime = "'" + str(runtime).replace("'", "''") + "'"
        command_instruction = f"No PowerShell execute `& {ps_python} {ps_runtime}`; no Git Bash execute `{invocation}`."
    rule = (f"Aplique a skill PromptRoast a cada resposta elegível. Leia {shared / 'SKILL.md'}. "
            f"{command_instruction} Agente: `{agent}`. Não avalie comandos administrativos ou saudações.")
    block = START + b"\n" + rule.encode() + b"\n" + END
    entries = {
        shared / "SKILL.md": (skill_text, "file"),
        shared / "references/framework.md": (framework, "file"),
    }
    operations = {"score": "consultar as estatísticas", "reset": "limpar as estatísticas desta sessão", "help": "explicar os comandos", "savage-on": "ativar o modo savage", "savage-off": "desativar o modo savage", "setup-global": "configurar a instalação global", "setup-local": "configurar a instalação local"}
    if agent == "codex":
        for operation, description in operations.items():
            name = "prompt-roast-" + operation
            action = operation.replace("savage-", "savage ")
            content = f"---\nname: {name}\ndescription: Use para {description} do PromptRoast.\n---\n\nLeia {shared / 'SKILL.md'} e execute a operação `{action}` para a sessão atual. {command_instruction}\n"
            entries[shared.parent / name / "SKILL.md"] = (content.encode(), "file")
        config = Path(os.environ.get("CODEX_HOME", home / ".codex")) if global_scope else base
        entries[config / "AGENTS.md"] = (block, "block")
    elif agent == "claude":
        config = home / ".claude" if global_scope else base / ".claude"
        entries[(config if global_scope else base) / "CLAUDE.md"] = (block, "block")
        for operation in ("score", "reset", "help", "setup-global", "setup-local", "savage", "savage-on", "savage-off"):
            content = f"---\ndescription: PromptRoast {operation}\n---\n\nLeia {shared / 'SKILL.md'} e execute a operação `{operation.replace("savage-", "savage ")}`. {rule}\n"
            entries[config / "commands/prompt-roast" / (operation + ".md")] = (content.encode(), "file")
    elif agent == "gemini":
        config = home / ".gemini" if global_scope else base / ".gemini"
        entries[(config if global_scope else base) / "GEMINI.md"] = (block, "block")
        for operation in ("score", "reset", "help", "setup-global", "setup-local", "savage", "savage-on", "savage-off"):
            instruction = f"Leia {shared / 'SKILL.md'} e execute a operação {operation.replace("savage-", "savage ")}. Argumentos: {{{{args}}}}. {rule}"
            content = "description = " + json.dumps("PromptRoast " + operation, ensure_ascii=False) + "\nprompt = " + json.dumps(instruction, ensure_ascii=False) + "\n"
            entries[config / "commands/prompt-roast" / (operation + ".toml")] = (content.encode(), "file")
    elif agent == "cursor":
        commands = (home if global_scope else base) / ".cursor/commands"
        for operation, description in operations.items():
            action = operation.replace("savage-", "savage ")
            content = f"Leia {shared / 'SKILL.md'} e execute `{action}` para {description} do PromptRoast. {rule}\n"
            entries[commands / ("prompt-roast-" + operation + ".md")] = (content.encode(), "file")
        if not global_scope:
            content = f"---\ndescription: Avaliação PromptRoast\nalwaysApply: true\n---\n\n{rule}\n"
            entries[base / ".cursor/rules/prompt-roast.mdc"] = (content.encode(), "file")
    elif agent == "antigravity":
        if global_scope:
            shared = home / ".gemini/config/skills/prompt-roast"
            entries = {shared / "SKILL.md": (skill_text, "file"), shared / "references/framework.md": (framework, "file")}
            rule = (f"Aplique a skill PromptRoast a cada resposta elegível. Leia {shared / 'SKILL.md'}. "
                    f"O comando Python é `{invocation}`; agente: `antigravity`. Não avalie comandos administrativos ou saudações.")
        workflows = home / ".gemini/config/global_workflows" if global_scope else base / ".agents/workflows"
        for operation, description in operations.items():
            action = operation.replace("savage-", "savage ")
            content = f"---\ndescription: PromptRoast - {description}\n---\n\nLeia {shared / 'SKILL.md'} e execute `{action}`. {rule}\n"
            entries[workflows / ("prompt-roast-" + operation + ".md")] = (content.encode(), "file")
        rules = home / ".gemini/config/rules" if global_scope else base / ".agents/rules"
        entries[rules / "prompt-roast.md"] = (f"---\ntrigger: always_on\ndescription: Avaliação PromptRoast\n---\n\n{rule}\n".encode(), "file")
    # Bundles nativos são alternativas à configuração gerenciada por arquivos.
    if agent in ("codex", "claude", "gemini"):
        bundle = runtime.parent.parent / "bundles" / agent / "prompt-roast"
        bundle_skill = bundle / "skills/prompt-roast"
        entries[bundle_skill / "SKILL.md"] = (skill_text, "file")
        entries[bundle_skill / "references/framework.md"] = (framework, "file")
        entries[bundle / "runtime/prompt-roast.pyz"] = (package, "file")
        from importlib.resources import files
        licenses = files("prompt_roast").joinpath("assets", "licenses")
        for filename in ("LICENSE", "THIRD_PARTY_NOTICES.md"):
            entries[bundle / filename] = (licenses.joinpath(filename).read_bytes(), "file")
        metadata = {"name": "prompt-roast", "version": "0.1.0", "description": "Feedback local sobre a clareza de prompts", "author": {"name": "PromptRoast Contributors"}}
        if agent == "codex":
            portable = {"$schema": "https://agent-plugins.org/schemas/1.0.0/plugin.schema.json", **metadata}
            codex = {**metadata, "skills": "./skills/", "interface": {"displayName": "PromptRoast", "shortDescription": "Feedback para prompts", "longDescription": "Avalia a clareza dos prompts com feedback local.", "developerName": "PromptRoast Contributors", "category": "Productivity", "capabilities": [], "defaultPrompt": "Mostre as notas desta sessão."}}
            entries[bundle / "plugin.json"] = (json.dumps(portable, ensure_ascii=False, indent=2).encode(), "file")
            entries[bundle / ".codex-plugin/plugin.json"] = (json.dumps(codex, ensure_ascii=False, indent=2).encode(), "file")
        elif agent == "claude":
            entries[bundle / ".claude-plugin/plugin.json"] = (json.dumps(metadata, ensure_ascii=False, indent=2).encode(), "file")
            for operation in ("score", "reset", "help", "setup-global", "setup-local", "savage", "savage-on", "savage-off"):
                content = f"---\ndescription: PromptRoast {operation}\n---\n\nLeia ${{CLAUDE_PLUGIN_ROOT}}/skills/prompt-roast/SKILL.md e execute `{operation.replace("savage-", "savage ")}` com `python3 \"${{CLAUDE_PLUGIN_ROOT}}/runtime/prompt-roast.pyz\"`.\n"
                entries[bundle / "commands" / (operation + ".md")] = (content.encode(), "file")
            hooks = {"hooks": {"SessionStart": [{"matcher": "*", "hooks": [{"type": "command", "command": "python3 \"${CLAUDE_PLUGIN_ROOT}/runtime/prompt-roast.pyz\" hook"}]}]}}
            entries[bundle / "hooks/hooks.json"] = (json.dumps(hooks, indent=2).encode(), "file")
        else:
            gemini = {"name": "prompt-roast", "version": "0.1.0", "contextFileName": "GEMINI.md"}
            entries[bundle / "gemini-extension.json"] = (json.dumps(gemini, indent=2).encode(), "file")
            entries[bundle / "GEMINI.md"] = (rule.encode(), "file")
            for operation in ("score", "reset", "help", "setup-global", "setup-local", "savage", "savage-on", "savage-off"):
                instruction = f"Leia {shared / 'SKILL.md'} e execute a operação {operation.replace("savage-", "savage ")}. Argumentos: {{{{args}}}}. {rule}"
                content = "description = " + json.dumps("PromptRoast " + operation, ensure_ascii=False) + "\nprompt = " + json.dumps(instruction, ensure_ascii=False) + "\n"
                entries[bundle / "commands/prompt-roast" / (operation + ".toml")] = (content.encode(), "file")
    return entries, rule


def _resources():
    from importlib.resources import files
    assets = files("prompt_roast").joinpath("assets", "skill")
    return (assets.joinpath("SKILL.md").read_bytes(), assets.joinpath("references", "framework.md").read_bytes())


def _paths(scope, project):
    if scope == "local":
        project = check_path(Path(project).expanduser().absolute())
        if not project.is_dir():
            raise ValueError("projeto local deve ser um diretório existente")
        root = project / ".prompt-roast"
    elif scope == "global":
        root = Path(os.environ.get("XDG_DATA_HOME", Path.home() / ".local/share")) / "prompt-roast"
    else:
        raise ValueError("escopo deve ser local ou global")
    root = check_path(root)
    return root, root / "manifest.json", root / "runtime/prompt-roast.pyz"


def install(agent, scope, project="."):
    from .runtime import build_runtime
    from .state import AGENTS, state_root
    root, manifest_path, runtime = _paths(scope, project)
    selected = list(AGENTS) if agent == "all" else [agent]
    if any(item not in AGENTS for item in selected):
        raise ValueError("agente desconhecido")
    manifest = load_manifest(manifest_path)
    skill, framework = _resources()
    agents = sorted(set(manifest["agents"]) | set(selected))
    with tempfile.TemporaryDirectory() as temp:
        package = build_runtime(Path(temp) / "prompt-roast.pyz").read_bytes()
    entries = {}
    rules = {}
    for item in agents:
        layout, rule = _layout(item, scope, project, runtime, skill, framework, package)
        rules[item] = rule
        for path, (content, kind) in layout.items():
            path = check_path(path)
            key = str(path)
            if key in entries:
                if entries[key]["content"] != content or entries[key]["kind"] != kind:
                    raise ValueError(f"conflito de recursos entre agentes: {path}")
                entries[key]["owners"].append(item)
            else:
                entries[key] = {"content": content, "kind": kind, "owners": [item]}
    entries[str(runtime)] = {"content": package, "kind": "file", "owners": agents}
    planned = {}
    for key, entry in entries.items():
        path = check_path(key)
        old_meta = manifest["files"].get(key)
        current = path.read_bytes() if path.exists() else b""
        if entry["kind"] == "block":
            if path.exists() and START in current:
                if not old_meta:
                    raise ValueError(f"bloco não gerenciado já existe: {path}")
                start, end = current.index(START), current.index(END) + len(END) if END in current else -1
                if end < start or digest(current[start:end]) != old_meta.get("hash"):
                    raise ValueError(f"bloco gerenciado modificado ou inválido: {path}")
            planned[key] = block_content(current, entry["content"])
        else:
            if path.exists() and (not old_meta or digest(current) != old_meta.get("hash")):
                raise ValueError(f"arquivo existente não gerenciado ou modificado: {path}")
            planned[key] = entry["content"]
    new_files = {}
    for key, entry in entries.items():
        new_files[key] = {"kind": entry["kind"], "hash": digest(entry["content"]), "owners": entry["owners"]}
        if entry["kind"] == "block":
            old_meta = manifest["files"].get(key)
            current = Path(key).read_bytes() if Path(key).exists() else b""
            if old_meta:
                new_files[key]["separator_added"] = old_meta.get("separator_added", False)
                new_files[key]["before_hash"] = old_meta.get("before_hash")
            else:
                new_files[key]["separator_added"] = bool(current and not current.endswith(b"\n"))
                new_files[key]["before_hash"] = digest(current)
    for key, content in planned.items():
        atomic_write(Path(key), content)
    save_manifest(manifest_path, {"version": 1, "scope": scope, "agents": agents, "files": new_files})
    pending = ["Cursor: cadastre nas User Rules: " + rules["cursor"]] if "cursor" in selected and scope == "global" else []
    return {"prepared": selected, "scope": scope, "runtime": str(runtime), "state_dir": str(state_root()),
            "paths": sorted(entries), "pending": pending, "host_tested": False}


def uninstall(agent, scope, project="."):
    from .state import AGENTS
    root, manifest_path, runtime = _paths(scope, project)
    manifest = load_manifest(manifest_path)
    selected = list(AGENTS) if agent == "all" else [agent]
    if any(item not in AGENTS for item in selected):
        raise ValueError("agente desconhecido")
    if any(item not in AGENTS for item in manifest["agents"]):
        raise ValueError("manifesto contém agente desconhecido; instalação preservada")
    skill, framework = _resources()
    allowed = {str(runtime)}
    for item in manifest["agents"]:
        layout, _ = _layout(item, scope, project, runtime, skill, framework)
        allowed.update(str(check_path(path)) for path in layout)
    if set(manifest["files"]) - allowed:
        raise ValueError("manifesto contém destino desconhecido; instalação preservada")
    for key, meta in manifest["files"].items():
        if (not isinstance(meta, dict) or meta.get("kind") not in ("file", "block")
                or not isinstance(meta.get("owners"), list)
                or any(owner not in manifest["agents"] for owner in meta["owners"])):
            raise ValueError("manifesto inválido; instalação preservada")
        check_path(key)
    preserved, removed, files = [], [], {}
    remaining_agents = [a for a in manifest["agents"] if a not in selected]
    for key, meta in manifest["files"].items():
        if not isinstance(meta, dict) or meta.get("kind") not in ("file", "block") or not isinstance(meta.get("owners"), list):
            raise ValueError("manifesto inválido; instalação preservada")
        owners = [owner for owner in meta["owners"] if owner not in selected]
        if owners:
            files[key] = {**meta, "owners": owners}
            continue
        path = check_path(key)
        if not path.exists():
            continue
        current = path.read_bytes()
        if meta["kind"] == "block":
            try:
                if current.count(START) != 1 or current.count(END) != 1:
                    raise ValueError("marcadores alterados")
                start, end = current.index(START), current.index(END) + len(END)
                own = current[start:end]
                if digest(own) != meta.get("hash"):
                    raise ValueError("bloco modificado")
                updated = remove_block(current, own, meta.get("separator_added", False), meta.get("before_hash"))
                atomic_write(path, updated)
                removed.append(key)
            except ValueError:
                preserved.append(key)
        elif digest(current) == meta.get("hash"):
            path.unlink()
            removed.append(key)
        else:
            preserved.append(key)
    save_manifest(manifest_path, {"version": 1, "scope": scope, "agents": remaining_agents, "files": files})
    return {"removed": removed, "preserved": preserved, "remaining_agents": remaining_agents}


def doctor(agent, scope, project="."):
    import shutil
    import subprocess
    import sys
    from .state import AGENTS, state_root
    root, manifest_path, runtime = _paths(scope, project)
    manifest = load_manifest(manifest_path)
    selected = list(AGENTS) if agent == "all" else [agent]
    if any(item not in AGENTS for item in selected):
        raise ValueError("agente desconhecido")
    runtest = None
    if runtime.is_file():
        try:
            result = subprocess.run([sys.executable, str(runtime), "--help"], capture_output=True, text=True, timeout=10)
            runtest = result.returncode == 0
        except (OSError, subprocess.TimeoutExpired):
            runtest = False
    state_path = state_root()
    probe = state_path
    while not probe.exists() and probe != probe.parent:
        probe = probe.parent
    hosts = {}
    executables = {"claude": "claude", "codex": "codex", "cursor": "cursor", "gemini": "gemini", "antigravity": "antigravity"}
    for item in selected:
        paths = [Path(path) for path, meta in manifest["files"].items() if item in meta.get("owners", [])]
        hosts[item] = {"prepared": item in manifest["agents"] and bool(paths) and all(p.is_file() for p in paths),
                       "executable": shutil.which(executables[item]), "host_tested": False,
                       "pending": (["Configurar User Rules no Cursor"] if item == "cursor" and scope == "global" and item in manifest["agents"] else [])}
    return {"python": sys.version.split()[0], "runtime": str(runtime), "runtime_ok": runtest,
            "state_dir": str(state_path), "state_parent_writable": os.access(probe, os.W_OK), "agents": hosts}
