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
  DialogActions,
  Select,
  MenuItem,
  FormControl,
  InputLabel,
} from '@mui/material';

const API_URL = 'http://backend:8000/api/v1';

const Features = () => {
  const [features, setFeatures] = useState([]);
  const [groups, setGroups] = useState([]);
  const [open, setOpen] = useState(false);
  const [valueDialog, setValueDialog] = useState(false);
  const [selectedFeature, setSelectedFeature] = useState(null);
  const [newFeature, setNewFeature] = useState({
    name: '',
    description: '',
    data_type: 'float',
    entity_id: '',
    feature_group_id: '',
    tags: '',
    metadata: {}
  });
  const [newValue, setNewValue] = useState({
    value: '',
    timestamp: new Date().toISOString()
  });

  useEffect(() => {
    fetchFeatures();
    fetchGroups();
  }, []);

  const fetchFeatures = async () => {
    try {
      const response = await fetch(`${API_URL}/features`);
      const data = await response.json();
      setFeatures(data);
    } catch (error) {
      console.error('Error fetching features:', error);
    }
  };

  const fetchGroups = async () => {
    try {
      const response = await fetch(`${API_URL}/feature-groups`);
      const data = await response.json();
      setGroups(data);
    } catch (error) {
      console.error('Error fetching groups:', error);
    }
  };

  const handleCreateFeature = async () => {
    try {
      const response = await fetch(`${API_URL}/features`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          ...newFeature,
          tags: newFeature.tags.split(',').map(tag => tag.trim())
        }),
      });
      const data = await response.json();
      setFeatures([...features, data]);
      setOpen(false);
      setNewFeature({
        name: '',
        description: '',
        data_type: 'float',
        entity_id: '',
        feature_group_id: '',
        tags: '',
        metadata: {}
      });
    } catch (error) {
      console.error('Error creating feature:', error);
    }
  };

  const handleAddValue = async () => {
    try {
      await fetch(`${API_URL}/features/${selectedFeature.id}/values`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(newValue),
      });
      setValueDialog(false);
      setNewValue({
        value: '',
        timestamp: new Date().toISOString()
      });
      fetchFeatures();
    } catch (error) {
      console.error('Error adding value:', error);
    }
  };

  return (
    <Box sx={{ p: 3 }}>
      <Box sx={{ display: 'flex', justifyContent: 'space-between', mb: 3 }}>
        <Typography variant="h4">Features</Typography>
        <Button variant="contained" color="primary" onClick={() => setOpen(true)}>
          Create Feature
        </Button>
      </Box>

      <Box sx={{ display: 'grid', gap: 2, gridTemplateColumns: 'repeat(auto-fill, minmax(300px, 1fr))' }}>
        {features.map((feature) => (
          <Card key={feature.id} sx={{ height: '100%' }}>
            <CardContent>
              <Typography variant="h6">{feature.name}</Typography>
              <Typography color="textSecondary">{feature.description}</Typography>
              <Typography variant="body2">Type: {feature.data_type}</Typography>
              <Typography variant="body2">Entity ID: {feature.entity_id}</Typography>
              <Box sx={{ mt: 1, mb: 2 }}>
                {feature.tags.map((tag) => (
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
              <Button
                variant="outlined"
                size="small"
                onClick={() => {
                  setSelectedFeature(feature);
                  setValueDialog(true);
                }}
              >
                Add Value
              </Button>
            </CardContent>
          </Card>
        ))}
      </Box>

      <Dialog open={open} onClose={() => setOpen(false)}>
        <DialogTitle>Create Feature</DialogTitle>
        <DialogContent>
          <TextField
            autoFocus
            margin="dense"
            label="Name"
            fullWidth
            value={newFeature.name}
            onChange={(e) => setNewFeature({ ...newFeature, name: e.target.value })}
          />
          <TextField
            margin="dense"
            label="Description"
            fullWidth
            value={newFeature.description}
            onChange={(e) => setNewFeature({ ...newFeature, description: e.target.value })}
          />
          <TextField
            margin="dense"
            label="Entity ID"
            fullWidth
            value={newFeature.entity_id}
            onChange={(e) => setNewFeature({ ...newFeature, entity_id: e.target.value })}
          />
          <FormControl fullWidth margin="dense">
            <InputLabel>Feature Group</InputLabel>
            <Select
              value={newFeature.feature_group_id}
              onChange={(e) => setNewFeature({ ...newFeature, feature_group_id: e.target.value })}
            >
              {groups.map((group) => (
                <MenuItem key={group.id} value={group.id}>
                  {group.name}
                </MenuItem>
              ))}
            </Select>
          </FormControl>
          <TextField
            margin="dense"
            label="Tags (comma-separated)"
            fullWidth
            value={newFeature.tags}
            onChange={(e) => setNewFeature({ ...newFeature, tags: e.target.value })}
          />
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setOpen(false)}>Cancel</Button>
          <Button onClick={handleCreateFeature} color="primary">
            Create
          </Button>
        </DialogActions>
      </Dialog>

      <Dialog open={valueDialog} onClose={() => setValueDialog(false)}>
        <DialogTitle>Add Value</DialogTitle>
        <DialogContent>
          <TextField
            autoFocus
            margin="dense"
            label="Value"
            type="number"
            fullWidth
            value={newValue.value}
            onChange={(e) => setNewValue({ ...newValue, value: parseFloat(e.target.value) })}
          />
          <TextField
            margin="dense"
            label="Timestamp"
            type="datetime-local"
            fullWidth
            value={newValue.timestamp.slice(0, 16)}
            onChange={(e) => setNewValue({ ...newValue, timestamp: new Date(e.target.value).toISOString() })}
            InputLabelProps={{
              shrink: true,
            }}
          />
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setValueDialog(false)}>Cancel</Button>
          <Button onClick={handleAddValue} color="primary">
            Add
          </Button>
        </DialogActions>
      </Dialog>
    </Box>
  );
};

export default Features;
