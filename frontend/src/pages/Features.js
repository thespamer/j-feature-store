import React, { useState, useEffect } from 'react';
import { 
  Box, 
  Typography, 
  Grid,
  CircularProgress,
  Button,
  Fab,
  Tooltip
} from '@mui/material';
import AddIcon from '@mui/icons-material/Add';
import FeatureCard from '../components/FeatureCard';
import CreateFeatureDialog from '../components/CreateFeatureDialog';
import config from '../config';

const Features = () => {
  const [features, setFeatures] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [createDialogOpen, setCreateDialogOpen] = useState(false);

  useEffect(() => {
    fetchFeatures();
  }, []);

  const fetchFeatures = async () => {
    try {
      setLoading(true);
      setError(null);
      
      const response = await fetch(`${config.API_URL}/features/`, {
        method: 'GET',
        headers: {
          'Accept': 'application/json',
          'Content-Type': 'application/json'
        },
        mode: 'cors'
      });
      
      if (!response.ok) {
        const errorText = await response.text();
        throw new Error(`HTTP error! status: ${response.status}, message: ${errorText}`);
      }
      
      const data = await response.json();
      const featuresArray = Array.isArray(data) ? data : [];
      setFeatures(featuresArray);
    } catch (error) {
      console.error('Error fetching features:', error);
      const errorMessage = error.message.includes('net::ERR_CONNECTION_RESET')
        ? 'Não foi possível conectar ao servidor. Por favor, verifique se o backend está rodando e tente novamente.'
        : error.message || 'Erro ao carregar features. Por favor, tente novamente.';
      setError(errorMessage);
    } finally {
      setLoading(false);
    }
  };

  const handleFeatureCreated = (newFeature) => {
    setFeatures(prev => [...prev, newFeature]);
  };

  if (loading) {
    return (
      <Box display="flex" justifyContent="center" alignItems="center" minHeight="200px">
        <CircularProgress />
      </Box>
    );
  }

  if (error) {
    return (
      <Box display="flex" justifyContent="center" alignItems="center" minHeight="200px">
        <Typography color="error" variant="h6" component="div">
          {error}
          <Box mt={2}>
            <Button onClick={fetchFeatures} className="retry-button">
              Tentar Novamente
            </Button>
          </Box>
        </Typography>
      </Box>
    );
  }

  return (
    <Box p={3}>
      <Box display="flex" justifyContent="space-between" alignItems="center" mb={3}>
        <Typography variant="h4">
          Features ({features.length})
        </Typography>
        <Tooltip title="Create new feature">
          <Fab 
            color="primary" 
            aria-label="add"
            onClick={() => setCreateDialogOpen(true)}
          >
            <AddIcon />
          </Fab>
        </Tooltip>
      </Box>

      <Grid container spacing={3}>
        {features.map((feature) => (
          <Grid item xs={12} sm={6} md={4} key={feature.id}>
            <FeatureCard feature={feature} />
          </Grid>
        ))}
        {features.length === 0 && (
          <Grid item xs={12}>
            <Typography variant="body1" color="textSecondary" align="center">
              No features found. Click the + button to create your first feature.
            </Typography>
          </Grid>
        )}
      </Grid>

      <CreateFeatureDialog
        open={createDialogOpen}
        onClose={() => setCreateDialogOpen(false)}
        onFeatureCreated={handleFeatureCreated}
      />
    </Box>
  );
};

export default Features;
