import React, { useState, useEffect } from 'react';
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
} from '@mui/material';
import { Delete, Add, Refresh, Edit } from '@mui/icons-material';
import { Friend } from '../types';
import { friendService } from '../services/friendService';

const Friends: React.FC = () => {
  const [friends, setFriends] = useState<Friend[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [dialogOpen, setDialogOpen] = useState(false);
  const [editDialogOpen, setEditDialogOpen] = useState(false);
  const [editingFriend, setEditingFriend] = useState<Friend | null>(null);
  const [newFriend, setNewFriend] = useState({ 
    riotId: '', 
    region: 'na1', 
    matchCount: 50,
    dateFrom: '',
    dateTo: ''
  });
  const [submitting, setSubmitting] = useState(false);

  useEffect(() => {
    loadFriends();
  }, []);

  const loadFriends = async () => {
    try {
      setLoading(true);
      const data = await friendService.getFriends();
      setFriends(data);
    } catch (error: any) {
      setError('Failed to load friends');
    } finally {
      setLoading(false);
    }
  };

  const handleAddFriend = async () => {
    if (!newFriend.riotId.trim()) return;

    try {
      setSubmitting(true);
      const friend = await friendService.addFriend(
        newFriend.riotId, 
        newFriend.region, 
        newFriend.matchCount,
        newFriend.dateFrom || undefined,
        newFriend.dateTo || undefined
      );
      setFriends([...friends, friend]);
      setNewFriend({ riotId: '', region: 'na1', matchCount: 50, dateFrom: '', dateTo: '' });
      setDialogOpen(false);
    } catch (error: any) {
      setError(error.response?.data?.error || 'Failed to add friend');
    } finally {
      setSubmitting(false);
    }
  };

  const handleDeleteFriend = async (friendId: number) => {
    try {
      await friendService.deleteFriend(friendId);
      setFriends(friends.filter(f => f.id !== friendId));
    } catch (error: any) {
      setError('Failed to delete friend');
    }
  };

  const handleRefreshMatches = async (puuid: string) => {
    try {
      setSubmitting(true);
      await friendService.refreshMatches(puuid);
      setError(''); // Clear any previous errors
    } catch (error: any) {
      setError('Failed to refresh matches');
    } finally {
      setSubmitting(false);
    }
  };

  const handleEditFriend = (friend: Friend) => {
    setEditingFriend(friend);
    setEditDialogOpen(true);
  };

  const handleUpdateFriend = async () => {
    if (!editingFriend) return;

    try {
      setSubmitting(true);
      const updatedFriend = await friendService.updateFriend(
        editingFriend.id, 
        editingFriend.match_count,
        editingFriend.date_from || undefined,
        editingFriend.date_to || undefined
      );
      setFriends(friends.map(f => f.id === editingFriend.id ? updatedFriend : f));
      setEditDialogOpen(false);
      setEditingFriend(null);
    } catch (error: any) {
      setError(error.response?.data?.error || 'Failed to update friend');
    } finally {
      setSubmitting(false);
    }
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
          Friends Management
        </Typography>
        <Button
          variant="contained"
          startIcon={<Add />}
          onClick={() => setDialogOpen(true)}
        >
          Add Friend
        </Button>
      </Box>

      {error && (
        <Alert severity="error" sx={{ mb: 2 }} onClose={() => setError('')}>
          {error}
        </Alert>
      )}

      <Grid container spacing={3}>
        {friends.map((friend) => (
          <Grid item xs={12} sm={6} md={4} key={friend.id}>
            <Card>
              <CardContent>
                <Box display="flex" justifyContent="space-between" alignItems="flex-start">
                  <Box flex={1}>
                    <Typography variant="h6" gutterBottom>
                      {friend.summoner_name}
                    </Typography>
                    <Typography variant="body2" color="textSecondary" gutterBottom>
                      {friend.riot_id}
                    </Typography>
                    <Box display="flex" gap={1} mt={1}>
                      <Chip label={friend.region.toUpperCase()} size="small" />
                      <Chip label={`${friend.total_matches_fetched} matches`} size="small" color="primary" />
                      <Chip label={`Added ${new Date(friend.created_at).toLocaleDateString()}`} size="small" variant="outlined" />
                    </Box>
                    {(friend.date_from || friend.date_to) && (
                      <Box display="flex" gap={1} mt={1}>
                        <Chip 
                          label={`Date range: ${friend.date_from || 'Any'} to ${friend.date_to || 'Any'}`} 
                          size="small" 
                          variant="outlined" 
                          color="secondary"
                        />
                      </Box>
                    )}
                  </Box>
                  <Box>
                    <IconButton
                      color="primary"
                      onClick={() => handleEditFriend(friend)}
                      size="small"
                      title="Edit friend"
                    >
                      <Edit />
                    </IconButton>
                    <IconButton
                      color="primary"
                      onClick={() => handleRefreshMatches(friend.puuid)}
                      size="small"
                      title="Refresh matches"
                    >
                      <Refresh />
                    </IconButton>
                    <IconButton
                      color="error"
                      onClick={() => handleDeleteFriend(friend.id)}
                      size="small"
                    >
                      <Delete />
                    </IconButton>
                  </Box>
                </Box>
              </CardContent>
            </Card>
          </Grid>
        ))}
      </Grid>

      {friends.length === 0 && (
        <Card>
          <CardContent sx={{ textAlign: 'center', py: 4 }}>
            <Typography variant="h6" color="textSecondary" gutterBottom>
              No Friends Added Yet
            </Typography>
            <Typography variant="body2" color="textSecondary" sx={{ mb: 2 }}>
              Add your League of Legends friends to start tracking win rates together.
            </Typography>
            <Button variant="contained" onClick={() => setDialogOpen(true)}>
              Add Your First Friend
            </Button>
          </CardContent>
        </Card>
      )}

      {/* Add Friend Dialog */}
      <Dialog open={dialogOpen} onClose={() => setDialogOpen(false)} maxWidth="sm" fullWidth>
        <DialogTitle>Add New Friend</DialogTitle>
        <DialogContent>
          <TextField
            autoFocus
            margin="dense"
            label="Riot ID"
            fullWidth
            variant="outlined"
            placeholder="SummonerName#TAG"
            value={newFriend.riotId}
            onChange={(e) => setNewFriend({ ...newFriend, riotId: e.target.value })}
            sx={{ mb: 2 }}
          />
          <FormControl fullWidth sx={{ mb: 2 }}>
            <InputLabel>Region</InputLabel>
            <Select
              value={newFriend.region}
              label="Region"
              onChange={(e) => setNewFriend({ ...newFriend, region: e.target.value })}
            >
              <MenuItem value="na1">North America</MenuItem>
              <MenuItem value="euw1">Europe West</MenuItem>
              <MenuItem value="kr">Korea</MenuItem>
            </Select>
          </FormControl>
          <TextField
            margin="dense"
            label="Number of Matches to Fetch"
            type="number"
            fullWidth
            variant="outlined"
            value={newFriend.matchCount}
            onChange={(e) => setNewFriend({ ...newFriend, matchCount: parseInt(e.target.value) || 50 })}
            inputProps={{ min: 1, max: 100 }}
            helperText="How many recent matches to fetch (1-100)"
            sx={{ mb: 2 }}
          />
          <TextField
            margin="dense"
            label="Date From (YYYY-MM-DD)"
            fullWidth
            variant="outlined"
            placeholder="2024-01-01"
            value={newFriend.dateFrom}
            onChange={(e) => setNewFriend({ ...newFriend, dateFrom: e.target.value })}
            helperText="Optional: Start date for match query (leave empty for recent matches)"
            sx={{ mb: 2 }}
          />
          <TextField
            margin="dense"
            label="Date To (YYYY-MM-DD)"
            fullWidth
            variant="outlined"
            placeholder="2024-12-31"
            value={newFriend.dateTo}
            onChange={(e) => setNewFriend({ ...newFriend, dateTo: e.target.value })}
            helperText="Optional: End date for match query (leave empty for recent matches)"
          />
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setDialogOpen(false)}>Cancel</Button>
          <Button
            onClick={handleAddFriend}
            variant="contained"
            disabled={!newFriend.riotId.trim() || submitting}
          >
            {submitting ? 'Adding...' : 'Add Friend'}
          </Button>
        </DialogActions>
      </Dialog>

      {/* Edit Friend Dialog */}
      <Dialog open={editDialogOpen} onClose={() => setEditDialogOpen(false)} maxWidth="sm" fullWidth>
        <DialogTitle>Edit Friend</DialogTitle>
        <DialogContent>
          {editingFriend && (
            <>
              <TextField
                margin="dense"
                label="Summoner Name"
                fullWidth
                variant="outlined"
                value={editingFriend.summoner_name}
                disabled
                sx={{ mb: 2 }}
              />
              <TextField
                margin="dense"
                label="Riot ID"
                fullWidth
                variant="outlined"
                value={editingFriend.riot_id}
                disabled
                sx={{ mb: 2 }}
              />
              <TextField
                margin="dense"
                label="Number of Matches to Fetch"
                type="number"
                fullWidth
                variant="outlined"
                value={editingFriend.match_count}
                onChange={(e) => setEditingFriend({
                  ...editingFriend,
                  match_count: parseInt(e.target.value) || 50
                })}
                inputProps={{ min: 1, max: 100 }}
                helperText="How many recent matches to fetch (1-100). This will refresh match data."
                sx={{ mb: 2 }}
              />
              <TextField
                margin="dense"
                label="Date From (YYYY-MM-DD)"
                fullWidth
                variant="outlined"
                placeholder="2024-01-01"
                value={editingFriend.date_from || ''}
                onChange={(e) => setEditingFriend({
                  ...editingFriend,
                  date_from: e.target.value || undefined
                })}
                helperText="Optional: Start date for match query (leave empty for recent matches)"
                sx={{ mb: 2 }}
              />
              <TextField
                margin="dense"
                label="Date To (YYYY-MM-DD)"
                fullWidth
                variant="outlined"
                placeholder="2024-12-31"
                value={editingFriend.date_to || ''}
                onChange={(e) => setEditingFriend({
                  ...editingFriend,
                  date_to: e.target.value || undefined
                })}
                helperText="Optional: End date for match query (leave empty for recent matches)"
              />
            </>
          )}
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setEditDialogOpen(false)}>Cancel</Button>
          <Button
            onClick={handleUpdateFriend}
            variant="contained"
            disabled={!editingFriend || submitting}
          >
            {submitting ? 'Updating...' : 'Update Friend'}
          </Button>
        </DialogActions>
      </Dialog>
    </Box>
  );
};

export default Friends; 