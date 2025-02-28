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
  Input,
  Accordion,
  AccordionSummary,
  AccordionDetails,
  Typography,
} from '@mui/material';
import ExpandMoreIcon from '@mui/icons-material/ExpandMore';

const CreateFeatureGroupDialog = ({ open, onClose, onSubmit, initialData = null }) => {
  const [formData, setFormData] = useState(initialData || {
    name: '',
    description: '',
    entity_type: '',
    tags: [],
    frequency: '',
    owner: '',
    offline_enabled: true,
    online_enabled: true,
    transformation: {
      type: 'sql',
      params: {
        query: '',
        features: []
      }
    }
  });

  const [tagInput, setTagInput] = useState('');
  const [featureInput, setFeatureInput] = useState('');

  const handleChange = (e) => {
    const { name, value } = e.target;
    setFormData(prev => ({
      ...prev,
      [name]: value
    }));
  };

  const handleTransformationChange = (e) => {
    const { name, value } = e.target;
    setFormData(prev => ({
      ...prev,
      transformation: {
        ...prev.transformation,
        params: {
          ...prev.transformation.params,
          [name]: value
        }
      }
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

  const handleFeatureInputKeyDown = (e) => {
    if (e.key === 'Enter' && featureInput) {
      e.preventDefault();
      const newFeature = featureInput.trim();
      if (newFeature && !formData.transformation.params.features.includes(newFeature)) {
        setFormData(prev => ({
          ...prev,
          transformation: {
            ...prev.transformation,
            params: {
              ...prev.transformation.params,
              features: [...prev.transformation.params.features, newFeature]
            }
          }
        }));
      }
      setFeatureInput('');
    }
  };

  const handleDeleteTag = (tagToDelete) => {
    setFormData(prev => ({
      ...prev,
      tags: prev.tags.filter(tag => tag !== tagToDelete)
    }));
  };

  const handleDeleteFeature = (featureToDelete) => {
    setFormData(prev => ({
      ...prev,
      transformation: {
        ...prev.transformation,
        params: {
          ...prev.transformation.params,
          features: prev.transformation.params.features.filter(f => f !== featureToDelete)
        }
      }
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
              <MenuItem value="">None</MenuItem>
              <MenuItem value="daily">Daily</MenuItem>
              <MenuItem value="hourly">Hourly</MenuItem>
              <MenuItem value="weekly">Weekly</MenuItem>
              <MenuItem value="monthly">Monthly</MenuItem>
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
              placeholder="Press Enter to add tag"
            />
            <Box sx={{ display: 'flex', flexWrap: 'wrap', gap: 1, mt: 1 }}>
              {formData.tags.map((tag) => (
                <Chip
                  key={tag}
                  label={tag}
                  onDelete={() => handleDeleteTag(tag)}
                />
              ))}
            </Box>
          </Box>

          <Accordion>
            <AccordionSummary expandIcon={<ExpandMoreIcon />}>
              <Typography>Transformação SQL</Typography>
            </AccordionSummary>
            <AccordionDetails>
              <Box display="flex" flexDirection="column" gap={2}>
                <TextField
                  name="query"
                  label="Query SQL"
                  value={formData.transformation.params.query}
                  onChange={handleTransformationChange}
                  fullWidth
                  multiline
                  rows={5}
                />
                <Box>
                  <TextField
                    label="Add Features"
                    value={featureInput}
                    onChange={(e) => setFeatureInput(e.target.value)}
                    onKeyDown={handleFeatureInputKeyDown}
                    fullWidth
                    placeholder="Press Enter to add feature"
                    helperText="Nome das colunas que serão usadas como features"
                  />
                  <Box sx={{ display: 'flex', flexWrap: 'wrap', gap: 1, mt: 1 }}>
                    {formData.transformation.params.features.map((feature) => (
                      <Chip
                        key={feature}
                        label={feature}
                        onDelete={() => handleDeleteFeature(feature)}
                      />
                    ))}
                  </Box>
                </Box>
              </Box>
            </AccordionDetails>
          </Accordion>
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
