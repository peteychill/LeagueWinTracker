import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import {
  Grid,
  Card,
  CardContent,
  Typography,
  Box,
  Button,
  CircularProgress,
  Alert,
} from '@mui/material';
import { PieChart, Pie, Cell, ResponsiveContainer, Tooltip, Legend } from 'recharts';
import { AnalysisTile } from '../types';
import { tileService } from '../services/tileService';

const COLORS = ['#0088FE', '#00C49F', '#FFBB28', '#FF8042', '#8884D8'];

const Dashboard: React.FC = () => {
  const navigate = useNavigate();
  const [tiles, setTiles] = useState<AnalysisTile[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');

  useEffect(() => {
    loadTiles();
  }, []);

  const loadTiles = async () => {
    try {
      setLoading(true);
      const data = await tileService.getTiles();
      setTiles(data);
    } catch (error: any) {
      setError('Failed to load analysis tiles');
    } finally {
      setLoading(false);
    }
  };

  const getOverallStats = () => {
    if (tiles.length === 0) return { totalTiles: 0, avgWinRate: 0, totalMatches: 0 };
    
    const totalMatches = tiles.reduce((sum, tile) => sum + tile.total_matches, 0);
    const avgWinRate = tiles.reduce((sum, tile) => sum + tile.win_rate, 0) / tiles.length;
    
    return {
      totalTiles: tiles.length,
      avgWinRate: Math.round(avgWinRate * 100) / 100,
      totalMatches,
    };
  };

  const getChartData = () => {
    return tiles.map((tile, index) => ({
      name: tile.name,
      value: tile.win_rate,
      color: COLORS[index % COLORS.length],
    }));
  };

  const stats = getOverallStats();
  const chartData = getChartData();

  if (loading) {
    return (
      <Box display="flex" justifyContent="center" alignItems="center" minHeight="400px">
        <CircularProgress />
      </Box>
    );
  }

  return (
    <Box>
      <Typography variant="h4" gutterBottom>
        Dashboard
      </Typography>

      {error && (
        <Alert severity="error" sx={{ mb: 2 }}>
          {error}
        </Alert>
      )}

      {/* Overall Stats */}
      <Grid container spacing={3} sx={{ mb: 4 }}>
        <Grid item xs={12} md={4}>
          <Card>
            <CardContent>
              <Typography color="textSecondary" gutterBottom>
                Total Analysis Tiles
              </Typography>
              <Typography variant="h3" component="div">
                {stats.totalTiles}
              </Typography>
            </CardContent>
          </Card>
        </Grid>
        <Grid item xs={12} md={4}>
          <Card>
            <CardContent>
              <Typography color="textSecondary" gutterBottom>
                Average Win Rate
              </Typography>
              <Typography variant="h3" component="div">
                {stats.avgWinRate}%
              </Typography>
            </CardContent>
          </Card>
        </Grid>
        <Grid item xs={12} md={4}>
          <Card>
            <CardContent>
              <Typography color="textSecondary" gutterBottom>
                Total Matches Analyzed
              </Typography>
              <Typography variant="h3" component="div">
                {stats.totalMatches}
              </Typography>
            </CardContent>
          </Card>
        </Grid>
      </Grid>

      {/* Win Rate Chart */}
      {tiles.length > 0 && (
        <Grid container spacing={3}>
          <Grid item xs={12} md={6}>
            <Card>
              <CardContent>
                <Typography variant="h6" gutterBottom>
                  Win Rates by Tile
                </Typography>
                <ResponsiveContainer width="100%" height={300}>
                  <PieChart>
                    <Pie
                      data={chartData}
                      cx="50%"
                      cy="50%"
                      labelLine={false}
                      label={({ name, value }) => `${name}: ${value}%`}
                      outerRadius={80}
                      fill="#8884d8"
                      dataKey="value"
                    >
                      {chartData.map((entry, index) => (
                        <Cell key={`cell-${index}`} fill={entry.color} />
                      ))}
                    </Pie>
                    <Tooltip />
                    <Legend />
                  </PieChart>
                </ResponsiveContainer>
              </CardContent>
            </Card>
          </Grid>

          <Grid item xs={12} md={6}>
            <Card>
              <CardContent>
                <Typography variant="h6" gutterBottom>
                  Recent Tiles
                </Typography>
                {tiles.slice(0, 5).map((tile) => (
                  <Box key={tile.id} sx={{ mb: 2, p: 2, border: '1px solid #333', borderRadius: 1 }}>
                    <Typography variant="subtitle1" fontWeight="bold">
                      {tile.name}
                    </Typography>
                    <Typography variant="body2" color="textSecondary">
                      Win Rate: {tile.win_rate}% ({tile.wins}W - {tile.losses}L)
                    </Typography>
                    <Typography variant="body2" color="textSecondary">
                      {tile.friends.map(f => f.summoner_name).join(', ')}
                    </Typography>
                  </Box>
                ))}
              </CardContent>
            </Card>
          </Grid>
        </Grid>
      )}

      {tiles.length === 0 && (
        <Card>
          <CardContent sx={{ textAlign: 'center', py: 4 }}>
            <Typography variant="h6" color="textSecondary" gutterBottom>
              No Analysis Tiles Yet
            </Typography>
            <Typography variant="body2" color="textSecondary" sx={{ mb: 2 }}>
              Create your first analysis tile to start tracking win rates with your friends.
            </Typography>
            <Button variant="contained" onClick={() => navigate('/tiles')}>
              Create First Tile
            </Button>
          </CardContent>
        </Card>
      )}
    </Box>
  );
};

export default Dashboard; 