"""
server.py — Serveur MCP exposant 2 outils à Claude Desktop / Cursor.

Démarrage :
    python server.py

Le serveur tourne en stdio (stdin/stdout) — c'est le transport
standard MCP que Claude Desktop et Cursor savent lire.
"""

import asyncio
from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp.types import Tool, TextContent

from tools import get_weather, scan_project

# ── Création du serveur ──────────────────────────────────────────────────────
app = Server("mon-serveur-mcp")


# ── Liste des outils exposés ─────────────────────────────────────────────────
@app.list_tools()
async def list_tools() -> list[Tool]:
    return [
        Tool(
            name="get_weather",
            description=(
                "Renvoie la météo actuelle (température, ressenti, humidité, vent, "
                "conditions) pour n'importe quelle ville dans le monde."
            ),
            inputSchema={
                "type": "object",
                "properties": {
                    "city": {
                        "type": "string",
                        "description": "Nom de la ville (ex: Paris, Lyon, Tokyo, New York)",
                    }
                },
                "required": ["city"],
            },
        ),
        Tool(
            name="scan_project",
            description=(
                "Analyse un dossier de projet de code : détecte les langages utilisés, "
                "compte les fichiers et les lignes par langage, liste les fichiers "
                "récemment modifiés et les fichiers de configuration importants "
                "(package.json, Dockerfile, requirements.txt…). "
                "Idéal pour avoir une vue d'ensemble d'un projet avant de plonger dedans."
            ),
            inputSchema={
                "type": "object",
                "properties": {
                    "path": {
                        "type": "string",
                        "description": (
                            "Chemin absolu ou relatif du dossier de projet à analyser. "
                            "Supporte ~/ pour le dossier home. "
                            "Exemple : C:/Users/princ/Downloads/mon_agent"
                        ),
                    }
                },
                "required": ["path"],
            },
        ),
    ]


# ── Exécution des outils ─────────────────────────────────────────────────────
@app.call_tool()
async def call_tool(name: str, arguments: dict) -> list[TextContent]:
    try:
        if name == "get_weather":
            city   = arguments["city"]
            result = get_weather(city)

        elif name == "scan_project":
            path   = arguments["path"]
            result = scan_project(path)

        else:
            result = f"Erreur : outil inconnu '{name}'."

    except KeyError as e:
        result = f"Erreur : paramètre manquant {e}."
    except Exception as e:
        result = f"Erreur lors de l'exécution de '{name}' : {e}"

    return [TextContent(type="text", text=result)]


# ── Point d'entrée ───────────────────────────────────────────────────────────
async def main():
    async with stdio_server() as (read_stream, write_stream):
        await app.run(
            read_stream,
            write_stream,
            app.create_initialization_options(),
        )


if __name__ == "__main__":
    asyncio.run(main())
