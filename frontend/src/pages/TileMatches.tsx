import React, { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import {
  Box,
  Typography,
  Card,
  CardContent,
  Grid,
  Chip,
  IconButton,
  Alert,
  CircularProgress,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  Paper,
  Divider,
  Tooltip,
} from '@mui/material';
import {
  ArrowBack,
  CheckCircle,
  Cancel,
  Person,
  Timer,
} from '@mui/icons-material';
import { Match, AnalysisTile } from '../types';
import { tileService } from '../services/tileService';

const TileMatches: React.FC = () => {
  const { tileId } = useParams<{ tileId: string }>();
  const navigate = useNavigate();
  const [matches, setMatches] = useState<Match[]>([]);
  const [tile, setTile] = useState<AnalysisTile | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');

  useEffect(() => {
    if (tileId) {
      loadTileMatches(parseInt(tileId));
    }
  }, [tileId]);

  const loadTileMatches = async (id: number) => {
    try {
      setLoading(true);
      const [matchesData, tilesData] = await Promise.all([
        tileService.getTileMatches(id),
        tileService.getTiles(),
      ]);
      setMatches(matchesData);
      const currentTile = tilesData.find(t => t.id === id);
      setTile(currentTile || null);
    } catch (error: any) {
      setError('Failed to load tile matches');
    } finally {
      setLoading(false);
    }
  };

  const formatDuration = (seconds: number) => {
    const minutes = Math.floor(seconds / 60);
    const remainingSeconds = seconds % 60;
    return `${minutes}:${remainingSeconds.toString().padStart(2, '0')}`;
  };

  const formatDate = (timestamp: number) => {
    return new Date(timestamp).toLocaleDateString('en-US', {
      year: 'numeric',
      month: 'short',
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit',
    });
  };

  const getWinRateColor = (winRate: number) => {
    if (winRate >= 60) return 'success';
    if (winRate >= 50) return 'warning';
    return 'error';
  };

  const getLaneIcon = (lane: string) => {
    switch (lane.toUpperCase()) {
      case 'TOP': return '🏔️';
      case 'JUNGLE': return '🌲';
      case 'MIDDLE': return '⚔️';
      case 'BOTTOM': return '🏹';
      case 'UTILITY': return '🛡️';
      default: return '❓';
    }
  };

  if (loading) {
    return (
      <Box display="flex" justifyContent="center" alignItems="center" minHeight="400px">
        <CircularProgress />
      </Box>
    );
  }

  if (!tile) {
    return (
      <Box>
        <Alert severity="error">Tile not found</Alert>
      </Box>
    );
  }

  return (
    <Box>
      {/* Header */}
      <Box display="flex" alignItems="center" mb={3}>
        <IconButton onClick={() => navigate('/tiles')} sx={{ mr: 2 }}>
          <ArrowBack />
        </IconButton>
        <Box>
          <Typography variant="h4" gutterBottom>
            {tile.name}
          </Typography>
          <Typography variant="body1" color="textSecondary">
            {tile.friends.map(f => f.summoner_name).join(', ')}
          </Typography>
        </Box>
      </Box>

      {error && (
        <Alert severity="error" sx={{ mb: 2 }} onClose={() => setError('')}>
          {error}
        </Alert>
      )}

      {/* Tile Stats */}
      <Grid container spacing={3} sx={{ mb: 4 }}>
        <Grid item xs={12} md={3}>
          <Card>
            <CardContent>
              <Typography color="textSecondary" gutterBottom>
                Win Rate
              </Typography>
              <Typography variant="h4" color={`${getWinRateColor(tile.win_rate)}.main`}>
                {tile.win_rate.toFixed(1)}%
              </Typography>
            </CardContent>
          </Card>
        </Grid>
        <Grid item xs={12} md={3}>
          <Card>
            <CardContent>
              <Typography color="textSecondary" gutterBottom>
                Total Matches
              </Typography>
              <Typography variant="h4">
                {tile.total_matches}
              </Typography>
            </CardContent>
          </Card>
        </Grid>
        <Grid item xs={12} md={3}>
          <Card>
            <CardContent>
              <Typography color="textSecondary" gutterBottom>
                Wins
              </Typography>
              <Typography variant="h4" color="success.main">
                {tile.wins}
              </Typography>
            </CardContent>
          </Card>
        </Grid>
        <Grid item xs={12} md={3}>
          <Card>
            <CardContent>
              <Typography color="textSecondary" gutterBottom>
                Losses
              </Typography>
              <Typography variant="h4" color="error.main">
                {tile.losses}
              </Typography>
            </CardContent>
          </Card>
        </Grid>
      </Grid>

      {/* Matches */}
      <Typography variant="h5" gutterBottom>
        Match History ({matches.length} matches)
      </Typography>

      {matches.length === 0 ? (
        <Card>
          <CardContent sx={{ textAlign: 'center', py: 4 }}>
            <Typography variant="h6" color="textSecondary" gutterBottom>
              No Matches Found
            </Typography>
            <Typography variant="body2" color="textSecondary">
              No matches found for this tile configuration.
            </Typography>
          </CardContent>
        </Card>
      ) : (
        <Grid container spacing={3}>
          {matches.map((match) => (
            <Grid item xs={12} key={match.id}>
              <Card>
                <CardContent>
                  {/* Match Header */}
                  <Box display="flex" justifyContent="space-between" alignItems="center" mb={2}>
                    <Box display="flex" alignItems="center" gap={2}>
                      <Typography variant="h6">
                        {match.game_mode}
                      </Typography>
                      <Chip
                        label={match.game_type}
                        size="small"
                        variant="outlined"
                      />
                      <Box display="flex" alignItems="center" gap={1}>
                        <Timer fontSize="small" />
                        <Typography variant="body2">
                          {formatDuration(match.game_duration)}
                        </Typography>
                      </Box>
                    </Box>
                    <Box display="flex" alignItems="center" gap={1}>
                      <Typography variant="body2" color="textSecondary">
                        {formatDate(match.game_creation)}
                      </Typography>
                    </Box>
                  </Box>

                  <Divider sx={{ mb: 2 }} />

                  {/* Teams */}
                  <Grid container spacing={2}>
                    {/* Team 1 (Blue) */}
                    <Grid item xs={12} md={6}>
                      <Typography variant="subtitle1" gutterBottom>
                        Team 1 (Blue)
                      </Typography>
                      <TableContainer component={Paper} variant="outlined">
                        <Table size="small">
                          <TableHead>
                            <TableRow>
                              <TableCell>Player</TableCell>
                              <TableCell>Champion</TableCell>
                              <TableCell>Lane</TableCell>
                              <TableCell>K/D/A</TableCell>
                              <TableCell>CS</TableCell>
                            </TableRow>
                          </TableHead>
                          <TableBody>
                            {match.participants
                              .filter(p => p.team_id === 100)
                              .map((participant, index) => (
                                <TableRow key={index}>
                                  <TableCell>
                                    <Box display="flex" alignItems="center" gap={1}>
                                      <Typography variant="body2">
                                        {participant.summoner_name}
                                      </Typography>
                                      {tile.friends.some(f => f.puuid === participant.puuid) && (
                                        <Tooltip title="Friend">
                                          <Person fontSize="small" color="primary" />
                                        </Tooltip>
                                      )}
                                    </Box>
                                  </TableCell>
                                  <TableCell>
                                    <Typography variant="body2">
                                      {participant.champion_name}
                                    </Typography>
                                  </TableCell>
                                  <TableCell>
                                    <Box display="flex" alignItems="center" gap={0.5}>
                                      <span>{getLaneIcon(participant.lane)}</span>
                                      <Typography variant="body2">
                                        {participant.lane || 'Unknown'}
                                      </Typography>
                                    </Box>
                                  </TableCell>
                                  <TableCell>
                                    <Typography variant="body2">
                                      {participant.kills}/{participant.deaths}/{participant.assists}
                                    </Typography>
                                  </TableCell>
                                  <TableCell>
                                    <Typography variant="body2">
                                      {participant.cs}
                                    </Typography>
                                  </TableCell>
                                </TableRow>
                              ))}
                          </TableBody>
                        </Table>
                      </TableContainer>
                    </Grid>

                    {/* Team 2 (Red) */}
                    <Grid item xs={12} md={6}>
                      <Typography variant="subtitle1" gutterBottom>
                        Team 2 (Red)
                      </Typography>
                      <TableContainer component={Paper} variant="outlined">
                        <Table size="small">
                          <TableHead>
                            <TableRow>
                              <TableCell>Player</TableCell>
                              <TableCell>Champion</TableCell>
                              <TableCell>Lane</TableCell>
                              <TableCell>K/D/A</TableCell>
                              <TableCell>CS</TableCell>
                            </TableRow>
                          </TableHead>
                          <TableBody>
                            {match.participants
                              .filter(p => p.team_id === 200)
                              .map((participant, index) => (
                                <TableRow key={index}>
                                  <TableCell>
                                    <Box display="flex" alignItems="center" gap={1}>
                                      <Typography variant="body2">
                                        {participant.summoner_name}
                                      </Typography>
                                      {tile.friends.some(f => f.puuid === participant.puuid) && (
                                        <Tooltip title="Friend">
                                          <Person fontSize="small" color="primary" />
                                        </Tooltip>
                                      )}
                                    </Box>
                                  </TableCell>
                                  <TableCell>
                                    <Typography variant="body2">
                                      {participant.champion_name}
                                    </Typography>
                                  </TableCell>
                                  <TableCell>
                                    <Box display="flex" alignItems="center" gap={0.5}>
                                      <span>{getLaneIcon(participant.lane)}</span>
                                      <Typography variant="body2">
                                        {participant.lane || 'Unknown'}
                                      </Typography>
                                    </Box>
                                  </TableCell>
                                  <TableCell>
                                    <Typography variant="body2">
                                      {participant.kills}/{participant.deaths}/{participant.assists}
                                    </Typography>
                                  </TableCell>
                                  <TableCell>
                                    <Typography variant="body2">
                                      {participant.cs}
                                    </Typography>
                                  </TableCell>
                                </TableRow>
                              ))}
                          </TableBody>
                        </Table>
                      </TableContainer>
                    </Grid>
                  </Grid>

                  {/* Match Result */}
                  <Box display="flex" justifyContent="center" mt={2}>
                    {match.participants.some(p => 
                      tile.friends.some(f => f.puuid === p.puuid) && p.win
                    ) ? (
                      <Chip
                        icon={<CheckCircle />}
                        label="VICTORY"
                        color="success"
                        variant="filled"
                        size="medium"
                      />
                    ) : (
                      <Chip
                        icon={<Cancel />}
                        label="DEFEAT"
                        color="error"
                        variant="filled"
                        size="medium"
                      />
                    )}
                  </Box>
                </CardContent>
              </Card>
            </Grid>
          ))}
        </Grid>
      )}
    </Box>
  );
};

export default TileMatches; 