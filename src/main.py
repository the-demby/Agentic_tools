import os
from dotenv import load_dotenv
from azure.identity import DefaultAzureCredential
from azure.ai.agents import AgentsClient
from azure.ai.agents.models import FunctionTool, ToolSet, MessageRole

from post_to_linkedin import post_to_linkedin

load_dotenv()
AGENT_NAME= "linkedin-poster-agent"

agents_client = AgentsClient(
    endpoint=os.getenv("PROJECT_ENDPOINT"),
    credential=DefaultAzureCredential(),
)

# FunctionTool pour LinkedIn
functions = FunctionTool({ post_to_linkedin })
toolset = ToolSet()
toolset.add(functions)
agents_client.enable_auto_function_calls(toolset)

# instructions système
with open("social-media-agent-instructions.txt", "r", encoding="utf-8") as f:
    instructions = f.read()

# 1) Supprimer les agents existants portant ce nom
print("🔍 Check rapide des agents existants…")
for existing in agents_client.list_agents():
    if existing.name == AGENT_NAME:
        agents_client.delete_agent(agent_id=existing.id)

agent = agents_client.create_agent(
    model=os.getenv("MODEL_DEPLOYMENT_NAME"),
    name=AGENT_NAME,
    instructions=instructions,
    toolset=toolset,
)

# thread (une fois par session)
thread = agents_client.threads.create()
print("💬 Conversation démarrée (taper 'exit' pour quitter)\n")

# Boucle de conversation
while True:
    user_input = input("Vous 😎​: ")
    if user_input.lower() in ("exit", "quit", "quitter"):
        break

    # Envoi du message utilisateur
    agents_client.messages.create(
        thread_id=thread.id,
        role=MessageRole.USER,
        content=user_input
    )

    # Créer et traiter synchroniquement le run (LLM + tool calls si besoin)
    run = agents_client.runs.create_and_process(
        thread_id=thread.id,
        agent_id=agent.id
    )

    # Récupérer le dernier message de l'assistant (En fait on lit tous les messages et on conserve le dernier assistant)
    all_messages = agents_client.messages.list(
        thread_id=thread.id,
        order="asc"
    )
    last_assistant = None
    for msg in all_messages:
        if msg.role == MessageRole.AGENT:
            last_assistant = msg

    if last_assistant and last_assistant.text_messages:
        # Concaténation des morceaux de texte (streamed si applicable)
        text = "".join(chunk.text.value for chunk in last_assistant.text_messages)
        print("Agent 🤖​ :", text)
    else:
        print("Agent : [Pas de réponse]\n")

print("Good bye mon pti chat 🤭​")
