import requests
import logging
from typing import Dict, List, Tuple
from django.conf import settings
from datetime import datetime, timedelta
import json
import os

logger = logging.getLogger(__name__)

class RiotAPIError(Exception):
    """Custom exception for Riot API errors"""
    pass

class ChampionData:
    """Champion data management using Riot's Data Dragon"""
    
    def __init__(self):
        self.champions = {}
        self.last_update = None
        self.update_interval = timedelta(hours=24)  # Update once per day
        self.load_champion_data()
    
    def load_champion_data(self):
        """Load champion data from Data Dragon or local cache"""
        try:
            # Check if we need to update
            if (self.last_update and 
                datetime.now() - self.last_update < self.update_interval and 
                self.champions):
                return
            
            # Try to load from local cache first
            cache_file = os.path.join(settings.BASE_DIR, 'champion_cache.json')
            if os.path.exists(cache_file):
                try:
                    with open(cache_file, 'r') as f:
                        data = json.load(f)
                        self.champions = data.get('champions', {})
                        self.last_update = datetime.fromisoformat(data.get('last_update', '2020-01-01'))
                        if datetime.now() - self.last_update < self.update_interval:
                            logger.info("Using cached champion data")
                            return
                except Exception as e:
                    logger.warning(f"Failed to load cached champion data: {e}")
            
            # Fetch from Data Dragon
            logger.info("Fetching champion data from Data Dragon")
            response = requests.get('https://ddragon.leagueoflegends.com/api/versions.json')
            if response.status_code == 200:
                versions = response.json()
                latest_version = versions[0]
                
                champion_response = requests.get(f'https://ddragon.leagueoflegends.com/cdn/{latest_version}/data/en_US/champion.json')
                if champion_response.status_code == 200:
                    champion_data = champion_response.json()
                    
                    # Build champion ID to name mapping
                    for champion_id, champion_info in champion_data['data'].items():
                        self.champions[int(champion_info['key'])] = champion_info['name']
                    
                    # Save to cache
                    try:
                        with open(cache_file, 'w') as f:
                            json.dump({
                                'champions': self.champions,
                                'last_update': datetime.now().isoformat()
                            }, f)
                    except Exception as e:
                        logger.warning(f"Failed to save champion cache: {e}")
                    
                    self.last_update = datetime.now()
                    logger.info(f"Loaded {len(self.champions)} champions from Data Dragon")
                else:
                    logger.error("Failed to fetch champion data from Data Dragon")
            else:
                logger.error("Failed to fetch version data from Data Dragon")
                
        except Exception as e:
            logger.error(f"Error loading champion data: {e}")
            # Fallback to basic champion list
            self.champions = {
                1: "Annie", 2: "Olaf", 3: "Galio", 4: "Twisted Fate", 5: "Xin Zhao",
                6: "Urgot", 7: "LeBlanc", 8: "Vladimir", 9: "Fiddlesticks", 10: "Kayle",
                11: "Master Yi", 12: "Alistar", 13: "Ryze", 14: "Sion", 15: "Sivir",
                16: "Soraka", 17: "Teemo", 18: "Tristana", 19: "Warwick", 20: "Nunu & Willump",
                21: "Miss Fortune", 22: "Ashe", 23: "Tryndamere", 24: "Jax", 25: "Morgana",
                26: "Zilean", 27: "Singed", 28: "Evelynn", 29: "Twitch", 30: "Karthus",
                31: "Chogath", 32: "Amumu", 33: "Rammus", 34: "Anivia", 35: "Shaco",
                36: "Dr. Mundo", 37: "Sona", 38: "Kassadin", 39: "Irelia", 40: "Janna",
                41: "Gangplank", 42: "Corki", 43: "Karma", 44: "Taric", 45: "Veigar",
                48: "Trundle", 50: "Swain", 51: "Caitlyn", 53: "Blitzcrank", 54: "Malphite",
                55: "Katarina", 56: "Nocturne", 57: "Maokai", 58: "Renekton", 59: "Jarvan IV",
                60: "Elise", 61: "Orianna", 62: "Wukong", 63: "Brand", 64: "Lee Sin",
                67: "Vayne", 68: "Rumble", 69: "Cassiopeia", 72: "Skarner", 74: "Heimerdinger",
                75: "Nasus", 76: "Nidalee", 77: "Udyr", 78: "Poppy", 79: "Gragas",
                80: "Pantheon", 81: "Ezreal", 82: "Mordekaiser", 83: "Yorick", 84: "Akali",
                85: "Kennen", 86: "Garen", 89: "Leona", 90: "Malzahar", 91: "Talon",
                92: "Riven", 96: "KogMaw", 98: "Shen", 99: "Lux", 101: "Xerath",
                102: "Shyvana", 103: "Ahri", 104: "Graves", 105: "Fizz", 106: "Volibear",
                107: "Rengar", 110: "Varus", 111: "Nautilus", 112: "Viktor", 113: "Sejuani",
                114: "Fiora", 115: "Ziggs", 117: "Lulu", 119: "Draven", 120: "Hecarim",
                121: "Khazix", 122: "Darius", 126: "Jayce", 127: "Lissandra", 131: "Diana",
                133: "Quinn", 134: "Syndra", 136: "Aurelion Sol", 141: "Kayn", 142: "Zoe",
                143: "Zyra", 145: "Kaisa", 147: "Seraphine", 150: "Gnar", 154: "Zac",
                157: "Yasuo", 161: "Velkoz", 163: "Taliyah", 164: "Camille", 166: "Akshan",
                200: "Belveth", 201: "Braum", 202: "Jhin", 203: "Kindred", 221: "Zeri",
                222: "Jinx", 223: "Tahm Kench", 234: "Viego", 235: "Senna", 236: "Lucian",
                238: "Zed", 240: "Kled", 245: "Ekko", 246: "Qiyana", 254: "Vi", 266: "Aatrox",
                267: "Nami", 268: "Azir", 350: "Yuumi", 360: "Samira", 412: "Thresh",
                420: "Illaoi", 421: "RekSai", 427: "Ivern", 429: "Kalista", 432: "Bard",
                516: "Ornn", 517: "Sylas", 518: "Neeko", 523: "Aphelios", 526: "Rell",
                555: "Pyke", 711: "Vex", 777: "Yone", 875: "Sett", 876: "Lillia",
                887: "Gwen", 888: "Renata Glasc", 895: "Nilah", 897: "KSante", 902: "Milio",
                950: "Naafiri", 901: "Briar", 902: "Milio", 903: "Hwei", 904: "Smolder"
            }
    
    def get_champion_name(self, champion_id: int) -> str:
        """Get champion name by ID"""
        return self.champions.get(champion_id, f"Champion_{champion_id}")

# Global champion data instance
champion_data = ChampionData()


class RiotAPIService:
    """Service for interacting with Riot Games API"""
    
    def __init__(self):
        self.api_key = settings.RIOT_API_KEY
        if not self.api_key:
            raise ValueError("RIOT_API_KEY is required")
        
        # Regional routing values for different APIs
        self.regional_routing = {
            'na1': 'americas',
            'euw1': 'europe', 
            'eun1': 'europe',
            'kr': 'asia',
            'jp1': 'asia',
            'br1': 'americas',
            'la1': 'americas',
            'la2': 'americas',
            'oc1': 'americas',
            'tr1': 'europe',
            'ru': 'europe',
        }
        
        self.base_urls = {
            'americas': 'https://americas.api.riotgames.com',
            'europe': 'https://europe.api.riotgames.com',
            'asia': 'https://asia.api.riotgames.com',
        }
        
        self.platform_urls = {
            'na1': 'https://na1.api.riotgames.com',
            'euw1': 'https://euw1.api.riotgames.com',
            'eun1': 'https://eun1.api.riotgames.com',
            'kr': 'https://kr.api.riotgames.com',
            'jp1': 'https://jp1.api.riotgames.com',
            'br1': 'https://br1.api.riotgames.com',
            'la1': 'https://la1.api.riotgames.com',
            'la2': 'https://la2.api.riotgames.com',
            'oc1': 'https://oc1.api.riotgames.com',
            'tr1': 'https://tr1.api.riotgames.com',
            'ru': 'https://ru.api.riotgames.com',
        }

    def _make_request(self, url: str, params: Dict = None) -> Dict:
        """Make a request to the Riot API"""
        headers = {
            'X-Riot-Token': self.api_key
        }
        
        logger.info(f"Making Riot API request to: {url}")
        if params:
            logger.info(f"Request parameters: {params}")
        
        try:
            response = requests.get(url, headers=headers, params=params)
            logger.info(f"Riot API response status: {response.status_code}")
            
            if response.status_code == 200:
                data = response.json()
                logger.info(f"Riot API response data keys: {list(data.keys()) if isinstance(data, dict) else 'Not a dict'}")
                return data
            else:
                logger.error(f"Riot API error response: {response.status_code} - {response.text}")
                response.raise_for_status()
                
        except requests.exceptions.HTTPError as e:
            if response.status_code == 429:
                logger.error("Riot API rate limit exceeded")
                raise RiotAPIError("Rate limit exceeded. Please try again later.")
            elif response.status_code == 404:
                logger.error(f"Riot API resource not found: {url}")
                raise RiotAPIError("Summoner not found. Please check the Riot ID.")
            else:
                logger.error(f"Riot API HTTP error {response.status_code}: {e}")
                raise RiotAPIError(f"API request failed: {e}")
        except requests.exceptions.RequestException as e:
            logger.error(f"Riot API request failed: {e}")
            raise RiotAPIError(f"API request failed: {e}")

    def get_summoner_by_riot_id(self, riot_id: str, region: str = 'na1') -> Dict:
        """Get summoner information by Riot ID"""
        if '#' not in riot_id:
            raise ValueError("Riot ID must be in format 'SummonerName#TAG'")
        
        game_name, tag_line = riot_id.split('#', 1)
        
        # Use regional routing for account API
        regional = self.regional_routing.get(region, 'americas')
        url = f"{self.base_urls[regional]}/riot/account/v1/accounts/by-riot-id/{game_name}/{tag_line}"
        return self._make_request(url)

    def get_summoner_by_puuid(self, puuid: str, region: str = 'na1') -> Dict:
        """Get summoner information by PUUID"""
        url = f"{self.platform_urls[region]}/lol/summoner/v4/summoners/by-puuid/{puuid}"
        return self._make_request(url)

    def get_match_ids(self, puuid: str, region: str = 'na1', count: int = 20, start_time: int = None, end_time: int = None) -> List[str]:
        """Get match IDs for a player with optional date range"""
        # Use regional routing for match API
        regional = self.regional_routing.get(region, 'americas')
        url = f"{self.base_urls[regional]}/lol/match/v5/matches/by-puuid/{puuid}/ids"
        params = {'count': count}
        
        # Add date range parameters if provided
        if start_time:
            params['startTime'] = start_time
        if end_time:
            params['endTime'] = end_time
        
        response = self._make_request(url, params)
        logger.info(f"Match IDs response type: {type(response)}, content: {response}")
        
        # The Riot API returns a list directly, not a dict with 'matchIds' key
        if isinstance(response, list):
            return response
        elif isinstance(response, dict):
            return response.get('matchIds', [])
        else:
            logger.error(f"Unexpected response type for match IDs: {type(response)}")
            return []

    def get_match_ids_by_date_range(self, puuid: str, region: str = 'na1', date_from: str = None, date_to: str = None, count: int = 100) -> List[str]:
        """Get match IDs for a player within a specific date range"""
        import time
        from datetime import datetime
        
        params = {'count': count}
        
        # Convert date strings to timestamps (milliseconds since epoch)
        if date_from:
            try:
                start_date = datetime.strptime(date_from, '%Y-%m-%d')
                start_timestamp = int(start_date.timestamp() * 1000)
                params['startTime'] = start_timestamp
                logger.info(f"Querying matches from {date_from} (timestamp: {start_timestamp})")
            except ValueError as e:
                logger.error(f"Invalid date_from format: {date_from}. Expected YYYY-MM-DD")
                raise ValueError(f"Invalid date format: {date_from}. Expected YYYY-MM-DD")
        
        if date_to:
            try:
                end_date = datetime.strptime(date_to, '%Y-%m-%d')
                # Add one day to include the entire end date
                end_date = end_date.replace(hour=23, minute=59, second=59)
                end_timestamp = int(end_date.timestamp() * 1000)
                params['endTime'] = end_timestamp
                logger.info(f"Querying matches until {date_to} (timestamp: {end_timestamp})")
            except ValueError as e:
                logger.error(f"Invalid date_to format: {date_to}. Expected YYYY-MM-DD")
                raise ValueError(f"Invalid date format: {date_to}. Expected YYYY-MM-DD")
        
        return self.get_match_ids(puuid, region, count, params.get('startTime'), params.get('endTime'))

    def get_match_details(self, match_id: str, region: str = 'na1') -> Dict:
        """Get detailed match information"""
        # Use regional routing for match API
        regional = self.regional_routing.get(region, 'americas')
        url = f"{self.base_urls[regional]}/lol/match/v5/matches/{match_id}"
        return self._make_request(url)

    def parse_match_data(self, match_data: Dict) -> Tuple[Dict, List[Dict]]:
        """Parse match data into our database format"""
        info = match_data.get('info', {})
        
        match_info = {
            'match_id': match_data.get('metadata', {}).get('matchId'),
            'game_mode': info.get('gameMode'),
            'game_type': info.get('gameType'),
            'queue_id': info.get('queueId', 0),  # Default to 0 if not present
            'game_duration': info.get('gameDuration'),
            'game_creation': info.get('gameCreation'),
            'platform_id': match_data.get('metadata', {}).get('platformId', 'NA1'),  # Default to NA1 if not present
        }
        
        participants_data = []
        for participant in info.get('participants', []):
            # Handle both old and new summoner name fields
            summoner_name = participant.get('riotIdGameName') or participant.get('summonerName', 'Unknown')
            
            participant_info = {
                'puuid': participant.get('puuid'),
                'summoner_name': summoner_name,
                'champion_id': participant.get('championId'),
                'champion_name': champion_data.get_champion_name(participant.get('championId')),
                'team_id': participant.get('teamId'),
                'win': participant.get('win'),
                'kills': participant.get('kills', 0),
                'deaths': participant.get('deaths', 0),
                'assists': participant.get('assists', 0),
                'gold_earned': participant.get('goldEarned', 0),
                'total_damage_dealt': participant.get('totalDamageDealt', 0),
                'total_damage_taken': participant.get('totalDamageTaken', 0),
                'vision_score': participant.get('visionScore', 0),
                'cs': participant.get('totalMinionsKilled', 0) + participant.get('neutralMinionsKilled', 0),
                'role': participant.get('role', ''),
                'lane': participant.get('individualPosition', ''),
            }
            participants_data.append(participant_info)
        
        return match_info, participants_data

    def test_api_connection(self, region: str = 'na1') -> Dict:
        """Test API connection by getting a simple endpoint"""
        try:
            # Test with a simple endpoint - get summoner by name (this is just for testing)
            # In practice, you'd want to test with a known summoner
            regional = self.regional_routing.get(region, 'americas')
            url = f"{self.base_urls[regional]}/lol/summoner/v4/summoners/by-name/test"
            
            # This will likely fail with 404, but it will test the connection
            response = requests.get(url, headers={'X-Riot-Token': self.api_key})
            
            return {
                'status': 'connected',
                'api_key_valid': response.status_code != 401,
                'rate_limited': response.status_code == 429,
                'test_url': url,
                'response_code': response.status_code
            }
        except Exception as e:
            return {
                'status': 'error',
                'error': str(e),
                'api_key_valid': False
            } 