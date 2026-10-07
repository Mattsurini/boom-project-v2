#!/usr/bin/env python3
"""Repro a Hermes slash command dispatch failure end-to-end.

Usage:
  venv/Scripts/python.exe repro_dispatch.py <command-name> [--project-dir <path>] [--platform desktop]

Runs the real dispatch chain (scan -> build -> skill_view) in a fresh process
and prints exactly where it breaks:
  exit 0 = dispatch would succeed
  exit 1 = dispatch would return 4018
  exit 2 = usage/env error

Run with the hermes-agent venv python. The script locates the hermes home
from its own path (<home>/skills/<skill>/scripts/).
"""
import json
import os
import sys
from pathlib import Path


def main() -> int:
    args = sys.argv[1:]
    if not args or args[0] in ("-h", "--help"):
        print(__doc__.strip())
        return 2
    name = args[0].lstrip("/")
    project_dir, platform = None, "desktop"
    i = 1
    while i < len(args):
        if args[i] == "--project-dir" and i + 1 < len(args):
            project_dir = Path(args[i + 1])
            i += 2
        elif args[i] == "--platform" and i + 1 < len(args):
            platform = args[i + 1]
            i += 2
        else:
            print(f"unknown arg: {args[i]}")
            return 2

    home = Path(__file__).resolve().parents[3]  # <home>/skills/<skill>/scripts -> <home>
    agent_root = home / "hermes-agent"
    if not (agent_root / "agent" / "skill_commands.py").exists():
        print(f"error: hermes-agent source not found under {agent_root}")
        return 2
    os.environ.setdefault("HERMES_HOME", str(home))
    os.environ["HERMES_PLATFORM"] = platform
    sys.path.insert(0, str(agent_root))

    if project_dir is not None:
        project_dir = project_dir.resolve()
        if not project_dir.exists():
            print(f"error: project dir not found: {project_dir}")
            return 2
        os.chdir(project_dir)
        proj_skills = project_dir / ".agents" / "skills"
        if proj_skills.exists():
            # Force the project tier into scope: session-gated discovery
            # (trusted_project_dirs + cwd) often comes back empty in an
            # isolated repro, hiding the very collision being investigated.
            import agent.skill_utils as su
            _orig_dirs = su.get_project_skills_dirs

            def _forced_dirs():
                dirs = list(_orig_dirs())
                if proj_skills not in dirs:
                    dirs.append(proj_skills)
                return dirs

            su.get_project_skills_dirs = _forced_dirs
            from tools import skills_tool as st
            _orig_search = st._skill_search_dirs

            def _forced_search():
                pd, ad, active = _orig_search()
                if proj_skills not in ad:
                    ad = list(ad) + [proj_skills]
                return pd, ad, active

            st._skill_search_dirs = _forced_search

    from agent.skill_commands import build_skill_invocation_message, scan_skill_commands
    from tools.skills_tool import skill_view

    print(f"HERMES_HOME={os.environ['HERMES_HOME']}  platform={platform}  cwd={os.getcwd()}")
    cmds = scan_skill_commands()
    key = f"/{name}"
    print(f"scan: {len(cmds)} commands; {key} registered: {key in cmds}")
    if key not in cmds:
        print("  not registered -> dispatch returns 4018.")
        print("  check: skills.disabled in config.yaml, platform/environment frontmatter gate,")
        print("  core-command collision, or slug dedup (grep the live log for the name).")
        return 1
    print(f"  -> skill_dir: {cmds[key].get('skill_dir')}")

    msg = build_skill_invocation_message(key, "", task_id="repro")
    if msg:
        print(f"load: OK ({len(msg)} chars) -> dispatch would SUCCEED")
        return 0

    print("load: build_skill_invocation_message -> None -> dispatch returns 4018")
    r = json.loads(skill_view(name, preprocess=False))
    print(f"skill_view('{name}') success={r.get('success')}")
    if not r.get("success"):
        print(f"  error: {r.get('error')}")
        for m in r.get("matches") or []:
            print(f"  candidate: {m}")
    return 1


if __name__ == "__main__":
    sys.exit(main())
