import React, { useState, useEffect } from 'react';
import {
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  Button,
  List,
  ListItem,
  ListItemText,
  ListItemSecondaryAction,
  IconButton,
  Checkbox,
  Typography,
  CircularProgress,
} from '@mui/material';
import DeleteIcon from '@mui/icons-material/Delete';

const API_URL = 'http://localhost:8000/api/v1';

const ManageGroupFeaturesDialog = ({ open, onClose, group, onUpdate }) => {
  const [loading, setLoading] = useState(true);
  const [allFeatures, setAllFeatures] = useState([]);
  const [selectedFeatures, setSelectedFeatures] = useState([]);
  const [error, setError] = useState(null);

  // Carregar todas as features disponíveis
  useEffect(() => {
    if (open) {
      fetchFeatures();
    }
  }, [open]);

  // Inicializar features selecionadas quando o grupo muda
  useEffect(() => {
    if (group && Array.isArray(group.features)) {
      setSelectedFeatures(group.features);
    } else {
      setSelectedFeatures([]);
    }
  }, [group]);

  const fetchFeatures = async () => {
    try {
      setLoading(true);
      setError(null);
      const response = await fetch(`${API_URL}/features`);
      if (!response.ok) throw new Error('Erro ao carregar features');
      const data = await response.json();
      setAllFeatures(Array.isArray(data) ? data : []);
    } catch (err) {
      console.error('Error fetching features:', err);
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  const handleToggleFeature = (featureId) => {
    setSelectedFeatures(prev => {
      const prevArray = Array.isArray(prev) ? prev : [];
      if (prevArray.includes(featureId)) {
        return prevArray.filter(id => id !== featureId);
      } else {
        return [...prevArray, featureId];
      }
    });
  };

  const handleSave = async () => {
    if (!group || !group.id) {
      setError('Grupo inválido');
      return;
    }

    try {
      setLoading(true);
      const response = await fetch(`${API_URL}/feature-groups/${group.id}`, {
        method: 'PUT',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          features: selectedFeatures
        }),
      });

      if (!response.ok) throw new Error('Erro ao atualizar features do grupo');
      
      const updatedGroup = await response.json();
      if (onUpdate) onUpdate(updatedGroup);
      onClose();
    } catch (err) {
      console.error('Error saving features:', err);
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  if (!group) return null;

  return (
    <Dialog open={open} onClose={onClose} maxWidth="md" fullWidth>
      <DialogTitle>
        Gerenciar Features do Grupo: {group.name}
      </DialogTitle>
      <DialogContent>
        {error && (
          <Typography color="error" gutterBottom>
            {error}
          </Typography>
        )}
        {loading ? (
          <CircularProgress />
        ) : (
          <List>
            {Array.isArray(allFeatures) && allFeatures.map((feature) => (
              <ListItem key={feature.id} dense button onClick={() => handleToggleFeature(feature.id)}>
                <Checkbox
                  edge="start"
                  checked={Array.isArray(selectedFeatures) && selectedFeatures.includes(feature.id)}
                  tabIndex={-1}
                  disableRipple
                />
                <ListItemText
                  primary={feature.name}
                  secondary={feature.description}
                />
                <ListItemSecondaryAction>
                  <Typography variant="caption" color="textSecondary">
                    {feature.type}
                  </Typography>
                </ListItemSecondaryAction>
              </ListItem>
            ))}
          </List>
        )}
      </DialogContent>
      <DialogActions>
        <Button onClick={onClose} color="inherit">
          Cancelar
        </Button>
        <Button 
          onClick={handleSave} 
          color="primary" 
          disabled={loading || !Array.isArray(selectedFeatures)}
        >
          Salvar
        </Button>
      </DialogActions>
    </Dialog>
  );
};

export default ManageGroupFeaturesDialog;
