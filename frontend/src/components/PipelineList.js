import React, { useState, useEffect, useCallback } from 'react';
import {
  Box,
  Button,
  Card,
  CardContent,
  CardActions,
  Typography,
  IconButton,
  Chip,
  Grid,
  CircularProgress,
  List,
  ListItem,
  ListItemText,
  ListItemSecondaryAction,
} from '@mui/material';
import PlayArrowIcon from '@mui/icons-material/PlayArrow';
import ScheduleIcon from '@mui/icons-material/Schedule';
import CodeIcon from '@mui/icons-material/Code';
import AddIcon from '@mui/icons-material/Add';
import CreatePipelineDialog from './CreatePipelineDialog';

const API_URL = 'http://localhost:8000/api/v1';

const PipelineList = ({ featureGroupId }) => {
  const [pipelines, setPipelines] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [createDialogOpen, setCreateDialogOpen] = useState(false);

  const fetchPipelines = useCallback(async () => {
    try {
      setLoading(true);
      setError(null);
      const response = await fetch(
        `${API_URL}/pipelines?feature_group_id=${featureGroupId}`
      );
      if (!response.ok) throw new Error('Erro ao carregar pipelines');
      const data = await response.json();
      setPipelines(data);
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  }, [featureGroupId]);

  useEffect(() => {
    if (featureGroupId) {
      fetchPipelines();
    }
  }, [featureGroupId, fetchPipelines]);

  const handleExecutePipeline = async (pipelineId) => {
    try {
      const response = await fetch(
        `${API_URL}/pipelines/${pipelineId}/execute`,
        { method: 'POST' }
      );
      if (!response.ok) throw new Error('Erro ao executar pipeline');
      // Atualiza lista após execução
      fetchPipelines();
    } catch (err) {
      setError(err.message);
    }
  };

  const getStatusColor = (status) => {
    const colors = {
      pending: 'default',
      running: 'primary',
      completed: 'success',
      failed: 'error',
    };
    return colors[status] || 'default';
  };

  const handlePipelineCreated = () => {
    fetchPipelines();
  };

  if (loading) return <CircularProgress />;
  if (error) return <Typography color="error">{error}</Typography>;

  return (
    <Box>
      <Box sx={{ mb: 2, display: 'flex', justifyContent: 'space-between' }}>
        <Typography variant="h6">Pipelines</Typography>
        <Button
          variant="contained"
          color="primary"
          onClick={() => setCreateDialogOpen(true)}
          startIcon={<AddIcon />}
        >
          Novo Pipeline
        </Button>
      </Box>

      <Grid container spacing={2}>
        {pipelines.map((pipeline) => (
          <Grid item xs={12} md={6} key={pipeline.id}>
            <Card>
              <CardContent>
                <Typography variant="h6" gutterBottom>
                  {pipeline.name}
                </Typography>
                
                <Box sx={{ mb: 2 }}>
                  <Chip
                    icon={<CodeIcon />}
                    label={pipeline.config.transformation_type}
                    size="small"
                    sx={{ mr: 1 }}
                  />
                  <Chip
                    icon={<ScheduleIcon />}
                    label={pipeline.config.schedule_interval}
                    size="small"
                    sx={{ mr: 1 }}
                  />
                  <Chip
                    label={pipeline.status}
                    color={getStatusColor(pipeline.status)}
                    size="small"
                  />
                </Box>

                {pipeline.last_run_at && (
                  <Typography variant="body2" color="textSecondary">
                    Última execução: {new Date(pipeline.last_run_at).toLocaleString()}
                  </Typography>
                )}
                
                {pipeline.next_run_at && (
                  <Typography variant="body2" color="textSecondary">
                    Próxima execução: {new Date(pipeline.next_run_at).toLocaleString()}
                  </Typography>
                )}

                {pipeline.error_message && (
                  <Typography color="error" variant="body2">
                    Erro: {pipeline.error_message}
                  </Typography>
                )}
              </CardContent>
              
              <CardActions>
                <IconButton
                  onClick={() => handleExecutePipeline(pipeline.id)}
                  disabled={pipeline.status === 'running'}
                >
                  <PlayArrowIcon />
                </IconButton>
              </CardActions>
            </Card>
          </Grid>
        ))}
      </Grid>

      <CreatePipelineDialog
        open={createDialogOpen}
        onClose={() => setCreateDialogOpen(false)}
        featureGroupId={featureGroupId}
        onPipelineCreated={handlePipelineCreated}
      />
    </Box>
  );
};

export default PipelineList;
