import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import {
  Box,
  Typography,
  Button,
  TextField,
  Card,
  CardContent,
  Grid,
  IconButton,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  FormControl,
  InputLabel,
  Select,
  MenuItem,
  Alert,
  CircularProgress,
  Chip,
  LinearProgress,
} from '@mui/material';
import { Delete, Add, Edit, Visibility } from '@mui/icons-material';
import { AnalysisTile, Friend, CreateTileData } from '../types';
import { tileService } from '../services/tileService';
import { friendService } from '../services/friendService';

const Tiles: React.FC = () => {
  const navigate = useNavigate();
  const [tiles, setTiles] = useState<AnalysisTile[]>([]);
  const [friends, setFriends] = useState<Friend[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [dialogOpen, setDialogOpen] = useState(false);
  const [editingTile, setEditingTile] = useState<AnalysisTile | null>(null);
  const [newTile, setNewTile] = useState<CreateTileData>({
    name: '',
    friend_ids: [],
    match_filter: 'inclusive',
    date_from: '',
    date_to: '',
    max_matches_per_tile: 50,
  });
  const [submitting, setSubmitting] = useState(false);

  useEffect(() => {
    loadData();
  }, []);

  const loadData = async () => {
    try {
      setLoading(true);
      const [tilesData, friendsData] = await Promise.all([
        tileService.getTiles(),
        friendService.getFriends(),
      ]);
      setTiles(tilesData);
      setFriends(friendsData);
    } catch (error: any) {
      setError('Failed to load data');
    } finally {
      setLoading(false);
    }
  };

  const handleCreateTile = async () => {
    if (!newTile.name.trim() || newTile.friend_ids.length === 0) return;

    console.log('Tiles: About to create tile with data:', newTile);
    console.log('Tiles: Name:', newTile.name);
    console.log('Tiles: Friend IDs:', newTile.friend_ids);
    console.log('Tiles: Match filter:', newTile.match_filter);

    try {
      setSubmitting(true);
      const tile = await tileService.createTile(newTile);
      setTiles([...tiles, tile]);
      resetForm();
      setDialogOpen(false);
    } catch (error: any) {
      console.error('Tiles: Error in handleCreateTile:', error);
      console.error('Tiles: Error response:', error.response?.data);
      setError(error.response?.data?.error || 'Failed to create tile');
    } finally {
      setSubmitting(false);
    }
  };

  const handleUpdateTile = async () => {
    if (!editingTile || !newTile.name.trim() || newTile.friend_ids.length === 0) return;

    try {
      setSubmitting(true);
      const updatedTile = await tileService.updateTile(editingTile.id, newTile);
      setTiles(tiles.map(t => t.id === editingTile.id ? updatedTile : t));
      resetForm();
      setDialogOpen(false);
    } catch (error: any) {
      setError(error.response?.data?.error || 'Failed to update tile');
    } finally {
      setSubmitting(false);
    }
  };

  const handleDeleteTile = async (tileId: number) => {
    try {
      await tileService.deleteTile(tileId);
      setTiles(tiles.filter(t => t.id !== tileId));
    } catch (error: any) {
      setError('Failed to delete tile');
    }
  };

  const handleEditTile = (tile: AnalysisTile) => {
    setEditingTile(tile);
    setNewTile({
      name: tile.name,
      friend_ids: tile.friends.map(f => f.id),
      match_filter: tile.match_filter,
      date_from: tile.date_from,
      date_to: tile.date_to,
      max_matches_per_tile: tile.max_matches_per_tile,
    });
    setDialogOpen(true);
  };

  const resetForm = () => {
    setNewTile({
      name: '',
      friend_ids: [],
      match_filter: 'inclusive',
      date_from: '',
      date_to: '',
      max_matches_per_tile: 50,
    });
    setEditingTile(null);
  };

  const handleDialogClose = () => {
    setDialogOpen(false);
    resetForm();
  };

  const getWinRateColor = (winRate: number) => {
    if (winRate >= 60) return 'success';
    if (winRate >= 50) return 'warning';
    return 'error';
  };

  if (loading) {
    return (
      <Box display="flex" justifyContent="center" alignItems="center" minHeight="400px">
        <CircularProgress />
      </Box>
    );
  }

  return (
    <Box>
      <Box display="flex" justifyContent="space-between" alignItems="center" mb={3}>
        <Typography variant="h4">
          Analysis Tiles
        </Typography>
        <Button
          variant="contained"
          startIcon={<Add />}
          onClick={() => setDialogOpen(true)}
          disabled={friends.length === 0}
        >
          Create Tile
        </Button>
      </Box>

      {error && (
        <Alert severity="error" sx={{ mb: 2 }} onClose={() => setError('')}>
          {error}
        </Alert>
      )}

      {friends.length === 0 && (
        <Alert severity="info" sx={{ mb: 2 }}>
          You need to add friends first before creating analysis tiles.
        </Alert>
      )}

      <Grid container spacing={3}>
        {tiles.map((tile) => (
          <Grid item xs={12} md={6} lg={4} key={tile.id}>
            <Card 
              sx={{ 
                cursor: 'pointer',
                '&:hover': {
                  boxShadow: 6,
                  transform: 'translateY(-2px)',
                  transition: 'all 0.2s ease-in-out',
                }
              }}
              onClick={() => navigate(`/tiles/${tile.id}`)}
            >
              <CardContent>
                <Box display="flex" justifyContent="space-between" alignItems="flex-start" mb={2}>
                  <Typography variant="h6" gutterBottom>
                    {tile.name}
                  </Typography>
                  <Box>
                    <IconButton
                      size="small"
                      onClick={(e) => {
                        e.stopPropagation();
                        navigate(`/tiles/${tile.id}`);
                      }}
                      title="View matches"
                      sx={{ color: 'primary.main' }}
                    >
                      <Visibility />
                    </IconButton>
                    <IconButton
                      size="small"
                      onClick={(e) => {
                        e.stopPropagation();
                        handleEditTile(tile);
                      }}
                    >
                      <Edit />
                    </IconButton>
                    <IconButton
                      color="error"
                      size="small"
                      onClick={(e) => {
                        e.stopPropagation();
                        handleDeleteTile(tile.id);
                      }}
                    >
                      <Delete />
                    </IconButton>
                  </Box>
                </Box>

                <Box mb={2}>
                  <Typography variant="h4" color={`${getWinRateColor(tile.win_rate)}.main`}>
                    {tile.win_rate.toFixed(1)}%
                  </Typography>
                  <Typography variant="body2" color="textSecondary">
                    {tile.wins}W - {tile.losses}L ({tile.total_matches} matches)
                  </Typography>
                </Box>

                <LinearProgress
                  variant="determinate"
                  value={tile.win_rate}
                  color={getWinRateColor(tile.win_rate) as any}
                  sx={{ mb: 2 }}
                />

                <Box mb={2}>
                  <Typography variant="body2" color="textSecondary" gutterBottom>
                    Friends:
                  </Typography>
                  <Box display="flex" flexWrap="wrap" gap={0.5}>
                    {tile.friends.map((friend) => (
                      <Chip
                        key={friend.id}
                        label={friend.summoner_name}
                        size="small"
                        variant="outlined"
                      />
                    ))}
                  </Box>
                </Box>

                <Box display="flex" gap={1}>
                  <Chip
                    label={tile.match_filter === 'exclusive' ? 'Exclusive' : 'Inclusive'}
                    size="small"
                    color="primary"
                    variant="outlined"
                  />
                  {(tile.date_from || tile.date_to) && (
                    <Chip
                      label={`Date: ${tile.date_from || 'Any'} to ${tile.date_to || 'Any'}`}
                      size="small"
                      color="secondary"
                      variant="outlined"
                    />
                  )}
                  <Chip
                    label={`Max: ${tile.max_matches_per_tile}`}
                    size="small"
                    color="info"
                    variant="outlined"
                  />
                </Box>
              </CardContent>
            </Card>
          </Grid>
        ))}
      </Grid>

      {tiles.length === 0 && friends.length > 0 && (
        <Card>
          <CardContent sx={{ textAlign: 'center', py: 4 }}>
            <Typography variant="h6" color="textSecondary" gutterBottom>
              No Analysis Tiles Yet
            </Typography>
            <Typography variant="body2" color="textSecondary" sx={{ mb: 2 }}>
              Create your first analysis tile to start tracking win rates with your friends.
            </Typography>
            <Button variant="contained" onClick={() => setDialogOpen(true)}>
              Create First Tile
            </Button>
          </CardContent>
        </Card>
      )}

      {/* Create/Edit Tile Dialog */}
      <Dialog open={dialogOpen} onClose={handleDialogClose} maxWidth="sm" fullWidth>
        <DialogTitle>
          {editingTile ? 'Edit Analysis Tile' : 'Create New Analysis Tile'}
        </DialogTitle>
        <DialogContent>
          <TextField
            autoFocus
            margin="dense"
            label="Tile Name"
            fullWidth
            variant="outlined"
            value={newTile.name}
            onChange={(e) => setNewTile({ ...newTile, name: e.target.value })}
            sx={{ mb: 2 }}
          />
          
          <FormControl fullWidth sx={{ mb: 2 }}>
            <InputLabel>Select Friends</InputLabel>
            <Select
              multiple
              value={newTile.friend_ids}
              label="Select Friends"
              onChange={(e) => setNewTile({ ...newTile, friend_ids: e.target.value as number[] })}
            >
              {friends.map((friend) => (
                <MenuItem key={friend.id} value={friend.id}>
                  {friend.summoner_name} ({friend.riot_id})
                </MenuItem>
              ))}
            </Select>
          </FormControl>

          <FormControl fullWidth sx={{ mb: 2 }}>
            <InputLabel>Match Filter</InputLabel>
            <Select
              value={newTile.match_filter}
              label="Match Filter"
              onChange={(e) => setNewTile({ ...newTile, match_filter: e.target.value as 'exclusive' | 'inclusive' })}
            >
              <MenuItem value="inclusive">Inclusive - Include matches with these players plus others</MenuItem>
              <MenuItem value="exclusive">Exclusive - Only include matches with these friends + random players (no other friends)</MenuItem>
            </Select>
          </FormControl>

          <TextField
            margin="dense"
            label="Date From (YYYY-MM-DD)"
            fullWidth
            variant="outlined"
            placeholder="2024-01-01"
            value={newTile.date_from}
            onChange={(e) => setNewTile({ ...newTile, date_from: e.target.value })}
            helperText="Optional: Start date for match filtering (leave empty for most recent matches)"
            sx={{ mb: 2 }}
          />

          <TextField
            margin="dense"
            label="Date To (YYYY-MM-DD)"
            fullWidth
            variant="outlined"
            placeholder="2024-12-31"
            value={newTile.date_to}
            onChange={(e) => setNewTile({ ...newTile, date_to: e.target.value })}
            helperText="Optional: End date for match filtering (leave empty for most recent matches)"
            sx={{ mb: 2 }}
          />

          <TextField
            margin="dense"
            label="Max Matches per Tile"
            type="number"
            fullWidth
            variant="outlined"
            value={newTile.max_matches_per_tile}
            onChange={(e) => setNewTile({ ...newTile, max_matches_per_tile: parseInt(e.target.value) || 50 })}
            inputProps={{ min: 1, max: 200 }}
            helperText="Maximum number of matches to show in this tile (1-200)"
          />
        </DialogContent>
        <DialogActions>
          <Button onClick={handleDialogClose}>Cancel</Button>
          <Button
            onClick={editingTile ? handleUpdateTile : handleCreateTile}
            variant="contained"
            disabled={!newTile.name.trim() || newTile.friend_ids.length === 0 || submitting}
          >
            {submitting ? 'Saving...' : (editingTile ? 'Update Tile' : 'Create Tile')}
          </Button>
        </DialogActions>
      </Dialog>
    </Box>
  );
};

export default Tiles; 