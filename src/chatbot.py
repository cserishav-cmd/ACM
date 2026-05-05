import os
import pickle
import pandas as pd
from openai import AsyncOpenAI
import datetime
import json
import asyncio
from utils.config import config

class ChatbotService:
    """Service to handle AI chatbot interactions with lazy loading and result caching."""

    _instance = None
    _lock = asyncio.Lock()

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialized = False
        return cls._instance

    def __init__(self):
        if self._initialized:
            return
            
        self.prompt_data = None
        self.wb_data = None
        self._historical_context_cache = None
        self._api_response_cache = {} # Simple cache for identical messages
        
        # Determine API Configuration
        api_key = os.getenv("NVIDIA_API_KEY") or os.getenv("TOGETHER_API_KEY")
        base_url = "https://integrate.api.nvidia.com/v1" if os.getenv("NVIDIA_API_KEY") else "https://api.together.xyz/v1"
        self.model_name = "meta/llama-3.1-70b-instruct" if os.getenv("NVIDIA_API_KEY") else "meta-llama/Meta-Llama-3.1-8B-Instruct-Turbo"
        
        if api_key:
            self.client = AsyncOpenAI(api_key=api_key, base_url=base_url)
        else:
            self.client = None

        self._initialized = True

    def _load_prompt_data(self):
        if self.prompt_data is None:
            self.prompt_data = self._load_pkl(config.CHATBOT_PROMPT_PATH)
        return self.prompt_data

    def _load_wb_data(self):
        if self.wb_data is None:
            self.wb_data = self._load_pkl(config.COMBINED_DATASETS_PATH)
        return self.wb_data

    def _load_pkl(self, filepath: str):
        if not os.path.exists(filepath):
            print(f"Warning: Dataset {filepath} not found.")
            return None
        try:
            with open(filepath, "rb") as f:
                return pickle.load(f)
        except Exception as e:
            print(f"Error loading {filepath}: {e}")
            return None

    def _get_historical_context(self) -> str:
        """Extract average yield and weather info from df.pkl, cached for performance."""
        if self._historical_context_cache:
            return self._historical_context_cache

        df_path = "models/df.pkl"
        if not os.path.exists(df_path):
            return "No historical data available."
            
        try:
            df = pd.read_pickle(df_path)
            context_lines = []
            
            if 'yield_kg_per_ha' in df.columns:
                avg_yield = df['yield_kg_per_ha'].mean()
                context_lines.append(f"- Avg Historical Yield: {avg_yield:.1f} kg/ha")
            if 'temp_mean_annual' in df.columns and 'rainfall_annual_mm' in df.columns:
                avg_temp = df['temp_mean_annual'].mean()
                avg_rain = df['rainfall_annual_mm'].mean()
                context_lines.append(f"- Hist. Weather: {avg_temp:.1f}°C, {avg_rain:.1f}mm Rain/Year")
                
            extreme_events = []
            if 'is_drought' in df.columns and df['is_drought'].sum() > 0:
                extreme_events.append("Historical Droughts recorded.")
            if 'is_flood' in df.columns and df['is_flood'].sum() > 0:
                extreme_events.append("Historical Floods recorded (Cyclone/Heavy Rain risks).")
            
            if extreme_events:
                context_lines.append(f"- Extreme Events: {' '.join(extreme_events)}")
                
            self._historical_context_cache = "\n".join(context_lines)
            return self._historical_context_cache
        except Exception as e:
            print(f"Error reading df.pkl context: {e}")
            return "Error loading historical data."

    def _get_knowledge_base_context(self, query: str = "") -> str:
        """Fetch relevant chunks from the knowledge base using simple keyword matching."""
        kb_path = "models/knowledge_base_chunks.pkl"
        if not os.path.exists(kb_path):
            return ""
            
        try:
            with open(kb_path, "rb") as f:
                chunks = pickle.load(f)
            
            if not query:
                selected = chunks[:2]
                return "\n---\n".join([getattr(c, 'page_content', str(c)) for c in selected])
                
            # Clean and split query
            import re
            query_words = set(re.findall(r'\w+', query.lower()))
            
            scored_chunks = []
            for c in chunks:
                text = getattr(c, 'page_content', str(c))
                text_words = set(re.findall(r'\w+', text.lower()))
                score = len(query_words.intersection(text_words))
                scored_chunks.append((score, text))
            
            # Sort by score descending, take top 3
            scored_chunks.sort(key=lambda x: x[0], reverse=True)
            selected_texts = [x[1] for x in scored_chunks[:3]]
            return "\n---\n".join(selected_texts)
        except Exception as e:
            print(f"Error reading KB: {e}")
            return ""

    def _format_pipeline_results(self, pipeline_results: dict) -> str:
        if not pipeline_results: return "No real-time data."
            
        context = [f"[PIPELINE] Route: {pipeline_results.get('route', 'Unknown')}"]
        
        disease = pipeline_results.get("disease")
        if disease:
            status = "Healthy" if disease.get('is_healthy') else disease.get('predicted_class')
            context.append(f"- Health: {status} ({disease.get('severity', 'N/A')})")
        
        seg = pipeline_results.get("segmentation")
        if seg:
            context.append(f"- Coverage: {seg.get('vegetation_percent', 0):.1f}%")
            
        variety = pipeline_results.get("variety")
        if variety:
            context.append(f"- Variety: {variety.get('predicted_class')}")
            
        return "\n".join(context)

    def _build_system_prompt(self, pipeline_results: dict, user_query: str = "") -> str:
        historical = self._get_historical_context()
        kb_context = self._get_knowledge_base_context(user_query)
        realtime = self._format_pipeline_results(pipeline_results)
        
        # Try to load custom prompt if exists, else use strict fallback
        prompt_data = self._load_prompt_data()
        
        DEFAULT_PROMPT = """You are a highly specialized AI Agriculture Assistant for West Bengal, focusing strictly on Rice (Paddy) cultivation, crop health, and weather-agrochemical interactions.

CRITICAL INSTRUCTIONS:
1. STRICT CONTEXT BOUNDARY: You must NEVER answer questions outside the scope of agriculture, crop science, weather patterns, and the provided data. If a user asks an out-of-context question (e.g., programming, politics, or unrelated topics), politely decline and state you only answer agriculture-related queries.
2. USE PROVIDED DATA: Base your answers heavily on the Historical Context, Real-Time Results, and the Knowledge Base provided below. Provide probable insights from the PKL data when queried.
3. PADDY KNOWLEDGE FALLBACK: If the user asks a question specifically about Paddy (Rice) and the answer is NOT found in the provided Historical Data or Knowledge Base, you are ALLOWED to generate an output based on your own general agricultural knowledge, BUT ONLY for Paddy-related queries.
4. WEATHER & CYCLONES: Always factor in real-time or historical extreme weather (cyclones, floods, droughts, high winds) if relevant. Emphasize how these events impact crop yield, pesticide drift, and fertilizer leaching. Do not invent weather data outside of what is logically probable for the region.

---
HISTORICAL DATA CONTEXT (From PKL):
{context}

RELEVANT KNOWLEDGE BASE EXTRACT:
{kb_context}

REAL-TIME PIPELINE RESULTS:
{pipeline_context}
---

Provide clear, concise, and scientifically accurate agronomic recommendations based ONLY on the data above and your agricultural expertise."""

        template = prompt_data.get("system_prompt", "") if prompt_data else DEFAULT_PROMPT
        
        # Ensure fallback if template string formatting fails
        try:
            return template.format(context=historical, kb_context=kb_context, pipeline_context=realtime)
        except Exception:
            return DEFAULT_PROMPT.format(context=historical, kb_context=kb_context, pipeline_context=realtime)

    async def generate_initial_insight(self, pipeline_results: dict) -> str:
        """Generates contextual insight, using cache if identical results provided."""
        cache_key = json.dumps(pipeline_results, sort_keys=True)
        if cache_key in self._api_response_cache:
            return self._api_response_cache[cache_key]

        if not self.client: return "AI Chatbot unavailable."
            
        user_msg = "Provide a concise, actionable agronomic recommendation based on these results."
        system_prompt = self._build_system_prompt(pipeline_results, user_query=user_msg)

        try:
            response = await self.client.chat.completions.create(
                model=self.model_name,
                messages=[{"role": "system", "content": system_prompt}, {"role": "user", "content": user_msg}],
                temperature=0.2,
                max_tokens=500
            )
            reply = response.choices[0].message.content.strip()
            self._api_response_cache[cache_key] = reply
            return reply
        except Exception as e:
            return f"Insight error: {str(e)}"

    async def chat(self, user_messages: list, pipeline_results: dict = None) -> str:
        if not self.client: return "AI Chatbot offline."
        
        # Extract the latest user query to filter KB
        latest_query = ""
        for msg in reversed(user_messages):
            if msg.get("role") == "user":
                latest_query = msg.get("content", "")
                break
                
        system_prompt = self._build_system_prompt(pipeline_results or {}, user_query=latest_query)
        messages = [{"role": "system", "content": system_prompt}] + user_messages
        
        try:
            response = await self.client.chat.completions.create(
                model=self.model_name,
                messages=messages,
                temperature=0.3,
                max_tokens=1000
            )
            return response.choices[0].message.content.strip()
        except Exception as e:
            return f"Chat error: {str(e)}"
