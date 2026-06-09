# mon-serveur-mcp

Serveur MCP Python exposant 2 outils à Claude Desktop, Cursor ou Claude Code.

## Outils disponibles

| Outil | Description |
|---|---|
| `get_weather(city)` | Météo actuelle pour n'importe quelle ville (via wttr.in) |
| `scan_project(path)` | Analyse complète d'un dossier de code |

---

## Installation

```bash
pip install mcp
```

---

## Brancher dans Claude Code ✅ (recommandé)

```bash
claude mcp add mon-serveur -- python C:/Users/princ/Downloads/mon_serveur_mcp/server.py
```

Vérifier que le serveur est bien enregistré :
```bash
claude mcp list
```

Lancer Claude Code :
```bash
claude
```

> Si les outils n'apparaissent pas immédiatement, redémarre Claude Code — ils seront visibles dès la session suivante.

---

## Brancher dans Claude Desktop (Windows)

Créer (ou modifier) le fichier :
```
%APPDATA%\Claude\claude_desktop_config.json
```

Contenu :
```json
{
  "mcpServers": {
    "mon-serveur": {
      "command": "python",
      "args": ["C:/Users/princ/Downloads/mon_serveur_mcp/server.py"]
    }
  }
}
```

→ Redémarre Claude Desktop  
→ L'icône 🔌 MCP apparaît en bas de la fenêtre de chat

---

## Brancher dans Cursor

Fichier de config : `C:\Users\princ\.cursor\mcp.json`

Si tu as déjà d'autres serveurs MCP, ajoute `mon-serveur` à côté :
```json
{
  "mcpServers": {
    "@21st-dev/magic": {
      "command": "npx",
      "args": ["-y", "@21st-dev/magic@latest", "API_KEY=..."]
    },
    "mon-serveur": {
      "command": "python",
      "args": ["C:/Users/princ/Downloads/mon_serveur_mcp/server.py"]
    }
  }
}
```

---

## Démarrage manuel (test uniquement)

```bash
python server.py
```

Le serveur tourne en stdio — le curseur clignote sans output, c'est normal.  
Il est piloté par le client MCP (Claude Code, Claude Desktop, Cursor), pas par l'utilisateur.

---

## Questions de test (critères de l'atelier)

```
1. Quel temps fait-il à Paris ?
   → appelle get_weather

2. Analyse mon projet dans C:/Users/princ/Downloads/mon_agent
   → appelle scan_project

3. Donne-moi la météo à Lyon et analyse aussi le dossier
   C:/Users/princ/Downloads/mon_agent
   → enchaîne get_weather + scan_project
```