import axios from 'axios';
import { Friend } from '../types';

const API_BASE_URL = process.env.REACT_APP_API_URL || '/api';

export const friendService = {
  async getFriends(): Promise<Friend[]> {
    const response = await axios.get(`${API_BASE_URL}/friends/`);
    // Handle paginated response from Django REST Framework
    return response.data.results || response.data;
  },

  async addFriend(riotId: string, region: string = 'na1', matchCount: number = 50, dateFrom?: string, dateTo?: string): Promise<Friend> {
    const response = await axios.post(`${API_BASE_URL}/friends/add-by-riot-id/`, {
      riot_id: riotId,
      region,
      match_count: matchCount,
      date_from: dateFrom,
      date_to: dateTo
    });
    return response.data.friend;
  },

  async updateFriend(friendId: number, matchCount: number, dateFrom?: string, dateTo?: string): Promise<Friend> {
    const response = await axios.put(`${API_BASE_URL}/friends/${friendId}/`, {
      match_count: matchCount,
      date_from: dateFrom,
      date_to: dateTo
    });
    return response.data;
  },

  async deleteFriend(friendId: number): Promise<void> {
    await axios.delete(`${API_BASE_URL}/friends/${friendId}/`);
  },

  async refreshMatches(puuid: string): Promise<void> {
    await axios.post(`${API_BASE_URL}/matches/refresh/${puuid}/`);
  }
}; 