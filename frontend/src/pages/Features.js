import React, { useState, useEffect } from 'react';
import { 
  Box, 
  Typography, 
  Grid,
  CircularProgress
} from '@mui/material';
import FeatureCard from '../components/FeatureCard';

const API_URL = 'http://localhost:8000/api/v1';

const Features = () => {
  const [features, setFeatures] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    fetchFeatures();
  }, []);

  const fetchFeatures = async () => {
    try {
      setLoading(true);
      setError(null);
      console.log('Fetching features from:', `${API_URL}/features/`);
      
      const response = await fetch(`${API_URL}/features/`, {
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
      console.log('Raw response:', data);
      
      // Garantir que features é um array
      const featuresArray = Array.isArray(data) ? data : [];
      console.log('Processed features:', featuresArray);
      
      setFeatures(featuresArray);
    } catch (error) {
      console.error('Error fetching features:', error);
      setError(error.message);
    } finally {
      setLoading(false);
    }
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
      <Box p={3}>
        <Typography color="error">Error: {error}</Typography>
      </Box>
    );
  }

  return (
    <Box p={3}>
      <Typography variant="h4" gutterBottom>
        Features ({features.length})
      </Typography>
      <Grid container spacing={3}>
        {features.map((feature) => (
          <Grid item xs={12} sm={6} md={4} key={feature.id}>
            <FeatureCard feature={feature} />
          </Grid>
        ))}
        {features.length === 0 && (
          <Grid item xs={12}>
            <Typography variant="body1" color="textSecondary" align="center">
              No features found
            </Typography>
          </Grid>
        )}
      </Grid>
    </Box>
  );
};

export default Features;
