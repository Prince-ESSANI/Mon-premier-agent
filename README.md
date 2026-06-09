# Mon Premier Agent IA

Projet réalisé dans le cadre du **Module 3 — Agents, MCP et génération d'images en local** .

Deux ateliers pratiques construits from scratch en Python :

| Dossier | Description |
|---|---|
| [`mon_agent/`](#atelier-1--agent-react) | Agent ReAct avec boucle LLM + outils (Atelier 1) |
| [`mon_serveur_mcp/`](#atelier-2--serveur-mcp) | Serveur MCP branché dans Claude Code / Cursor (Atelier 2) |

---

## Atelier 1 — Agent ReAct

Un agent IA minimaliste (~150 lignes) qui tourne en local avec **Ollama**, expose 5 outils Python et s'interroge en ligne de commande.

### Architecture

```
mon_agent/
├── agent.py      ← boucle ReAct (max 10 itérations)
├── tools.py      ← 5 outils disponibles
├── prompts.py    ← system prompt dev/tech
└── main.py       ← CLI interactive + mode --test
```

### Outils disponibles

| Outil | Type | Description |
|---|---|---|
| `get_current_time` | Système | Heure courante ISO 8601 |
| `list_directory(path)` | Système | Contenu d'un dossier |
| `read_file(path)` | Système | Lit un fichier texte (max 4 Ko) |
| `get_weather(city)` | API publique | Météo en temps réel via wttr.in |
| `get_folder_size(path)` | Système | Taille totale + top 5 fichiers |

### Stack

- **LLM** : Ollama local (qwen2.5:3b recommandé)
- **Dépendances** : `ollama` — pas de framework agent externe
- **Transport** : stdio

### Installation & lancement

```bash
pip install ollama
ollama pull qwen2.5:3b
python main.py

# Mode test automatique (3 questions de l'atelier)
python main.py --test
```

### Exemple de session

```
> Quelle heure est-il et quel temps fait-il à Paris ?
  [itération 1] → appel outil(s) : get_current_time, get_weather
    ↳ get_current_time({}) → 2026-06-09T15:58:55
    ↳ get_weather({'city': 'Paris'}) → Météo à Paris : Partly cloudy, 19°C...
  [itération 2] → réponse finale
🤖 Il est 15h58. À Paris, il fait partiellement nuageux avec 19°C...
```

---

## Atelier 2 — Serveur MCP

Un serveur **Model Context Protocol** qui expose 2 outils à n'importe quel client MCP compatible (Claude Code, Claude Desktop, Cursor).

### Architecture

```
mon_serveur_mcp/
├── server.py        ← serveur MCP (stdio transport)
├── tools.py         ← fonctions Python exposées
├── pyproject.toml   ← métadonnées du package
└── README.md        ← instructions d'installation
```

### Outils exposés

| Outil | Description |
|---|---|
| `get_weather(city)` | Météo actuelle via wttr.in (sans clé API) |
| `scan_project(path)` | Analyse un dossier de code : langages, lignes, fichiers de config, fichiers récents |

### Installation

```bash
pip install mcp
```

### Brancher dans Claude Code

```bash
claude mcp add mon-serveur -- python /chemin/vers/mon_serveur_mcp/server.py
claude mcp list   # vérifier
claude            # lancer
```

### Brancher dans Claude Desktop (Windows)

Créer `%APPDATA%\Claude\claude_desktop_config.json` :

```json
{
  "mcpServers": {
    "mon-serveur": {
      "command": "python",
      "args": ["C:/chemin/vers/mon_serveur_mcp/server.py"]
    }
  }
}
```

### Brancher dans Cursor

Fichier : `C:\Users\<user>\.cursor\mcp.json` — même format JSON.

---

## Résultats obtenus

### Atelier 1
- ✅ Agent enchaîne 2 outils sur une seule question (Q1 : `get_current_time` + `get_weather` en parallèle)
- ✅ Les erreurs sont renvoyées comme observations au LLM sans crasher l'agent
- ✅ Testé avec qwen2.5:3b via Ollama

### Atelier 2
- ✅ Serveur démarre sans erreur (`python server.py`)
- ✅ Outils visibles et appelables depuis Claude Code
- ✅ `scan_project` + `get_weather` enchaînés sur une même question

---

## Auteur

**Prince Essani** — étudiant DAD 3ème année, ESTIAM Lyon  
[GitHub](https://github.com/Prince-ESSANI)
