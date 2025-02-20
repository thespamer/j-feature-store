import React, { useState } from 'react';
import {
  Box,
  Button,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  TextField,
  Typography,
  Paper,
  Stack,
  Select,
  MenuItem,
  FormControl,
  InputLabel,
} from '@mui/material';
import AddIcon from '@mui/icons-material/Add';

const FeatureGroups = () => {
  const [open, setOpen] = useState(false);
  const [newGroup, setNewGroup] = useState({
    name: '',
    description: '',
    entity_type: '',
    tags: [],
    frequency: 'daily'
  });

  const handleOpen = () => setOpen(true);
  const handleClose = () => setOpen(false);

  const handleChange = (e) => {
    const { name, value } = e.target;
    setNewGroup(prev => ({
      ...prev,
      [name]: value
    }));
  };

  const handleSubmit = async () => {
    try {
      // Converter tags de string para array se necessário
      const groupData = {
        ...newGroup,
        tags: typeof newGroup.tags === 'string' ? 
          newGroup.tags.split(',').map(tag => tag.trim()) : 
          newGroup.tags
      };

      const response = await fetch('http://localhost:8000/api/v1/feature-groups', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(groupData),
      });

      if (response.ok) {
        handleClose();
        // Limpar o formulário
        setNewGroup({
          name: '',
          description: '',
          entity_type: '',
          tags: [],
          frequency: 'daily'
        });
        // TODO: Atualizar a lista de grupos
      }
    } catch (error) {
      console.error('Error creating feature group:', error);
    }
  };

  return (
    <Box sx={{ p: 3 }}>
      <Stack direction="row" justifyContent="space-between" alignItems="center" mb={3}>
        <Typography variant="h4" gutterBottom>
          Feature Groups
        </Typography>
        <Button
          variant="contained"
          color="primary"
          startIcon={<AddIcon />}
          onClick={handleOpen}
          sx={{
            background: 'linear-gradient(45deg, #00f2ff 30%, #ff00f2 90%)',
            color: 'white',
            '&:hover': {
              background: 'linear-gradient(45deg, #00f2ff 10%, #ff00f2 70%)',
              boxShadow: '0 0 20px rgba(0, 242, 255, 0.5)',
            },
          }}
        >
          Create Group
        </Button>
      </Stack>

      <Dialog open={open} onClose={handleClose}>
        <DialogTitle>Create New Feature Group</DialogTitle>
        <DialogContent>
          <Stack spacing={2} sx={{ mt: 2 }}>
            <TextField
              name="name"
              label="Name"
              value={newGroup.name}
              onChange={handleChange}
              fullWidth
            />
            <TextField
              name="description"
              label="Description"
              value={newGroup.description}
              onChange={handleChange}
              fullWidth
              multiline
              rows={3}
            />
            <TextField
              name="entity_type"
              label="Entity Type"
              value={newGroup.entity_type}
              onChange={handleChange}
              fullWidth
            />
            <TextField
              name="tags"
              label="Tags (comma separated)"
              value={newGroup.tags}
              onChange={handleChange}
              fullWidth
              helperText="Enter tags separated by commas"
            />
            <FormControl fullWidth>
              <InputLabel>Frequency</InputLabel>
              <Select
                name="frequency"
                value={newGroup.frequency}
                onChange={handleChange}
                label="Frequency"
              >
                <MenuItem value="daily">Daily</MenuItem>
                <MenuItem value="hourly">Hourly</MenuItem>
                <MenuItem value="weekly">Weekly</MenuItem>
                <MenuItem value="monthly">Monthly</MenuItem>
              </Select>
            </FormControl>
          </Stack>
        </DialogContent>
        <DialogActions>
          <Button onClick={handleClose} color="primary">
            Cancel
          </Button>
          <Button 
            onClick={handleSubmit} 
            variant="contained" 
            color="primary"
            sx={{
              background: 'linear-gradient(45deg, #00f2ff 30%, #ff00f2 90%)',
              '&:hover': {
                background: 'linear-gradient(45deg, #00f2ff 10%, #ff00f2 70%)',
                boxShadow: '0 0 20px rgba(0, 242, 255, 0.5)',
              },
            }}
          >
            Create
          </Button>
        </DialogActions>
      </Dialog>

      {/* Lista de grupos será adicionada aqui */}
      <Paper 
        sx={{ 
          p: 2,
          background: 'linear-gradient(45deg, rgba(0, 242, 255, 0.05), rgba(255, 0, 242, 0.05))',
          border: '1px solid rgba(0, 242, 255, 0.1)',
          borderRadius: '8px',
          '&:hover': {
            border: '1px solid rgba(0, 242, 255, 0.2)',
            boxShadow: '0 0 20px rgba(0, 242, 255, 0.1)',
          },
        }}
      >
        <Typography variant="body1" color="text.secondary">
          No feature groups yet. Click the button above to create one.
        </Typography>
      </Paper>
    </Box>
  );
};

export default FeatureGroups;
