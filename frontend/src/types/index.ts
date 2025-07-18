export interface User {
  id: number;
  username: string;
  email: string;
}

export interface UserProfile {
  id: number;
  user: User;
  riot_id: string;
  puuid: string;
  summoner_name: string;
  tag_line: string;
  region: string;
  last_match_sync: string | null;
}

export interface Friend {
  id: number;
  riot_id: string;
  puuid: string;
  summoner_name: string;
  tag_line: string;
  region: string;
  match_count: number;
  date_from?: string;
  date_to?: string;
  total_matches_fetched: number;
  created_at: string;
}

export interface MatchParticipant {
  puuid: string;
  summoner_name: string;
  champion_id: number;
  champion_name: string;
  team_id: number;
  win: boolean;
  kills: number;
  deaths: number;
  assists: number;
  gold_earned: number;
  total_damage_dealt: number;
  total_damage_taken: number;
  vision_score: number;
  cs: number;
  role: string;
  lane: string;
}

export interface Match {
  id: number;
  match_id: string;
  game_mode: string;
  game_type: string;
  queue_id: number;
  game_duration: number;
  game_creation: number;
  platform_id: string;
  participants: MatchParticipant[];
}

export interface AnalysisTile {
  id: number;
  name: string;
  friends: Friend[];
  match_filter: 'inclusive' | 'exclusive';
  date_from?: string;
  date_to?: string;
  max_matches_per_tile: number;
  win_rate: number;
  wins: number;
  losses: number;
  total_matches: number;
  created_at: string;
}

export interface CreateTileData {
  name: string;
  friend_ids: number[];
  match_filter: 'inclusive' | 'exclusive';
  date_from?: string;
  date_to?: string;
  max_matches_per_tile?: number;
}

export interface LoginData {
  username: string;
  password: string;
}

export interface RegisterData {
  username: string;
  email: string;
  password: string;
  password_confirm: string;
}

export interface AddFriendData {
  riot_id: string;
  region: string;
} 