import axios from 'axios';
import { AnalysisTile, CreateTileData, Match } from '../types';

const API_BASE_URL = process.env.REACT_APP_API_URL || '/api';

export const tileService = {
  async getTiles(): Promise<AnalysisTile[]> {
    const response = await axios.get(`${API_BASE_URL}/tiles/`);
    // Handle paginated response from Django REST Framework
    return response.data.results || response.data;
  },

  async createTile(tileData: CreateTileData): Promise<AnalysisTile> {
    console.log('tileService: Sending tile data:', tileData);
    try {
      const response = await axios.post(`${API_BASE_URL}/tiles/`, tileData);
      console.log('tileService: Response received:', response.data);
      return response.data;
    } catch (error: any) {
      console.error('tileService: Error creating tile:', error);
      console.error('tileService: Error response data:', error.response?.data);
      console.error('tileService: Error status:', error.response?.status);
      throw error;
    }
  },

  async updateTile(tileId: number, tileData: Partial<CreateTileData>): Promise<AnalysisTile> {
    const response = await axios.put(`${API_BASE_URL}/tiles/${tileId}/`, tileData);
    return response.data;
  },

  async deleteTile(tileId: number): Promise<void> {
    await axios.delete(`${API_BASE_URL}/tiles/${tileId}/`);
  },

  async getTileMatches(tileId: number): Promise<Match[]> {
    const response = await axios.get(`${API_BASE_URL}/tiles/${tileId}/matches/`);
    // Handle paginated response from Django REST Framework
    return response.data.results || response.data;
  },
}; 