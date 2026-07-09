import math
import json

# ── Tool Definitions for Groq ──────────────────────────────
TOOLS = [
    {
        "type": "function",
        "function": {
            "name": "web_search",
            "description": "Search the web for current information on any topic",
            "parameters": {
                "type": "object",
                "properties": {
                    "query": {
                        "type": "string",
                        "description": "The search query"
                    }
                },
                "required": ["query"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "calculator",
            "description": "Evaluate mathematical expressions and calculations",
            "parameters": {
                "type": "object",
                "properties": {
                    "expression": {
                        "type": "string",
                        "description": "Math expression to evaluate e.g. '2 + 2', '15 * 100 / 12'"
                    }
                },
                "required": ["expression"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "document_retrieval",
            "description": "Search and retrieve information from the knowledge base documents",
            "parameters": {
                "type": "object",
                "properties": {
                    "query": {
                        "type": "string",
                        "description": "What to search for in the documents"
                    }
                },
                "required": ["query"]
            }
        }
    }
]

# ── Knowledge Base ─────────────────────────────────────────
KNOWLEDGE_BASE = {
    "machine learning": "Machine learning is a subset of AI that enables systems to learn from data. Key types: supervised learning, unsupervised learning, reinforcement learning.",
    "deep learning": "Deep learning uses neural networks with multiple layers. Powers image recognition, NLP, and speech recognition.",
    "transformer": "Transformers use attention mechanisms to process sequences in parallel. Architecture behind GPT, BERT, Claude.",
    "rag": "RAG (Retrieval Augmented Generation) combines document retrieval with LLM generation. Solves LLM knowledge cutoff problem.",
    "python": "Python is a high-level programming language known for readability. Popular for AI/ML, web development, and automation.",
    "fastapi": "FastAPI is a modern Python web framework. Fast, automatic docs, type-safe. Built on Starlette and Pydantic.",
    "react": "React is a JavaScript library for building user interfaces. Component-based, virtual DOM, maintained by Meta.",
    "chromadb": "ChromaDB is an open-source vector database. Used to store and query embeddings for semantic search.",
    "lora": "LoRA (Low-Rank Adaptation) is a parameter-efficient fine-tuning method. Trains only 0.1-1% of model parameters.",
    "agent": "An AI agent is an LLM in a loop that can use tools. Follows ReAct pattern: Reason, Act, Observe, repeat.",
    "mcp": "Model Context Protocol (MCP) is Anthropic's open standard for connecting LLMs to external tools and data sources.",
    "dpo": "DPO (Direct Preference Optimization) trains LLMs on preference pairs. Simpler alternative to RLHF/PPO.",
    "chain of thought": "Chain of Thought prompting asks model to think step by step. Dramatically improves reasoning accuracy.",
    "vector database": "Vector databases store embeddings and enable fast similarity search. Options: ChromaDB, Pinecone, Weaviate, Qdrant.",
    "groq": "Groq provides ultra-fast LLM inference using custom LPU chips. Free tier available at console.groq.com.",
    "embedding": "Embeddings are dense vector representations of text. Similar meanings = close vectors in high-dimensional space.",
}

# ── Search Results Database ────────────────────────────────
SEARCH_RESULTS = {
    "python frameworks": "Top Python frameworks: 1. FastAPI (fastest growing) 2. Django (most popular) 3. Flask (lightweight) 4. Tornado (async)",
    "node.js orms": "Top Node.js ORMs: 1. Prisma (type-safe, modern) 2. Sequelize (most popular) 3. TypeORM (TypeScript-first)",
    "best ai tools": "Top AI tools 2025: 1. Claude (best coding) 2. GPT-4 (versatile) 3. Gemini (multimodal) 4. Groq (fastest inference)",
    "machine learning salary": "ML Engineer salary India: Junior ₹6-12 LPA, Mid ₹12-25 LPA, Senior ₹25-60 LPA",
    "react vs vue": "React vs Vue: React has larger ecosystem and job market. Vue has gentler learning curve. Both are excellent choices.",
    "vector databases": "Top vector DBs: 1. Pinecone (managed) 2. ChromaDB (open-source) 3. Weaviate (GraphQL) 4. Qdrant (Rust, fast)",
    "ai internship": "AI internship tips: Build projects, contribute to open source, learn PyTorch/TensorFlow, practice on Kaggle datasets.",
}


# ── Tool Execution ─────────────────────────────────────────
def execute_tool(tool_name: str, tool_input: dict) -> str:
    if tool_name == "web_search":
        query = tool_input.get("query", "").lower()

        # Match against search database
        for key, result in SEARCH_RESULTS.items():
            if any(word in query for word in key.split()):
                return f"Search results for '{tool_input['query']}': {result}"

        return f"Search results for '{tool_input['query']}': Found general information. The topic relates to {tool_input['query']} which is an active area in technology and AI development."

    elif tool_name == "calculator":
        expression = tool_input.get("expression", "")
        try:
            allowed = {
                "__builtins__": {},
                "abs": abs, "round": round,
                "min": min, "max": max,
                "sqrt": math.sqrt,
                "pow": math.pow,
                "pi": math.pi,
            }
            expr = expression.replace("%", "/100").replace("^", "**")
            result = eval(expr, allowed)
            if isinstance(result, float):
                result = round(result, 4)
            return f"Result of '{expression}' = {result}"
        except Exception as e:
            return f"Could not calculate '{expression}': {str(e)}"

    elif tool_name == "document_retrieval":
        query = tool_input.get("query", "").lower()

        # Find matching documents
        matches = []
        for key, content in KNOWLEDGE_BASE.items():
            if any(word in query for word in key.split()) or key in query:
                matches.append(f"[{key.upper()}]: {content}")

        if matches:
            return "Retrieved documents:\n" + "\n".join(matches[:3])
        return f"No specific documents found for '{tool_input['query']}'. The knowledge base covers: ML, Deep Learning, Transformers, RAG, Python, FastAPI, React, ChromaDB, LoRA, Agents, MCP, DPO, CoT, Vector DBs."

    return f"Unknown tool: {tool_name}"
