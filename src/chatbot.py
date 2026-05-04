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
        """Extract average yield and weather info, cached for performance."""
        if self._historical_context_cache:
            return self._historical_context_cache

        data = self._load_wb_data()
        if not data:
            return "No historical data available."
            
        context_lines = []
        
        # Optimized loading: Only use necessary columns/stats
        yield_df = data.get("rice_yield")
        if yield_df is not None and not yield_df.empty:
            stats = yield_df.agg({
                "Yield_kg_per_ha": "mean",
                "N_req_kg_per_ha": "mean",
                "P_req_kg_per_ha": "mean",
                "K_req_kg_per_ha": "mean"
            })
            context_lines.append(f"- Avg WB Yield: {stats['Yield_kg_per_ha']:.1f} kg/ha")
            context_lines.append(f"- Avg N-P-K: {stats['N_req_kg_per_ha']:.0f}-{stats['P_req_kg_per_ha']:.0f}-{stats['K_req_kg_per_ha']:.0f} kg/ha")
            
        weather_df = data.get("weather")
        if weather_df is not None and not weather_df.empty:
            stats = weather_df.agg({"Temperature": "mean", "Rainfall": "mean"})
            context_lines.append(f"- Hist. Weather: {stats['Temperature']:.1f}°C, {stats['Rainfall']:.1f}mm Rain")
            
        self._historical_context_cache = "\n".join(context_lines)
        return self._historical_context_cache

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

    def _build_system_prompt(self, pipeline_results: dict) -> str:
        historical = self._get_historical_context()
        realtime = self._format_pipeline_results(pipeline_results)
        
        # Load template lazily
        prompt_data = self._load_prompt_data()
        template = prompt_data.get("system_prompt", "") if prompt_data else "You are an AI Agriculture Assistant for West Bengal."
        
        return template.format(context=historical, pipeline_context=realtime)

    async def generate_initial_insight(self, pipeline_results: dict) -> str:
        """Generates contextual insight, using cache if identical results provided."""
        cache_key = json.dumps(pipeline_results, sort_keys=True)
        if cache_key in self._api_response_cache:
            return self._api_response_cache[cache_key]

        if not self.client: return "AI Chatbot unavailable."
            
        system_prompt = self._build_system_prompt(pipeline_results)
        user_msg = "Provide a concise, actionable agronomic recommendation based on these results."

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
        
        system_prompt = self._build_system_prompt(pipeline_results or {})
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
