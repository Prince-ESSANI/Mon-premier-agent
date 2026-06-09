"""
tools.py — Fonctions Python exposées via le serveur MCP.
Aucune dépendance MCP ici : des fonctions standard réutilisables.
"""

import os
import json
import urllib.request
import urllib.parse
from pathlib import Path
from collections import defaultdict


# ─────────────────────────────────────────────
# OUTIL 1 — API publique : météo (wttr.in)
# ─────────────────────────────────────────────

def get_weather(city: str) -> str:
    """
    Renvoie la météo actuelle pour une ville donnée.
    Utilise wttr.in — gratuit, sans clé API.
    """
    url = f"https://wttr.in/{urllib.parse.quote(city)}?format=j1"
    req = urllib.request.Request(url, headers={"User-Agent": "curl/7.68.0"})

    with urllib.request.urlopen(req, timeout=8) as resp:
        data = json.loads(resp.read())

    current  = data["current_condition"][0]
    temp_c   = current["temp_C"]
    feels    = current["FeelsLikeC"]
    humidity = current["humidity"]
    wind_kmh = current["windspeedKmph"]
    desc     = current["weatherDesc"][0]["value"]
    area     = data["nearest_area"][0]["areaName"][0]["value"]
    country  = data["nearest_area"][0]["country"][0]["value"]

    return (
        f"Météo à {area}, {country} : {desc}. "
        f"Température : {temp_c}°C (ressenti {feels}°C), "
        f"humidité : {humidity}%, vent : {wind_kmh} km/h."
    )


# ─────────────────────────────────────────────
# OUTIL 2 — Personnel : analyse d'un projet de code
# ─────────────────────────────────────────────

# Extensions → langage
LANG_MAP = {
    ".py": "Python", ".js": "JavaScript", ".ts": "TypeScript",
    ".jsx": "React/JSX", ".tsx": "React/TSX", ".vue": "Vue.js",
    ".php": "PHP", ".java": "Java", ".cs": "C#", ".cpp": "C++",
    ".c": "C", ".go": "Go", ".rs": "Rust", ".rb": "Ruby",
    ".html": "HTML", ".css": "CSS", ".scss": "SCSS",
    ".json": "JSON", ".yaml": "YAML", ".yml": "YAML",
    ".sql": "SQL", ".md": "Markdown", ".sh": "Shell",
    ".dockerfile": "Docker", ".toml": "TOML", ".env": "Config",
}

# Dossiers à ignorer
IGNORE_DIRS = {
    "node_modules", ".git", "__pycache__", ".venv", "venv",
    "env", "dist", "build", ".next", "target", "vendor",
    ".idea", ".vscode", "coverage", ".cache",
}


def scan_project(path: str) -> str:
    """
    Analyse un dossier de projet de code.
    Retourne : langages détectés, nombre de fichiers par langage,
    taille totale, les 5 fichiers les plus récemment modifiés,
    et détecte les fichiers de config importants (package.json,
    requirements.txt, Dockerfile, etc.).
    """
    root = Path(os.path.expanduser(path))

    if not root.exists():
        return f"Erreur : le chemin '{path}' n'existe pas."
    if not root.is_dir():
        return f"Erreur : '{path}' n'est pas un dossier."

    lang_count   = defaultdict(int)   # langage → nb fichiers
    lang_lines   = defaultdict(int)   # langage → nb lignes (approx)
    total_size   = 0
    total_files  = 0
    recent_files = []                  # (mtime, nom relatif)
    config_found = []                  # fichiers de config détectés

    config_names = {
        "package.json", "requirements.txt", "Pipfile", "pyproject.toml",
        "Dockerfile", "docker-compose.yml", "docker-compose.yaml",
        ".env.example", "pom.xml", "build.gradle", "Makefile",
        "tsconfig.json", ".eslintrc.json", "composer.json",
    }

    for f in root.rglob("*"):
        # Ignorer les dossiers blacklistés
        if any(part in IGNORE_DIRS for part in f.parts):
            continue
        if not f.is_file():
            continue

        try:
            stat      = f.stat()
            size      = stat.st_size
            mtime     = stat.st_mtime
            ext       = f.suffix.lower()
            rel_name  = str(f.relative_to(root))

            total_size  += size
            total_files += 1
            recent_files.append((mtime, rel_name))

            # Détecter le langage
            lang = LANG_MAP.get(ext)
            if lang:
                lang_count[lang] += 1
                # Compter les lignes (fichiers texte seulement, max 500 Ko)
                if size < 500_000:
                    try:
                        lines = f.read_text(encoding="utf-8", errors="ignore").count("\n")
                        lang_lines[lang] += lines
                    except Exception:
                        pass

            # Détecter fichiers de config
            if f.name in config_names:
                config_found.append(rel_name)

        except (PermissionError, OSError):
            continue

    if total_files == 0:
        return f"Le dossier '{path}' est vide ou ne contient pas de fichiers accessibles."

    # Taille humaine
    def human(n):
        for unit in ["o", "Ko", "Mo", "Go"]:
            if n < 1024:
                return f"{n:.1f} {unit}"
            n /= 1024
        return f"{n:.1f} To"

    # Top 5 langages par nb de fichiers
    top_langs = sorted(lang_count.items(), key=lambda x: x[1], reverse=True)[:6]
    langs_str = "\n".join(
        f"  • {lang}: {count} fichier{'s' if count > 1 else ''}"
        f" (~{lang_lines[lang]:,} lignes)"
        for lang, count in top_langs
    )

    # 5 fichiers les plus récemment modifiés
    recent_files.sort(reverse=True)
    recent_str = "\n".join(f"  • {name}" for _, name in recent_files[:5])

    # Config trouvés
    config_str = (
        "\n".join(f"  • {c}" for c in config_found[:8])
        if config_found else "  • Aucun fichier de config standard détecté"
    )

    return (
        f"📁 Projet : {root.name}\n"
        f"📊 {total_files} fichiers — {human(total_size)}\n\n"
        f"🔤 Langages détectés :\n{langs_str}\n\n"
        f"🕐 Fichiers récemment modifiés :\n{recent_str}\n\n"
        f"⚙️  Fichiers de config :\n{config_str}"
    )
