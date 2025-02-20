import React, { useState, useEffect } from 'react';
import { 
  Box, 
  Button, 
  Card, 
  CardContent, 
  Typography, 
  TextField,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions
} from '@mui/material';

const API_URL = 'http://localhost:8000/api/v1';

const FeatureGroups = () => {
  const [groups, setGroups] = useState([]);
  const [open, setOpen] = useState(false);
  const [newGroup, setNewGroup] = useState({
    name: '',
    description: '',
    entity_type: '',
    tags: [],
    frequency: 'daily'
  });

  useEffect(() => {
    fetchGroups();
  }, []);

  const fetchGroups = async () => {
    try {
      const response = await fetch(`${API_URL}/feature-groups`);
      const data = await response.json();
      setGroups(data);
    } catch (error) {
      console.error('Error fetching groups:', error);
    }
  };

  const handleCreateGroup = async () => {
    try {
      const response = await fetch(`${API_URL}/feature-groups`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          ...newGroup,
          tags: newGroup.tags.split(',').map(tag => tag.trim())
        }),
      });
      const data = await response.json();
      setGroups([...groups, data]);
      setOpen(false);
      setNewGroup({
        name: '',
        description: '',
        entity_type: '',
        tags: [],
        frequency: 'daily'
      });
    } catch (error) {
      console.error('Error creating group:', error);
    }
  };

  return (
    <Box sx={{ p: 3 }}>
      <Box sx={{ display: 'flex', justifyContent: 'space-between', mb: 3 }}>
        <Typography variant="h4">Feature Groups</Typography>
        <Button variant="contained" color="primary" onClick={() => setOpen(true)}>
          Create Group
        </Button>
      </Box>

      <Box sx={{ display: 'grid', gap: 2, gridTemplateColumns: 'repeat(auto-fill, minmax(300px, 1fr))' }}>
        {groups.map((group) => (
          <Card key={group.id} sx={{ height: '100%' }}>
            <CardContent>
              <Typography variant="h6">{group.name}</Typography>
              <Typography color="textSecondary">{group.description}</Typography>
              <Typography variant="body2">Entity Type: {group.entity_type}</Typography>
              <Typography variant="body2">Frequency: {group.frequency}</Typography>
              <Box sx={{ mt: 1 }}>
                {group.tags.map((tag) => (
                  <Typography
                    key={tag}
                    component="span"
                    sx={{
                      bgcolor: 'primary.light',
                      color: 'white',
                      px: 1,
                      py: 0.5,
                      borderRadius: 1,
                      mr: 1,
                      display: 'inline-block',
                      mb: 1,
                    }}
                  >
                    {tag}
                  </Typography>
                ))}
              </Box>
            </CardContent>
          </Card>
        ))}
      </Box>

      <Dialog open={open} onClose={() => setOpen(false)}>
        <DialogTitle>Create Feature Group</DialogTitle>
        <DialogContent>
          <TextField
            autoFocus
            margin="dense"
            label="Name"
            fullWidth
            value={newGroup.name}
            onChange={(e) => setNewGroup({ ...newGroup, name: e.target.value })}
          />
          <TextField
            margin="dense"
            label="Description"
            fullWidth
            value={newGroup.description}
            onChange={(e) => setNewGroup({ ...newGroup, description: e.target.value })}
          />
          <TextField
            margin="dense"
            label="Entity Type"
            fullWidth
            value={newGroup.entity_type}
            onChange={(e) => setNewGroup({ ...newGroup, entity_type: e.target.value })}
          />
          <TextField
            margin="dense"
            label="Tags (comma-separated)"
            fullWidth
            value={newGroup.tags}
            onChange={(e) => setNewGroup({ ...newGroup, tags: e.target.value })}
          />
          <TextField
            margin="dense"
            label="Frequency"
            fullWidth
            value={newGroup.frequency}
            onChange={(e) => setNewGroup({ ...newGroup, frequency: e.target.value })}
          />
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setOpen(false)}>Cancel</Button>
          <Button onClick={handleCreateGroup} color="primary">
            Create
          </Button>
        </DialogActions>
      </Dialog>
    </Box>
  );
};

export default FeatureGroups;
