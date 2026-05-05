"""Weather service for fetching real-time data and providing agricultural insights."""
import os
import datetime
import json
from collections import defaultdict
import requests

class WeatherService:
    def __init__(self):
        self.api_key = os.getenv("OPENWEATHER_API_KEY")
        self.base_url = "https://api.openweathermap.org/data/2.5/forecast"
        self.insights_data = self._load_agrochemical_insights()
        
    def _load_agrochemical_insights(self) -> dict:
        """Load data-driven thresholds from the analysis module."""
        try:
            insights_path = os.path.join(os.path.dirname(__file__), "analysis", "agrochemical_insights.json")
            if os.path.exists(insights_path):
                with open(insights_path, 'r') as f:
                    return json.load(f)
        except Exception as e:
            print(f"[Warning] Could not load agrochemical insights: {e}")
        return {}
        
    def get_forecast(self, lat: float, lon: float, crop_condition: str = None) -> dict:
        """Fetches 5-7 day forecast from OpenWeather API or returns mock data if key is missing."""
        if not self.api_key:
            return self._get_mock_data(lat, lon, crop_condition)
            
        try:
            # We use the 5-day / 3-hour forecast API as it's universally available on free tiers
            # without requiring a credit card, unlike One Call API 3.0.
            params = {
                "lat": lat,
                "lon": lon,
                "appid": self.api_key,
                "units": "metric"
            }
            response = requests.get(self.base_url, params=params, timeout=10)
            
            if response.status_code == 200:
                return self._parse_forecast_data(response.json(), crop_condition)
            elif response.status_code == 401:
                print(f"[Warning] OpenWeather API Key invalid or unauthorized. Using mock data.")
                return self._get_mock_data(lat, lon, crop_condition)
            else:
                response.raise_for_status()
                
        except Exception as e:
            print(f"[Error] Failed to fetch weather data: {e}. Using mock data.")
            return self._get_mock_data(lat, lon, crop_condition)

    def _parse_forecast_data(self, data: dict, crop_condition: str = None) -> dict:
        """Parses the 3-hour interval data into daily aggregates and derives insights."""
        daily_data = defaultdict(lambda: {
            "temp_max": -999,
            "temp_min": 999,
            "conditions": [],
            "icons": [],
            "wind_speeds": [],
            "humidities": [],
            "pops": []
        })
        
        for item in data.get("list", []):
            dt_txt = item.get("dt_txt", "")
            if not dt_txt:
                continue
                
            # Parse '2023-10-25 15:00:00' to date string '2023-10-25'
            date_str = dt_txt.split(" ")[0]
            date_obj = datetime.datetime.strptime(date_str, "%Y-%m-%d")
            
            # Map standard datetime weekday to shortened name
            day_name = date_obj.strftime("%a")
            
            temp_max = item["main"]["temp_max"]
            temp_min = item["main"]["temp_min"]
            condition = item["weather"][0]["main"] # e.g., Clouds, Rain, Clear
            icon = item["weather"][0]["icon"]
            wind_speed = item["wind"]["speed"] # in m/s
            humidity = item["main"].get("humidity", 50)
            pop = item.get("pop", 0.0) # Probability of precipitation (0 to 1)
            
            daily_data[date_str]["day_name"] = day_name
            daily_data[date_str]["date"] = date_str
            daily_data[date_str]["temp_max"] = max(daily_data[date_str]["temp_max"], temp_max)
            daily_data[date_str]["temp_min"] = min(daily_data[date_str]["temp_min"], temp_min)
            daily_data[date_str]["conditions"].append(condition)
            daily_data[date_str]["icons"].append(icon)
            daily_data[date_str]["wind_speeds"].append(wind_speed)
            daily_data[date_str]["humidities"].append(humidity)
            daily_data[date_str]["pops"].append(pop)

        # Build the final list (taking the most frequent condition/icon for the day)
        forecast_list = []
        for date_str, stats in list(daily_data.items())[:7]: # Limit to 7 days
            # Find most common condition
            most_common_condition = max(set(stats["conditions"]), key=stats["conditions"].count) if stats["conditions"] else "Clear"
            
            # Select appropriate icon based on condition priority (Rain/Thunderstorm > Clouds > Clear)
            priority_icons = [i for i in stats["icons"] if i.startswith(("11", "09", "10", "13"))] # Thunderstorm, Rain, Snow
            final_icon = priority_icons[0] if priority_icons else stats["icons"][len(stats["icons"])//2]
            
            # Map OpenWeather icon code to our internal name for the UI
            mapped_icon = self._map_icon(most_common_condition, final_icon)
            
            max_wind = max(stats["wind_speeds"]) if stats["wind_speeds"] else 0
            # Convert m/s to km/h
            max_wind_kmh = max_wind * 3.6
            
            avg_humidity = sum(stats["humidities"]) / len(stats["humidities"]) if stats["humidities"] else 50
            max_pop = max(stats["pops"]) if stats["pops"] else 0.0
            
            forecast_list.append({
                "day_name": stats["day_name"],
                "date": stats["date"],
                "temp_max": round(stats["temp_max"]),
                "temp_min": round(stats["temp_min"]),
                "condition": most_common_condition,
                "icon": mapped_icon,
                "max_wind_kmh": round(max_wind_kmh, 1),
                "humidity": round(avg_humidity),
                "pop": round(max_pop * 100) # percentage
            })
            
        # Generate Agricultural Insights based on the upcoming 48 hours (first 2 days)
        insights = self._generate_spraying_insights(forecast_list[:2], crop_condition)

        return {
            "success": True,
            "forecast": forecast_list,
            "insights": insights,
            "is_mock": False
        }

    def _map_icon(self, condition: str, icon_code: str) -> str:
        """Map OpenWeather condition to a generic icon name matching frontend Material Symbols."""
        condition = condition.lower()
        if "thunderstorm" in condition:
            return "thunderstorm"
        elif "rain" in condition or "drizzle" in condition:
            return "rainy"
        elif "snow" in condition:
            return "cloudy_snowing"
        elif "cloud" in condition:
            return "cloud"
        elif "clear" in condition:
            return "sunny"
        else:
            return "partly_cloudy_day"

    def _generate_spraying_insights(self, next_few_days: list, crop_condition: str = None) -> dict:
        """Analyze upcoming weather to determine if spraying pesticides/fertilizers is safe."""
        if not next_few_days:
            return {"status": "unsafe", "title": "Avoid Spraying", "message": "Weather data unavailable.", "actionable": "Check sensors or local reports before spraying."}
            
        today = next_few_days[0]
        wind_kmh = today["max_wind_kmh"]
        temp = today["temp_max"]
        humidity = today.get("humidity", 50)
        pop = today.get("pop", 0)
        condition = today["condition"].lower()
        
        is_rainy = "rain" in condition or "thunderstorm" in condition
        
        # Load data-driven thresholds or fallback to defaults
        thresholds = self.insights_data.get("thresholds", {})
        
        # Since annual mean windspeed from data was ~2 m/s, we convert to realistic daily km/h scale
        data_wind_unsafe = thresholds.get("windspeed", {}).get("unsafe", 2.0)
        unsafe_wind_threshold = data_wind_unsafe * 3.6 * 2 if data_wind_unsafe < 5 else 15
        
        data_temp_unsafe = thresholds.get("temperature", {}).get("unsafe", 35)
        unsafe_temp_threshold = max(data_temp_unsafe, 30) # at least 30C
        
        # Adjust recommendation based on crop condition
        condition_context = ""
        action_prefix = "Delay application"
        if crop_condition and crop_condition.lower() not in ["healthy", "normal"]:
            condition_context = f" considering the detection of {crop_condition}"
            action_prefix = f"{crop_condition} requires attention. However, delay application"
        
        # Rule 1: Unsafe conditions
        if wind_kmh > unsafe_wind_threshold:
            return {
                "status": "unsafe",
                "title": "Avoid Spraying",
                "message": f"Data indicates high wind speeds ({wind_kmh} km/h) reduce efficiency and pose drift risk{condition_context}.",
                "actionable": f"{action_prefix} until winds are calmer."
            }
        if pop >= 30 or is_rainy:
            return {
                "status": "unsafe",
                "title": "Avoid Spraying",
                "message": f"High probability of rain ({pop}%). Data shows rainfall causes nutrient/chemical leaching{condition_context}.",
                "actionable": f"{action_prefix} until there's a clear 24-hour dry window."
            }
        if temp > unsafe_temp_threshold:
            return {
                "status": "unsafe",
                "title": "Avoid Spraying",
                "message": f"Extreme heat ({temp}°C) affects agrochemical uptake and causes evaporation{condition_context}.",
                "actionable": "If you must spray, do so only during early morning or late evening."
            }
            
        # Rule 2: Moderate conditions
        if wind_kmh > unsafe_wind_threshold * 0.75:
            return {
                "status": "moderate",
                "title": "Moderate Spraying Conditions",
                "message": f"Wind speeds are slightly elevated ({wind_kmh} km/h).",
                "actionable": "Use drift-reducing nozzles and spray early in the morning when winds are lowest."
            }
        if pop > 10:
            return {
                "status": "moderate",
                "title": "Moderate Spraying Conditions",
                "message": f"There is a slight chance of rain ({pop}%).",
                "actionable": "Ensure your pesticide has enough drying time before any potential rainfall."
            }
        if humidity < 40:
            return {
                "status": "moderate",
                "title": "Moderate Spraying Conditions",
                "message": f"Low humidity ({humidity}%) can cause smaller droplets to evaporate before reaching the target.",
                "actionable": "Use larger droplet sizes or an adjuvant to improve coverage."
            }
            
        # Rule 3: Optimal conditions
        actionable_optimal = "Best time window: 6 AM to 10 AM or late afternoon. Proceed with standard application."
        if crop_condition and crop_condition.lower() not in ["healthy", "normal"]:
             actionable_optimal = f"Optimal conditions for treating {crop_condition}. Proceed with recommended fungicide/pesticide application."
             
        return {
            "status": "optimal",
            "title": "Optimal Spraying Conditions",
            "message": f"Data-backed optimal conditions: Low wind ({wind_kmh} km/h), no rain, moderate temperature ({temp}°C).",
            "actionable": actionable_optimal
        }

    def _get_mock_data(self, lat: float, lon: float, crop_condition: str = None) -> dict:
        """Returns realistic mock data when API key is missing or invalid."""
        base_date = datetime.datetime.now()
        
        mock_forecast = []
        conditions = [
            ("Clear", "sunny", 34, 25, 10, 60, 0),
            ("Rain", "rainy", 31, 26, 16, 85, 0.8),
            ("Thunderstorm", "thunderstorm", 33, 26, 12, 90, 0.9),
            ("Thunderstorm", "thunderstorm", 33, 26, 8, 80, 0.5),
            ("Clouds", "cloud", 34, 26, 5, 55, 0.15),
            ("Rain", "rainy", 35, 27, 20, 75, 0.4),
            ("Clear", "sunny", 33, 26, 10, 50, 0)
        ]
        
        for i in range(7):
            current_date = base_date + datetime.timedelta(days=i)
            condition, icon, tmax, tmin, wind, humidity, pop = conditions[i % len(conditions)]
            mock_forecast.append({
                "day_name": current_date.strftime("%a"),
                "date": current_date.strftime("%Y-%m-%d"),
                "temp_max": tmax,
                "temp_min": tmin,
                "condition": condition,
                "icon": icon,
                "max_wind_kmh": wind,
                "humidity": humidity,
                "pop": int(pop * 100)
            })
            
        return {
            "success": True,
            "forecast": mock_forecast,
            "insights": self._generate_spraying_insights(mock_forecast[:2], crop_condition),
            "is_mock": True
        }
