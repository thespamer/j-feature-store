import React, { useState, useEffect } from 'react';
import {
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  Button,
  TextField,
  Select,
  MenuItem,
  FormControl,
  InputLabel,
  Box,
  Chip,
  Input,
  CircularProgress,
} from '@mui/material';

const API_URL = 'http://localhost:8000/api/v1';

const CreateFeatureDialog = ({ open, onClose, feature = null, onSave }) => {
  const [loading, setLoading] = useState(false);
  const [groups, setGroups] = useState([]);
  const [formData, setFormData] = useState({
    name: '',
    description: '',
    type: 'float',
    entity_id: '',
    feature_group_id: '',
    metadata: {
      tags: []
    }
  });

  useEffect(() => {
    if (open) {
      fetchGroups();
      if (feature) {
        setFormData({
          name: feature.name || '',
          description: feature.description || '',
          type: feature.type || 'float',
          entity_id: feature.entity_id || '',
          feature_group_id: feature.feature_group_id || '',
          metadata: {
            tags: feature.metadata?.tags || []
          }
        });
      }
    }
  }, [open, feature]);

  const fetchGroups = async () => {
    try {
      const response = await fetch(`${API_URL}/feature-groups`);
      if (!response.ok) throw new Error('Erro ao carregar grupos');
      const data = await response.json();
      setGroups(data);
    } catch (error) {
      console.error('Error fetching groups:', error);
    }
  };

  const handleInputChange = (e) => {
    const { name, value } = e.target;
    setFormData(prev => ({
      ...prev,
      [name]: value
    }));
  };

  const handleTagsChange = (e) => {
    const tags = e.target.value.split(',').map(tag => tag.trim()).filter(Boolean);
    setFormData(prev => ({
      ...prev,
      metadata: {
        ...prev.metadata,
        tags
      }
    }));
  };

  const handleSubmit = async () => {
    try {
      setLoading(true);
      const response = await fetch(`${API_URL}/features${feature ? `/${feature.id}` : ''}`, {
        method: feature ? 'PUT' : 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(formData),
      });

      if (!response.ok) throw new Error('Erro ao salvar feature');
      
      const savedFeature = await response.json();
      onSave(savedFeature);
      onClose();
    } catch (error) {
      console.error('Error saving feature:', error);
    } finally {
      setLoading(false);
    }
  };

  return (
    <Dialog open={open} onClose={onClose} maxWidth="sm" fullWidth>
      <DialogTitle>
        {feature ? 'Editar Feature' : 'Nova Feature'}
      </DialogTitle>
      <DialogContent>
        <Box display="flex" flexDirection="column" gap={2} mt={2}>
          <TextField
            name="name"
            label="Nome"
            value={formData.name}
            onChange={handleInputChange}
            fullWidth
            required
          />
          <TextField
            name="description"
            label="Descrição"
            value={formData.description}
            onChange={handleInputChange}
            fullWidth
            multiline
            rows={3}
          />
          <FormControl fullWidth>
            <InputLabel>Tipo</InputLabel>
            <Select
              name="type"
              value={formData.type}
              onChange={handleInputChange}
              label="Tipo"
            >
              <MenuItem value="float">Float</MenuItem>
              <MenuItem value="int">Integer</MenuItem>
              <MenuItem value="string">String</MenuItem>
              <MenuItem value="boolean">Boolean</MenuItem>
              <MenuItem value="datetime">DateTime</MenuItem>
            </Select>
          </FormControl>
          <TextField
            name="entity_id"
            label="Entity ID"
            value={formData.entity_id}
            onChange={handleInputChange}
            fullWidth
          />
          <FormControl fullWidth>
            <InputLabel>Grupo de Features</InputLabel>
            <Select
              name="feature_group_id"
              value={formData.feature_group_id}
              onChange={handleInputChange}
              label="Grupo de Features"
            >
              <MenuItem value="">Nenhum</MenuItem>
              {groups.map((group) => (
                <MenuItem key={group.id} value={group.id}>
                  {group.name}
                </MenuItem>
              ))}
            </Select>
          </FormControl>
          <TextField
            name="tags"
            label="Tags (separadas por vírgula)"
            value={formData.metadata.tags.join(', ')}
            onChange={handleTagsChange}
            fullWidth
          />
          <Box display="flex" gap={1} flexWrap="wrap">
            {formData.metadata.tags.map((tag) => (
              <Chip key={tag} label={tag} size="small" />
            ))}
          </Box>
        </Box>
      </DialogContent>
      <DialogActions>
        <Button onClick={onClose} color="inherit">
          Cancelar
        </Button>
        <Button
          onClick={handleSubmit}
          color="primary"
          disabled={loading || !formData.name}
        >
          {loading ? <CircularProgress size={24} /> : 'Salvar'}
        </Button>
      </DialogActions>
    </Dialog>
  );
};

export default CreateFeatureDialog;
