"""
Exemple d'agent IA — fichier de DÉMO pour tester la cartographie & gouvernance IA de SecMind.
Ce code n'est PAS destiné à être exécuté : il contient volontairement des motifs
(fournisseurs LLM, frameworks d'agents, signaux) que le scanner SecMind détecte.
"""

# ── Fournisseurs LLM ────────────────────────────────────────────────
import openai
from openai import OpenAI
import anthropic
import google.generativeai as genai          # Google Gemini
import cohere
from mistralai.client import MistralClient    # Mistral

# ── Frameworks d'agents ─────────────────────────────────────────────
from langchain.agents import AgentExecutor, create_react_agent  # LangChain + exécution autonome
from llama_index.core import VectorStoreIndex                    # LlamaIndex + RAG
from crewai import Agent, Task, Crew                             # CrewAI

# ── RAG / base vectorielle ──────────────────────────────────────────
import chromadb
from openai import embeddings   # embeddings


client = OpenAI(api_key="REMPLACER_PAR_VARIABLE_ENV")
anthropic_client = anthropic.Anthropic()


def repondre(question: str) -> str:
    # Prompt système + tool / function calling
    messages = [
        {"role": "system", "content": "Tu es un assistant interne."},
        {"role": "user", "content": question},
    ]
    completion = client.chat.completions.create(
        model="gpt-4o",
        messages=messages,
        tools=[{"type": "function", "function": {"name": "lookup", "parameters": {}}}],
        tool_choice="auto",
    )
    # Exemple Anthropic Claude
    anthropic_client.messages.create(
        model="claude-3-5-sonnet-20241022",
        max_tokens=300,
        messages=[{"role": "user", "content": question}],
    )
    # Exemple Gemini
    genai.GenerativeModel("gemini-1.5-flash").generate_content(question)
    return completion.choices[0].message.content


def agent_autonome():
    # Exécution autonome via LangChain AgentExecutor
    executor = AgentExecutor(agent=None, tools=[])
    return executor.run("Analyse ce dépôt et corrige les failles.")
