from ollama import chat
from tools import TOOLS, TOOLS_SCHEMA

# Modèles connus pour NE PAS supporter le tool calling
MODELS_WITHOUT_TOOL_SUPPORT = {"qwen2:0.5b", "qwen2:1.5b", "qwen:0.5b"}


class Agent:
    def __init__(self, model: str = "qwen2.5:1.5b", system_prompt: str = ""):
        self.model = model
        self.history = [{"role": "system", "content": system_prompt}]
        self.max_iterations = 10
        self._warn_if_unsupported()

    def _warn_if_unsupported(self):
        if self.model in MODELS_WITHOUT_TOOL_SUPPORT:
            print(f"""
⚠️  ATTENTION : '{self.model}' ne supporte pas le tool calling.
   L'agent ne pourra pas appeler les outils — il répondra en langage naturel.
   → Lance : ollama pull qwen2.5:1.5b
   → Puis change MODEL = "qwen2.5:1.5b" dans main.py
""")

    def run(self, user_input: str) -> str:
        """Lance la boucle ReAct pour une question utilisateur."""
        self.history.append({"role": "user", "content": user_input})

        for iteration in range(self.max_iterations):
            print(f"  [itération {iteration + 1}]", end=" ", flush=True)

            response = chat(
                model=self.model,
                messages=self.history,
                tools=TOOLS_SCHEMA,
            )
            msg = response["message"]
            self.history.append(msg)

            # Cas 1 : pas d'outil demandé → réponse finale
            if not msg.get("tool_calls"):
                print("→ réponse finale")
                return msg["content"]

            # Cas 2 : un ou plusieurs outils à appeler
            tool_names = [c["function"]["name"] for c in msg["tool_calls"]]
            print(f"→ appel outil(s) : {', '.join(tool_names)}")

            for call in msg["tool_calls"]:
                self._execute_tool(call)

        return "⚠️ Limite d'itérations atteinte sans réponse finale."

    def _execute_tool(self, call: dict):
        """Exécute un outil et injecte le résultat dans l'historique."""
        fn_name = call["function"]["name"]
        fn_args = call["function"]["arguments"]

        if fn_name not in TOOLS:
            result = f"Erreur : outil inconnu '{fn_name}'"
        else:
            try:
                result = TOOLS[fn_name](**fn_args)
            except Exception as e:
                result = f"Erreur lors de l'exécution de '{fn_name}' : {e}"

        print(f"    ↳ {fn_name}({fn_args}) → {str(result)[:120]}{'...' if len(str(result)) > 120 else ''}")

        self.history.append({
            "role": "tool",
            "content": str(result),
        })
