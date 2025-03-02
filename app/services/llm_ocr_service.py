import base64
import os
from typing import Dict, Optional
from openai import AsyncOpenAI
import json

class LLMOCRService:
    def __init__(self, api_key: str = None):
        self.api_key = api_key or os.getenv("OPENAI_API_KEY")
        self.client = AsyncOpenAI(api_key=self.api_key)
        
        # System prompt for consistent formatting
        self.system_prompt = """You are a specialized AI for analyzing Call of Duty match result screens.
        Extract and return the following information in a consistent JSON format:
        - Team scores
        - Player stats (kills, deaths, assists)
        - Game mode
        - Map name
        Be precise and only return valid JSON."""

    async def process_image(self, image_bytes: bytes) -> Optional[Dict]:
        """
        Process a COD stat screen image using ChatGPT Vision API.
        """
        try:
            # Convert image bytes to base64
            encoded_image = base64.b64encode(image_bytes).decode()
            
            # Prepare the message for GPT-4 Vision
            messages = [
                {
                    "role": "system",
                    "content": self.system_prompt
                },
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "text",
                            "text": "Analyze this Call of Duty match result screen and extract the key statistics in JSON format."
                        },
                        {
                            "type": "image_url",
                            "image_url": {
                                "url": f"data:image/jpeg;base64,{encoded_image}"
                            }
                        }
                    ]
                }
            ]

            # Call GPT-4 Vision API
            response = await self.client.chat.completions.create(
                model="gpt-4-vision-preview",
                messages=messages,
                max_tokens=500,
                temperature=0.1  # Low temperature for consistent formatting
            )

            # Extract and parse the JSON response
            try:
                content = response.choices[0].message.content
                # Find JSON content between triple backticks if present
                if "```json" in content:
                    json_str = content.split("```json")[1].split("```")[0]
                else:
                    json_str = content
                
                stats = json.loads(json_str)
                return self._normalize_stats(stats)
            except json.JSONDecodeError:
                print("Failed to parse JSON from GPT response")
                return None

        except Exception as e:
            print(f"Error processing image with ChatGPT: {str(e)}")
            return None

    def _normalize_stats(self, stats: Dict) -> Dict:
        """
        Normalize the stats into a consistent format regardless of GPT's response structure.
        """
        normalized = {
            "team_scores": {},
            "player_stats": {},
            "game_info": {}
        }

        # Extract team scores
        if "team_scores" in stats:
            normalized["team_scores"] = stats["team_scores"]
        elif "teams" in stats:
            normalized["team_scores"] = stats["teams"]

        # Extract player stats
        if "player_stats" in stats:
            normalized["player_stats"] = stats["player_stats"]
        else:
            # Try to find stats in root level
            for key in ["kills", "deaths", "assists"]:
                if key in stats:
                    normalized["player_stats"][key] = stats[key]

        # Extract game info
        if "game_info" in stats:
            normalized["game_info"] = stats["game_info"]
        else:
            for key in ["mode", "map"]:
                if key in stats:
                    normalized["game_info"][key] = stats[key]

        return normalized

    def validate_stats(self, stats: Dict) -> bool:
        """
        Validate that the extracted stats make sense for a COD game.
        """
        if not stats:
            return False

        try:
            player_stats = stats.get("player_stats", {})
            
            # Basic validation rules
            if not all(key in player_stats for key in ["kills", "deaths", "assists"]):
                return False

            # Validate reasonable ranges for COD stats
            if not (0 <= player_stats["kills"] <= 100 and 
                   0 <= player_stats["deaths"] <= 100 and
                   0 <= player_stats["assists"] <= 50):
                return False

            # Validate team scores if present
            team_scores = stats.get("team_scores", {})
            if team_scores:
                for score in team_scores.values():
                    if not isinstance(score, (int, float)) or score < 0:
                        return False

            # Validate game info if present
            game_info = stats.get("game_info", {})
            if game_info:
                if "mode" in game_info and not isinstance(game_info["mode"], str):
                    return False
                if "map" in game_info and not isinstance(game_info["map"], str):
                    return False

            return True

        except Exception as e:
            print(f"Error validating stats: {str(e)}")
            return False 