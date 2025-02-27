import React, { useState, useEffect } from 'react';
import { 
  Box, 
  Typography, 
  Grid,
  CircularProgress,
  Fab,
  Tooltip,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  Button
} from '@mui/material';
import AddIcon from '@mui/icons-material/Add';
import FeatureGroupCard from '../components/FeatureGroupCard';
import CreateFeatureGroupDialog from '../components/CreateFeatureGroupDialog';

const API_URL = 'http://localhost:8000/api/v1';

const FeatureGroups = () => {
  const [groups, setGroups] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [createDialogOpen, setCreateDialogOpen] = useState(false);
  const [editingGroup, setEditingGroup] = useState(null);
  const [deleteDialogOpen, setDeleteDialogOpen] = useState(false);
  const [groupToDelete, setGroupToDelete] = useState(null);

  useEffect(() => {
    fetchGroups();
  }, []);

  const fetchGroups = async () => {
    try {
      setLoading(true);
      setError(null);
      const response = await fetch(`${API_URL}/feature-groups`);
      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }
      const data = await response.json();
      setGroups(Array.isArray(data) ? data : []);
    } catch (error) {
      console.error('Error fetching groups:', error);
      setError(error.message);
    } finally {
      setLoading(false);
    }
  };

  const handleCreateGroup = async (groupData) => {
    try {
      const response = await fetch(`${API_URL}/feature-groups`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(groupData),
      });
      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }
      const newGroup = await response.json();
      setGroups(prev => [...prev, newGroup]);
      setCreateDialogOpen(false);
    } catch (error) {
      console.error('Error creating group:', error);
      setError(error.message);
    }
  };

  const handleEditGroup = async (groupData) => {
    try {
      const response = await fetch(`${API_URL}/feature-groups/${editingGroup.id}`, {
        method: 'PUT',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(groupData),
      });
      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }
      const updatedGroup = await response.json();
      setGroups(prev => prev.map(g => g.id === updatedGroup.id ? updatedGroup : g));
      setEditingGroup(null);
    } catch (error) {
      console.error('Error updating group:', error);
      setError(error.message);
    }
  };

  const handleDeleteGroup = async () => {
    if (!groupToDelete) return;
    try {
      const response = await fetch(`${API_URL}/feature-groups/${groupToDelete.id}`, {
        method: 'DELETE',
      });
      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }
      setGroups(prev => prev.filter(g => g.id !== groupToDelete.id));
      setGroupToDelete(null);
      setDeleteDialogOpen(false);
    } catch (error) {
      console.error('Error deleting group:', error);
      setError(error.message);
    }
  };

  const handleViewFeatures = (group) => {
    // Implementar navegação para a página de features do grupo
    console.log('View features for group:', group);
  };

  if (loading) {
    return (
      <Box display="flex" justifyContent="center" alignItems="center" minHeight="200px">
        <CircularProgress />
      </Box>
    );
  }

  return (
    <Box p={3}>
      <Box display="flex" justifyContent="space-between" alignItems="center" mb={3}>
        <Typography variant="h4">
          Feature Groups ({groups.length})
        </Typography>
        <Tooltip title="Create Feature Group">
          <Fab
            color="primary"
            size="medium"
            onClick={() => setCreateDialogOpen(true)}
          >
            <AddIcon />
          </Fab>
        </Tooltip>
      </Box>

      {error && (
        <Typography color="error" mb={3}>
          Error: {error}
        </Typography>
      )}

      <Grid container spacing={3}>
        {groups.map((group) => (
          <Grid item xs={12} sm={6} md={4} key={group.id}>
            <FeatureGroupCard
              group={group}
              onEdit={(group) => {
                setEditingGroup(group);
                setCreateDialogOpen(true);
              }}
              onDelete={(group) => {
                setGroupToDelete(group);
                setDeleteDialogOpen(true);
              }}
              onViewFeatures={handleViewFeatures}
            />
          </Grid>
        ))}
        {groups.length === 0 && (
          <Grid item xs={12}>
            <Typography variant="body1" color="textSecondary" align="center">
              No feature groups found. Create your first feature group!
            </Typography>
          </Grid>
        )}
      </Grid>

      <CreateFeatureGroupDialog
        open={createDialogOpen}
        onClose={() => {
          setCreateDialogOpen(false);
          setEditingGroup(null);
        }}
        onSubmit={editingGroup ? handleEditGroup : handleCreateGroup}
        initialData={editingGroup}
      />

      <Dialog open={deleteDialogOpen} onClose={() => setDeleteDialogOpen(false)}>
        <DialogTitle>Delete Feature Group</DialogTitle>
        <DialogContent>
          Are you sure you want to delete the feature group "{groupToDelete?.name}"?
          This action cannot be undone.
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setDeleteDialogOpen(false)}>Cancel</Button>
          <Button onClick={handleDeleteGroup} color="error">
            Delete
          </Button>
        </DialogActions>
      </Dialog>
    </Box>
  );
};

export default FeatureGroups;
