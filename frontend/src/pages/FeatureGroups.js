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
  Select,
  MenuItem,
  FormControl,
  InputLabel,
  Card,
  CardContent,
  Grid,
  Chip,
  List,
  ListItem,
  ListItemText,
} from '@mui/material';
import AddIcon from '@mui/icons-material/Add';

const FeatureGroups = () => {
  const [open, setOpen] = useState(false);
  const [groups, setGroups] = useState([]);
  const [newGroup, setNewGroup] = useState({
    name: '',
    description: '',
    entity_type: '',
    features: [],
    tags: [],
    frequency: 'daily'
  });

  const fetchGroups = async () => {
    try {
      const response = await fetch('http://localhost:8000/api/v1/feature-groups');
      const data = await response.json();
      setGroups(data);
    } catch (error) {
      console.error('Error fetching feature groups:', error);
    }
  };

  useEffect(() => {
    fetchGroups();
  }, []);

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
      const response = await fetch('http://localhost:8000/api/v1/feature-groups', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(newGroup),
      });

      if (response.ok) {
        handleClose();
        fetchGroups();
        setNewGroup({
          name: '',
          description: '',
          entity_type: '',
          features: [],
          tags: [],
          frequency: 'daily'
        });
      }
    } catch (error) {
      console.error('Error creating feature group:', error);
    }
  };

  return (
    <Box sx={{ p: 3 }}>
      <Stack direction="row" justifyContent="space-between" alignItems="center" mb={3}>
        <Typography variant="h4">
          Grupos de Features
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
          Novo Grupo
        </Button>
      </Stack>

      <Grid container spacing={3}>
        {groups.map((group) => (
          <Grid item xs={12} sm={6} md={4} key={group.id}>
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
                  {group.name}
                </Typography>
                <Typography variant="body2" color="textSecondary" paragraph>
                  {group.description}
                </Typography>
                <Stack direction="row" spacing={1} mb={2}>
                  <Chip 
                    label={`Entidade: ${group.entity_type}`}
                    size="small"
                    sx={{
                      background: 'linear-gradient(45deg, #00f2ff 30%, #ff00f2 90%)',
                      color: 'white',
                    }}
                  />
                  <Chip 
                    label={`Frequência: ${group.frequency}`}
                    size="small"
                    sx={{
                      background: 'linear-gradient(45deg, #ff00f2 30%, #00f2ff 90%)',
                      color: 'white',
                    }}
                  />
                </Stack>
                {group.features.length > 0 && (
                  <Box mb={2}>
                    <Typography variant="subtitle2" color="textSecondary" gutterBottom>
                      Features:
                    </Typography>
                    <List dense>
                      {group.features.map((feature, index) => (
                        <ListItem key={index} sx={{ py: 0 }}>
                          <ListItemText 
                            primary={feature}
                            sx={{
                              '& .MuiTypography-root': {
                                color: 'rgba(255, 255, 255, 0.7)',
                              }
                            }}
                          />
                        </ListItem>
                      ))}
                    </List>
                  </Box>
                )}
                <Box>
                  {group.tags.map((tag, index) => (
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
        <DialogTitle>Novo Grupo de Features</DialogTitle>
        <DialogContent>
          <Stack spacing={2} sx={{ mt: 2 }}>
            <TextField
              name="name"
              label="Nome"
              fullWidth
              value={newGroup.name}
              onChange={handleChange}
            />
            <TextField
              name="description"
              label="Descrição"
              fullWidth
              multiline
              rows={3}
              value={newGroup.description}
              onChange={handleChange}
            />
            <TextField
              name="entity_type"
              label="Tipo de Entidade"
              fullWidth
              value={newGroup.entity_type}
              onChange={handleChange}
            />
            <FormControl fullWidth>
              <InputLabel>Frequência</InputLabel>
              <Select
                name="frequency"
                value={newGroup.frequency}
                label="Frequência"
                onChange={handleChange}
              >
                <MenuItem value="hourly">Horária</MenuItem>
                <MenuItem value="daily">Diária</MenuItem>
                <MenuItem value="weekly">Semanal</MenuItem>
                <MenuItem value="monthly">Mensal</MenuItem>
              </Select>
            </FormControl>
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

export default FeatureGroups;
