import os
import json
import urllib.request
from pathlib import Path
from datetime import datetime


# ─────────────────────────────────────────────
# OUTILS DE BASE (fournis par l'atelier)
# ─────────────────────────────────────────────

def get_current_time() -> str:
    """Renvoie la date et l'heure courante au format ISO 8601."""
    return datetime.now().isoformat()


def list_directory(path: str) -> list[str]:
    """Liste les fichiers et dossiers d'un chemin donné sur le système."""
    expanded = os.path.expanduser(path)
    if not os.path.exists(expanded):
        return [f"Erreur : le chemin '{path}' n'existe pas."]
    return os.listdir(expanded)


def read_file(path: str) -> str:
    """Lit le contenu d'un fichier texte (max 4096 caractères renvoyés)."""
    expanded = os.path.expanduser(path)
    content = Path(expanded).read_text(encoding="utf-8")
    return content[:4096]


# ─────────────────────────────────────────────
# OUTIL PERSO 1 — API publique : météo
# Utilise Open-Meteo (gratuit, sans clé API)
# ─────────────────────────────────────────────

def get_weather(city: str) -> str:
    """
    Renvoie la météo actuelle pour une ville donnée.
    Utilise l'API wttr.in (gratuite, sans clé, supporte les villes en français).
    Paramètres : city (str) — nom de la ville (ex: Paris, Lyon, Tokyo).
    """
    url = f"https://wttr.in/{urllib.parse.quote(city)}?format=j1"
    req = urllib.request.Request(url, headers={"User-Agent": "curl/7.68.0"})

    with urllib.request.urlopen(req, timeout=8) as resp:
        data = json.loads(resp.read())

    current = data["current_condition"][0]
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
# OUTIL PERSO 2 — Système : taille d'un dossier
# ─────────────────────────────────────────────

def get_folder_size(path: str) -> str:
    """
    Calcule la taille totale d'un dossier, le nombre de fichiers qu'il contient,
    et retourne les 5 fichiers les plus lourds.
    Paramètres : path (str) — chemin absolu ou relatif (~/ supporté).
    """
    expanded = Path(os.path.expanduser(path))
    if not expanded.exists():
        return f"Erreur : le chemin '{path}' n'existe pas."
    if not expanded.is_dir():
        return f"Erreur : '{path}' n'est pas un dossier."

    total_size = 0
    file_count = 0
    file_sizes = []

    for f in expanded.rglob("*"):
        if f.is_file():
            try:
                size = f.stat().st_size
                total_size += size
                file_count += 1
                file_sizes.append((size, f.name))
            except (PermissionError, OSError):
                pass

    # Convertir en unité lisible
    def human(n):
        for unit in ["o", "Ko", "Mo", "Go"]:
            if n < 1024:
                return f"{n:.1f} {unit}"
            n /= 1024
        return f"{n:.1f} To"

    top5 = sorted(file_sizes, reverse=True)[:5]
    top5_str = ", ".join(f"{name} ({human(s)})" for s, name in top5)

    return (
        f"Dossier '{path}' : {file_count} fichiers, "
        f"taille totale {human(total_size)}. "
        f"Top 5 fichiers : {top5_str or 'aucun'}."
    )


# ─────────────────────────────────────────────
# REGISTRE DES OUTILS
# ─────────────────────────────────────────────

import urllib.parse  # noqa: E402 (import tardif pour get_weather)

TOOLS = {
    "get_current_time": get_current_time,
    "list_directory":   list_directory,
    "read_file":        read_file,
    "get_weather":      get_weather,
    "get_folder_size":  get_folder_size,
}

# ─────────────────────────────────────────────
# SCHÉMAS JSON-SCHEMA (format Ollama/OpenAI)
# ─────────────────────────────────────────────

TOOLS_SCHEMA = [
    {
        "type": "function",
        "function": {
            "name": "get_current_time",
            "description": "Renvoie la date et l'heure courante au format ISO 8601.",
            "parameters": {"type": "object", "properties": {}, "required": []},
        },
    },
    {
        "type": "function",
        "function": {
            "name": "list_directory",
            "description": "Liste les fichiers et dossiers présents dans un répertoire.",
            "parameters": {
                "type": "object",
                "properties": {
                    "path": {"type": "string", "description": "Chemin du dossier (ex: ~/Downloads)"},
                },
                "required": ["path"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "read_file",
            "description": "Lit le contenu d'un fichier texte et renvoie les 4096 premiers caractères.",
            "parameters": {
                "type": "object",
                "properties": {
                    "path": {"type": "string", "description": "Chemin complet du fichier"},
                },
                "required": ["path"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "get_weather",
            "description": "Renvoie la météo actuelle (température, humidité, vent, conditions) pour une ville donnée.",
            "parameters": {
                "type": "object",
                "properties": {
                    "city": {"type": "string", "description": "Nom de la ville (ex: Paris, Lyon, Tokyo)"},
                },
                "required": ["city"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "get_folder_size",
            "description": "Calcule la taille totale d'un dossier, le nombre de fichiers, et liste les 5 plus gros fichiers.",
            "parameters": {
                "type": "object",
                "properties": {
                    "path": {"type": "string", "description": "Chemin du dossier à analyser (ex: ~/Documents)"},
                },
                "required": ["path"],
            },
        },
    },
]
