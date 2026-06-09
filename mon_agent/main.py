from agent import Agent
from prompts import SYSTEM_PROMPT

# ─── Modèle Ollama ────────────────────────────────────────────────────────────
# Remplace "llama4" par "mistral", "qwen2.5", etc. selon ce que tu as en local.
# Pour vérifier : ollama list
MODEL = "qwen2.5:3b"   # change vers qwen2.5:3b ou mistral si tu les as

# ─── Questions de test (critères de réussite de l'atelier) ───────────────────
TEST_QUESTIONS = [
    # Question 1 : 2 outils (météo + heure)
    "Quelle heure est-il, et quel temps fait-il actuellement à Paris ?",

    # Question 2 : 2 outils (list_directory + get_folder_size)
    "Liste le contenu de mon dossier ~ et donne-moi la taille totale de ce dossier.",

    # Question 3 : 3 outils enchaînés (list_directory + get_folder_size + get_weather)
    "Montre-moi les fichiers de ~/Downloads, calcule la taille du dossier, "
    "et dis-moi aussi la météo à Lyon pour savoir si je peux sortir.",
]


def run_tests():
    """Lance les 3 questions de test automatiquement."""
    print("\n" + "═" * 60)
    print("  MODE TEST — 3 questions de l'atelier")
    print("═" * 60)

    agent = Agent(model=MODEL, system_prompt=SYSTEM_PROMPT)

    for i, question in enumerate(TEST_QUESTIONS, 1):
        print(f"\n{'─' * 60}")
        print(f"  Question {i} : {question}")
        print("─" * 60)
        response = agent.run(question)
        print(f"\n🤖 {response}\n")


def run_interactive():
    """Lance le mode interactif CLI."""
    print("\n" + "═" * 60)
    print(f"  Agent ReAct — modèle : {MODEL}")
    print("  Tapez 'exit' ou 'quit' pour quitter")
    print("  Tapez 'test' pour lancer les questions de l'atelier")
    print("═" * 60)

    agent = Agent(model=MODEL, system_prompt=SYSTEM_PROMPT)

    while True:
        try:
            user_input = input("\n> ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\nAu revoir !")
            break

        if not user_input:
            continue

        if user_input.lower() in {"exit", "quit"}:
            print("Au revoir !")
            break

        if user_input.lower() == "test":
            run_tests()
            continue

        response = agent.run(user_input)
        print(f"\n🤖 {response}")


if __name__ == "__main__":
    import sys

    if len(sys.argv) > 1 and sys.argv[1] == "--test":
        run_tests()
    else:
        run_interactive()
