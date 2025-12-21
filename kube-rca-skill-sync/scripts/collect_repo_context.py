#!/usr/bin/env python3
"""
Collect a lightweight repo context report for kube-rca skill updates.

Requires Python 3.9+ (PEP 585 type hints).
"""

import argparse
from datetime import datetime
from pathlib import Path
from typing import Iterable, Optional, Sequence

SKIP_DIRS = {
    ".git",
    ".terraform",
    "__pycache__",
    "dist",
    "build",
    "node_modules",
    ".next",
    ".venv",
    "vendor",
}

DEFAULT_MAPPING = {
    "kube-rca-backend": "backend",
    "kube-rca-agent": "agent",
    "kube-rca-frontend": "frontend",
    "kube-rca-helm": "helm-charts",
    "kube-rca-terraform": "terraform",
    "kube-rca-full": ".",
}

KEY_ITEMS = {
    "kube-rca-backend": [
        "go.mod",
        "main.go",
        "internal",
        "Dockerfile",
        "kubernetes",
        "README.md",
    ],
    "kube-rca-agent": [
        "pyproject.toml",
        "app",
        "tests",
        "Dockerfile",
        "README.md",
        "Makefile",
    ],
    "kube-rca-frontend": [
        "package.json",
        "src",
        "public",
        "index.html",
        "vite.config.ts",
        "vite.config.js",
        "tailwind.config.ts",
        "tailwind.config.js",
        "tsconfig.json",
        "README.md",
    ],
    "kube-rca-helm": [
        "charts",
        "README.md",
        "values.yaml",
    ],
    "kube-rca-terraform": [
        "envs",
        ".terraform-version",
        "README.md",
    ],
    "kube-rca-full": [
        "backend",
        "frontend",
        "helm-charts",
        "terraform",
        "k8s-resources",
        "AGENTS.md",
    ],
}


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Collect repo context for updating kube-rca skills."
    )
    parser.add_argument("--repo-root", default=".", help="Path to repo root.")
    parser.add_argument("--skills-dir", default="skills", help="Skills directory.")
    parser.add_argument(
        "--targets",
        default="",
        help="Comma-separated skill names. Default: all skills under skills-dir.",
    )
    parser.add_argument("--output", default="", help="Write report to a file path.")
    return parser.parse_args()


def normalize_targets(raw: str, fallback: Sequence[str]) -> list[str]:
    if raw.strip():
        return [item.strip() for item in raw.split(",") if item.strip()]
    return list(fallback)


def find_skills(skills_dir: Path) -> list[str]:
    if not skills_dir.is_dir():
        return []
    skills = []
    for entry in sorted(skills_dir.iterdir(), key=lambda p: p.name):
        if entry.is_dir() and (entry / "SKILL.md").is_file():
            skills.append(entry.name)
    return skills


def list_top_level(path: Path, max_items: int = 40) -> tuple[list[str], list[str]]:
    dirs: list[str] = []
    files: list[str] = []
    for entry in sorted(path.iterdir(), key=lambda p: p.name):
        if entry.name in SKIP_DIRS:
            continue
        if entry.is_dir():
            dirs.append(f"{entry.name}/")
        else:
            files.append(entry.name)
    return trim_list(dirs, max_items), trim_list(files, max_items)


def gather_key_items(path: Path, items: Iterable[str]) -> list[str]:
    found: list[str] = []
    for item in items:
        item_path = path / item
        if item_path.exists():
            suffix = "/" if item_path.is_dir() else ""
            found.append(f"{item}{suffix}")
    return found


def list_subdirs(path: Path, max_items: int = 20) -> list[str]:
    if not path.is_dir():
        return []
    names = []
    for entry in sorted(path.iterdir(), key=lambda p: p.name):
        if entry.is_dir() and entry.name not in SKIP_DIRS:
            names.append(f"{entry.name}/")
    return trim_list(names, max_items)


def trim_list(items: list[str], max_items: int) -> list[str]:
    if len(items) <= max_items:
        return items
    return items[:max_items] + [f"...({len(items) - max_items} more)"]


def map_skill_to_path(skill_name: str, repo_root: Path) -> tuple[str, Optional[Path]]:
    mapped = DEFAULT_MAPPING.get(skill_name)
    if mapped is None:
        return "UNMAPPED", None
    if mapped == ".":
        return mapped, repo_root
    return mapped, repo_root / mapped


def format_bool(value: bool) -> str:
    return "true" if value else "false"


def build_report(
    repo_root: Path, skills_dir: Path, targets: Sequence[str]
) -> list[str]:
    lines: list[str] = []
    timestamp = datetime.now().isoformat(timespec="seconds")
    lines.append("# kube-rca skill sync report")
    lines.append(f"generated_at: {timestamp}")
    lines.append(f"repo_root: {repo_root}")
    lines.append(f"skills_dir: {skills_dir}")
    lines.append(f"targets: {', '.join(targets) if targets else '(none)'}")
    lines.append("")

    for skill in targets:
        mapped, target_path = map_skill_to_path(skill, repo_root)
        exists = target_path is not None and target_path.exists()
        lines.append(f"## {skill}")
        lines.append(f"- mapped_path: {mapped}")
        lines.append(f"- path_exists: {format_bool(exists)}")
        if not exists or target_path is None:
            lines.append("")
            continue
        git_present = (target_path / ".git").exists()
        dirs, files = list_top_level(target_path)
        key_items = gather_key_items(target_path, KEY_ITEMS.get(skill, []))
        lines.append(f"- git_present: {format_bool(git_present)}")
        lines.append(f"- top_level_dirs: {', '.join(dirs) if dirs else '(none)'}")
        lines.append(f"- top_level_files: {', '.join(files) if files else '(none)'}")
        lines.append(f"- key_items: {', '.join(key_items) if key_items else '(none)'}")

        if skill == "kube-rca-helm":
            charts = list_subdirs(target_path / "charts")
            lines.append(f"- charts: {', '.join(charts) if charts else '(none)'}")
        if skill == "kube-rca-terraform":
            envs = list_subdirs(target_path / "envs")
            lines.append(f"- envs: {', '.join(envs) if envs else '(none)'}")

        lines.append("")

    return lines


def write_output(lines: list[str], output_path: str) -> None:
    content = "\n".join(lines).rstrip() + "\n"
    if output_path:
        Path(output_path).write_text(content, encoding="utf-8")
    else:
        print(content, end="")


def main() -> None:
    args = parse_args()
    repo_root = Path(args.repo_root).resolve()
    skills_dir = Path(args.skills_dir)
    if not skills_dir.is_absolute():
        skills_dir = repo_root / skills_dir

    skills = find_skills(skills_dir)
    targets = normalize_targets(args.targets, skills)
    lines = build_report(repo_root, skills_dir, targets)
    write_output(lines, args.output)


if __name__ == "__main__":
    main()
