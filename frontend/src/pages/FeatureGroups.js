import React, { useState, useEffect } from 'react';
import { 
  Box, 
  Typography, 
  Grid,
  CircularProgress
} from '@mui/material';
import FeatureGroupCard from '../components/FeatureGroupCard';

const API_URL = 'http://localhost:8000/api/v1';

const FeatureGroups = () => {
  const [groups, setGroups] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    fetchGroups();
  }, []);

  const fetchGroups = async () => {
    try {
      setLoading(true);
      setError(null);
      console.log('Fetching groups from:', `${API_URL}/feature-groups/`);
      
      const response = await fetch(`${API_URL}/feature-groups/`, {
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
      
      // Garantir que groups é um array
      const groupsArray = Array.isArray(data) ? data : [];
      console.log('Processed groups:', groupsArray);
      
      setGroups(groupsArray);
    } catch (error) {
      console.error('Error fetching groups:', error);
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
        Feature Groups ({groups.length})
      </Typography>
      <Grid container spacing={3}>
        {groups.map((group) => (
          <Grid item xs={12} sm={6} md={4} key={group.id}>
            <FeatureGroupCard group={group} />
          </Grid>
        ))}
        {groups.length === 0 && (
          <Grid item xs={12}>
            <Typography variant="body1" color="textSecondary" align="center">
              No feature groups found
            </Typography>
          </Grid>
        )}
      </Grid>
    </Box>
  );
};

export default FeatureGroups;
