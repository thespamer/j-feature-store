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
  Alert,
  Typography,
  Switch,
  FormControlLabel
} from '@mui/material';
import config from '../config';

const CreateFeatureDialog = ({ open, onClose, onFeatureCreated }) => {
  const [formData, setFormData] = useState({
    name: '',
    description: '',
    type: 'numerical',
    entity_id: 'customer_id',
    validation_rules: {
      allow_null: false,
      min_value: null,
      max_value: null
    },
    transformation: {
      enabled: false,
      sql_query: '',
      aggregation_window: '1d'
    }
  });
  const [error, setError] = useState(null);
  const [loading, setLoading] = useState(false);

  const handleChange = (e) => {
    const { name, value } = e.target;
    if (name.includes('.')) {
      const [parent, child] = name.split('.');
      setFormData(prev => ({
        ...prev,
        [parent]: {
          ...prev[parent],
          [child]: value
        }
      }));
    } else {
      setFormData(prev => ({
        ...prev,
        [name]: value
      }));
    }
  };

  const handleTransformationToggle = () => {
    setFormData(prev => ({
      ...prev,
      transformation: {
        ...prev.transformation,
        enabled: !prev.transformation.enabled
      }
    }));
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    setError(null);

    try {
      const requestBody = {
        ...formData,
        metadata: {
          owner: 'user',
          created_at: new Date().toISOString(),
          updated_at: new Date().toISOString(),
          tags: ['web-ui']
        }
      };

      // Remove transformation if not enabled
      if (!formData.transformation.enabled) {
        delete requestBody.transformation;
      }

      const response = await fetch(`${config.API_URL}/features/`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(requestBody)
      });

      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.detail || 'Error creating feature');
      }

      const newFeature = await response.json();
      onFeatureCreated(newFeature);
      onClose();
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  return (
    <Dialog open={open} onClose={onClose} maxWidth="md" fullWidth>
      <DialogTitle>Create New Feature</DialogTitle>
      <form onSubmit={handleSubmit}>
        <DialogContent>
          {error && (
            <Box mb={2}>
              <Alert severity="error">{error}</Alert>
            </Box>
          )}
          
          <Box mb={2}>
            <TextField
              fullWidth
              label="Name"
              name="name"
              value={formData.name}
              onChange={handleChange}
              required
              helperText="Feature name (e.g., customer_total_purchases)"
            />
          </Box>

          <Box mb={2}>
            <TextField
              fullWidth
              label="Description"
              name="description"
              value={formData.description}
              onChange={handleChange}
              multiline
              rows={2}
              required
              helperText="Detailed description of the feature"
            />
          </Box>

          <Box mb={2}>
            <FormControl fullWidth>
              <InputLabel>Type</InputLabel>
              <Select
                name="type"
                value={formData.type}
                onChange={handleChange}
                required
              >
                <MenuItem value="numerical">Numerical</MenuItem>
                <MenuItem value="categorical">Categorical</MenuItem>
                <MenuItem value="temporal">Temporal</MenuItem>
              </Select>
            </FormControl>
          </Box>

          <Box mb={2}>
            <TextField
              fullWidth
              label="Entity ID"
              name="entity_id"
              value={formData.entity_id}
              onChange={handleChange}
              required
              helperText="Entity identifier (e.g., customer_id, product_id)"
            />
          </Box>

          <Box mb={2}>
            <Typography variant="subtitle1" gutterBottom>
              Transformation
            </Typography>
            <FormControlLabel
              control={
                <Switch
                  checked={formData.transformation.enabled}
                  onChange={handleTransformationToggle}
                  name="transformation.enabled"
                />
              }
              label="Enable SQL Transformation"
            />
            
            {formData.transformation.enabled && (
              <>
                <Box mt={2}>
                  <TextField
                    fullWidth
                    label="SQL Query"
                    name="transformation.sql_query"
                    value={formData.transformation.sql_query}
                    onChange={handleChange}
                    multiline
                    rows={4}
                    required
                    helperText={
                      <span>
                        SQL transformation query. Example:<br />
                        SELECT<br />
                        &nbsp;&nbsp;user_id,<br />
                        &nbsp;&nbsp;AVG(session_duration) as avg_session_duration<br />
                        FROM input_data<br />
                        GROUP BY user_id
                      </span>
                    }
                  />
                </Box>
                <Box mt={2}>
                  <FormControl fullWidth>
                    <InputLabel>Aggregation Window</InputLabel>
                    <Select
                      name="transformation.aggregation_window"
                      value={formData.transformation.aggregation_window}
                      onChange={handleChange}
                      required
                    >
                      <MenuItem value="1h">1 Hour</MenuItem>
                      <MenuItem value="6h">6 Hours</MenuItem>
                      <MenuItem value="12h">12 Hours</MenuItem>
                      <MenuItem value="1d">1 Day</MenuItem>
                      <MenuItem value="7d">7 Days</MenuItem>
                      <MenuItem value="30d">30 Days</MenuItem>
                    </Select>
                  </FormControl>
                </Box>
              </>
            )}
          </Box>
        </DialogContent>
        
        <DialogActions>
          <Button onClick={onClose}>Cancel</Button>
          <Button 
            type="submit" 
            variant="contained" 
            color="primary"
            disabled={loading}
          >
            {loading ? 'Creating...' : 'Create'}
          </Button>
        </DialogActions>
      </form>
    </Dialog>
  );
};

export default CreateFeatureDialog;
