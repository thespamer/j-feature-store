import React, { useState, useEffect } from 'react';
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
  Card,
  CardContent,
  Grid,
  Chip,
} from '@mui/material';
import AddIcon from '@mui/icons-material/Add';

const Features = () => {
  const [open, setOpen] = useState(false);
  const [features, setFeatures] = useState([]);
  const [newFeature, setNewFeature] = useState({
    name: '',
    description: '',
    type: '',
    value: ''
  });

  const fetchFeatures = async () => {
    try {
      const response = await fetch('http://localhost:8000/api/v1/features');
      const data = await response.json();
      setFeatures(data);
    } catch (error) {
      console.error('Error fetching features:', error);
    }
  };

  useEffect(() => {
    fetchFeatures();
  }, []);

  const handleOpen = () => setOpen(true);
  const handleClose = () => setOpen(false);

  const handleChange = (e) => {
    const { name, value } = e.target;
    setNewFeature(prev => ({
      ...prev,
      [name]: value
    }));
  };

  const handleSubmit = async () => {
    try {
      const response = await fetch('http://localhost:8000/api/v1/features', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(newFeature),
      });

      if (response.ok) {
        handleClose();
        // Limpar o formulário
        setNewFeature({
          name: '',
          description: '',
          type: '',
          value: ''
        });
        // Atualizar a lista de features
        fetchFeatures();
      }
    } catch (error) {
      console.error('Error creating feature:', error);
    }
  };

  return (
    <Box sx={{ p: 3 }}>
      <Stack direction="row" justifyContent="space-between" alignItems="center" mb={3}>
        <Typography variant="h4" gutterBottom>
          Features
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
          Create Feature
        </Button>
      </Stack>

      <Dialog open={open} onClose={handleClose}>
        <DialogTitle>Create New Feature</DialogTitle>
        <DialogContent>
          <Stack spacing={2} sx={{ mt: 2 }}>
            <TextField
              name="name"
              label="Name"
              value={newFeature.name}
              onChange={handleChange}
              fullWidth
            />
            <TextField
              name="description"
              label="Description"
              value={newFeature.description}
              onChange={handleChange}
              fullWidth
              multiline
              rows={3}
            />
            <TextField
              name="type"
              label="Type"
              value={newFeature.type}
              onChange={handleChange}
              fullWidth
            />
            <TextField
              name="value"
              label="Value"
              value={newFeature.value}
              onChange={handleChange}
              fullWidth
            />
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

      <Grid container spacing={3}>
        {features.length > 0 ? (
          features.map((feature) => (
            <Grid item xs={12} sm={6} md={4} key={feature.id}>
              <Card 
                sx={{ 
                  height: '100%',
                  background: 'linear-gradient(45deg, rgba(0, 242, 255, 0.05), rgba(255, 0, 242, 0.05))',
                  border: '1px solid rgba(0, 242, 255, 0.1)',
                  borderRadius: '8px',
                  transition: 'all 0.3s ease-in-out',
                  '&:hover': {
                    border: '1px solid rgba(0, 242, 255, 0.2)',
                    boxShadow: '0 0 20px rgba(0, 242, 255, 0.1)',
                    transform: 'translateY(-2px)',
                  },
                }}
              >
                <CardContent>
                  <Typography variant="h6" gutterBottom color="primary">
                    {feature.name}
                  </Typography>
                  <Typography variant="body2" color="text.secondary" paragraph>
                    {feature.description}
                  </Typography>
                  <Stack direction="row" spacing={1} mb={2}>
                    <Chip 
                      label={feature.type}
                      sx={{
                        background: 'linear-gradient(45deg, #00f2ff 30%, #ff00f2 90%)',
                        color: 'white',
                      }}
                    />
                  </Stack>
                  <Typography variant="body2" color="text.primary">
                    Value: {feature.value}
                  </Typography>
                </CardContent>
              </Card>
            </Grid>
          ))
        ) : (
          <Grid item xs={12}>
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
                No features yet. Click the button above to create one.
              </Typography>
            </Paper>
          </Grid>
        )}
      </Grid>
    </Box>
  );
};

export default Features;
