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
  Stack,
  Card,
  CardContent,
  Grid,
  Chip,
  MenuItem,
} from '@mui/material';
import AddIcon from '@mui/icons-material/Add';

const Features = () => {
  const [open, setOpen] = useState(false);
  const [features, setFeatures] = useState([]);
  const [newFeature, setNewFeature] = useState({
    name: '',
    description: '',
    data_type: 'float',
    entity_id: '',
    feature_group_id: '',
    tags: []
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
        fetchFeatures();
        setNewFeature({
          name: '',
          description: '',
          data_type: 'float',
          entity_id: '',
          feature_group_id: '',
          tags: []
        });
      }
    } catch (error) {
      console.error('Error creating feature:', error);
    }
  };

  return (
    <Box sx={{ p: 3 }}>
      <Stack direction="row" justifyContent="space-between" alignItems="center" mb={3}>
        <Typography variant="h4">
          Features
        </Typography>
        <Button
          variant="contained"
          startIcon={<AddIcon />}
          onClick={handleOpen}
          sx={{
            background: 'linear-gradient(45deg, #00f2ff 30%, #ff00f2 90%)',
            color: 'white',
            '&:hover': {
              background: 'linear-gradient(45deg, #00f2ff 20%, #ff00f2 100%)',
            },
          }}
        >
          Nova Feature
        </Button>
      </Stack>

      <Grid container spacing={3}>
        {features.map((feature) => (
          <Grid item xs={12} sm={6} md={4} key={feature.id}>
            <Card 
              sx={{ 
                height: '100%',
                background: 'linear-gradient(45deg, rgba(0, 242, 255, 0.05), rgba(255, 0, 242, 0.05))',
                border: '1px solid rgba(0, 242, 255, 0.1)',
                transition: 'all 0.3s ease-in-out',
                '&:hover': {
                  border: '1px solid rgba(0, 242, 255, 0.2)',
                  boxShadow: '0 0 20px rgba(0, 242, 255, 0.1)',
                  transform: 'translateY(-4px)',
                },
              }}
            >
              <CardContent>
                <Typography variant="h6" color="primary" gutterBottom>
                  {feature.name}
                </Typography>
                <Typography variant="body2" color="textSecondary" paragraph>
                  {feature.description}
                </Typography>
                <Stack direction="row" spacing={1} mb={2}>
                  <Chip 
                    label={`Tipo: ${feature.data_type}`}
                    size="small"
                    sx={{
                      background: 'linear-gradient(45deg, #00f2ff 30%, #ff00f2 90%)',
                      color: 'white',
                    }}
                  />
                  <Chip 
                    label={`Entidade: ${feature.entity_id}`}
                    size="small"
                    sx={{
                      background: 'linear-gradient(45deg, #ff00f2 30%, #00f2ff 90%)',
                      color: 'white',
                    }}
                  />
                </Stack>
                <Box>
                  {feature.tags.map((tag, index) => (
                    <Chip
                      key={index}
                      label={tag}
                      size="small"
                      sx={{
                        m: 0.5,
                        background: 'rgba(0, 242, 255, 0.1)',
                        border: '1px solid rgba(0, 242, 255, 0.2)',
                        color: 'white',
                      }}
                    />
                  ))}
                </Box>
              </CardContent>
            </Card>
          </Grid>
        ))}
      </Grid>

      <Dialog open={open} onClose={handleClose}>
        <DialogTitle>Nova Feature</DialogTitle>
        <DialogContent>
          <Stack spacing={2} sx={{ mt: 2 }}>
            <TextField
              name="name"
              label="Nome"
              fullWidth
              value={newFeature.name}
              onChange={handleChange}
            />
            <TextField
              name="description"
              label="Descrição"
              fullWidth
              multiline
              rows={3}
              value={newFeature.description}
              onChange={handleChange}
            />
            <TextField
              name="data_type"
              label="Tipo de Dado"
              select
              fullWidth
              value={newFeature.data_type}
              onChange={handleChange}
            >
              <MenuItem value="float">Float</MenuItem>
              <MenuItem value="int">Integer</MenuItem>
              <MenuItem value="string">String</MenuItem>
            </TextField>
            <TextField
              name="entity_id"
              label="ID da Entidade"
              fullWidth
              value={newFeature.entity_id}
              onChange={handleChange}
            />
            <TextField
              name="feature_group_id"
              label="ID do Grupo"
              fullWidth
              value={newFeature.feature_group_id}
              onChange={handleChange}
            />
          </Stack>
        </DialogContent>
        <DialogActions>
          <Button onClick={handleClose}>Cancelar</Button>
          <Button 
            onClick={handleSubmit}
            sx={{
              background: 'linear-gradient(45deg, #00f2ff 30%, #ff00f2 90%)',
              color: 'white',
              '&:hover': {
                background: 'linear-gradient(45deg, #00f2ff 20%, #ff00f2 100%)',
              },
            }}
          >
            Criar
          </Button>
        </DialogActions>
      </Dialog>
    </Box>
  );
};

export default Features;
