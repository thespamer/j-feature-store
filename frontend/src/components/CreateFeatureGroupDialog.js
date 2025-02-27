import React, { useState } from 'react';
import {
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  TextField,
  Button,
  FormControl,
  InputLabel,
  Select,
  MenuItem,
  Box,
  Chip,
  Input
} from '@mui/material';

const CreateFeatureGroupDialog = ({ open, onClose, onSubmit, initialData = null }) => {
  const [formData, setFormData] = useState(initialData || {
    name: '',
    description: '',
    entity_type: '',
    tags: [],
    frequency: '',
    owner: '',
    offline_enabled: true,
    online_enabled: true
  });

  const [tagInput, setTagInput] = useState('');

  const handleChange = (e) => {
    const { name, value } = e.target;
    setFormData(prev => ({
      ...prev,
      [name]: value
    }));
  };

  const handleTagInputKeyDown = (e) => {
    if (e.key === 'Enter' && tagInput) {
      e.preventDefault();
      const newTag = tagInput.trim();
      if (newTag && !formData.tags.includes(newTag)) {
        setFormData(prev => ({
          ...prev,
          tags: [...prev.tags, newTag]
        }));
      }
      setTagInput('');
    }
  };

  const handleDeleteTag = (tagToDelete) => {
    setFormData(prev => ({
      ...prev,
      tags: prev.tags.filter(tag => tag !== tagToDelete)
    }));
  };

  const handleSubmit = () => {
    onSubmit(formData);
    onClose();
  };

  return (
    <Dialog open={open} onClose={onClose} maxWidth="sm" fullWidth>
      <DialogTitle>
        {initialData ? 'Edit Feature Group' : 'Create Feature Group'}
      </DialogTitle>
      <DialogContent>
        <Box sx={{ display: 'flex', flexDirection: 'column', gap: 2, mt: 2 }}>
          <TextField
            name="name"
            label="Name"
            value={formData.name}
            onChange={handleChange}
            fullWidth
            required
          />
          <TextField
            name="description"
            label="Description"
            value={formData.description}
            onChange={handleChange}
            fullWidth
            multiline
            rows={3}
          />
          <TextField
            name="entity_type"
            label="Entity Type"
            value={formData.entity_type}
            onChange={handleChange}
            fullWidth
            required
          />
          <FormControl fullWidth>
            <InputLabel>Update Frequency</InputLabel>
            <Select
              name="frequency"
              value={formData.frequency}
              onChange={handleChange}
              label="Update Frequency"
            >
              <MenuItem value="hourly">Hourly</MenuItem>
              <MenuItem value="daily">Daily</MenuItem>
              <MenuItem value="weekly">Weekly</MenuItem>
              <MenuItem value="monthly">Monthly</MenuItem>
              <MenuItem value="on_demand">On Demand</MenuItem>
            </Select>
          </FormControl>
          <TextField
            name="owner"
            label="Owner"
            value={formData.owner}
            onChange={handleChange}
            fullWidth
          />
          <Box>
            <TextField
              label="Add Tags"
              value={tagInput}
              onChange={(e) => setTagInput(e.target.value)}
              onKeyDown={handleTagInputKeyDown}
              fullWidth
              helperText="Press Enter to add tags"
            />
            <Box sx={{ display: 'flex', flexWrap: 'wrap', gap: 1, mt: 1 }}>
              {formData.tags.map((tag, index) => (
                <Chip
                  key={index}
                  label={tag}
                  onDelete={() => handleDeleteTag(tag)}
                  size="small"
                />
              ))}
            </Box>
          </Box>
        </Box>
      </DialogContent>
      <DialogActions>
        <Button onClick={onClose}>Cancel</Button>
        <Button onClick={handleSubmit} variant="contained" color="primary">
          {initialData ? 'Update' : 'Create'}
        </Button>
      </DialogActions>
    </Dialog>
  );
};

export default CreateFeatureGroupDialog;
