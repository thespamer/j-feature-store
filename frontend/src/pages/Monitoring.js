import React, { useState, useEffect } from 'react';
import {
  Box,
  Grid,
  Paper,
  Typography,
  Card,
  CardContent,
  Stack,
  LinearProgress,
  List,
  ListItem,
  ListItemText,
  Divider,
} from '@mui/material';

const Monitoring = () => {
  const [metrics, setMetrics] = useState({
    processedFeatures: 0,
    totalFeatures: 0,
    processingRate: 0,
    lastProcessingTime: null,
    recentActivity: [],
    featureStats: {
      numerical: 0,
      categorical: 0,
      temporal: 0
    }
  });

  const fetchMetrics = async () => {
    try {
      const response = await fetch('http://localhost:8000/api/v1/monitoring/metrics');
      const data = await response.json();
      // Map feature_types to featureStats
      const mappedData = {
        ...data,
        featureStats: data.feature_types || {
          numerical: 0,
          categorical: 0,
          temporal: 0
        }
      };
      setMetrics(mappedData);
    } catch (error) {
      console.error('Error fetching metrics:', error);
    }
  };

  useEffect(() => {
    fetchMetrics();
    const interval = setInterval(fetchMetrics, 30000); // Atualiza a cada 30 segundos
    return () => clearInterval(interval);
  }, []);

  return (
    <Box sx={{ p: 3 }}>
      <Typography variant="h4" gutterBottom>
        Feature Store Monitoring
      </Typography>

      <Grid container spacing={3}>
        {/* Métricas Principais */}
        <Grid item xs={12} md={8}>
          <Grid container spacing={2}>
            <Grid item xs={12} sm={6} md={4}>
              <Card 
                sx={{ 
                  background: 'linear-gradient(45deg, rgba(0, 242, 255, 0.05), rgba(255, 0, 242, 0.05))',
                  border: '1px solid rgba(0, 242, 255, 0.1)',
                  '&:hover': {
                    border: '1px solid rgba(0, 242, 255, 0.2)',
                    boxShadow: '0 0 20px rgba(0, 242, 255, 0.1)',
                  },
                }}
              >
                <CardContent>
                  <Typography color="textSecondary" gutterBottom>
                    Features Processadas
                  </Typography>
                  <Typography variant="h3" component="div" color="primary">
                    {metrics.processedFeatures}
                  </Typography>
                  <Typography variant="body2" color="textSecondary">
                    de {metrics.totalFeatures} total
                  </Typography>
                  <LinearProgress 
                    variant="determinate" 
                    value={(metrics.processedFeatures / metrics.totalFeatures) * 100}
                    sx={{
                      mt: 2,
                      background: 'rgba(0, 242, 255, 0.1)',
                      '& .MuiLinearProgress-bar': {
                        background: 'linear-gradient(45deg, #00f2ff 30%, #ff00f2 90%)',
                      },
                    }}
                  />
                </CardContent>
              </Card>
            </Grid>

            <Grid item xs={12} sm={6} md={4}>
              <Card 
                sx={{ 
                  background: 'linear-gradient(45deg, rgba(0, 242, 255, 0.05), rgba(255, 0, 242, 0.05))',
                  border: '1px solid rgba(0, 242, 255, 0.1)',
                  '&:hover': {
                    border: '1px solid rgba(0, 242, 255, 0.2)',
                    boxShadow: '0 0 20px rgba(0, 242, 255, 0.1)',
                  },
                }}
              >
                <CardContent>
                  <Typography color="textSecondary" gutterBottom>
                    Taxa de Processamento
                  </Typography>
                  <Typography variant="h3" component="div" color="primary">
                    {metrics.processingRate}
                  </Typography>
                  <Typography variant="body2" color="textSecondary">
                    features/segundo
                  </Typography>
                </CardContent>
              </Card>
            </Grid>

            <Grid item xs={12} sm={6} md={4}>
              <Card 
                sx={{ 
                  background: 'linear-gradient(45deg, rgba(0, 242, 255, 0.05), rgba(255, 0, 242, 0.05))',
                  border: '1px solid rgba(0, 242, 255, 0.1)',
                  '&:hover': {
                    border: '1px solid rgba(0, 242, 255, 0.2)',
                    boxShadow: '0 0 20px rgba(0, 242, 255, 0.1)',
                  },
                }}
              >
                <CardContent>
                  <Typography color="textSecondary" gutterBottom>
                    Último Processamento
                  </Typography>
                  <Typography variant="h6" component="div" color="primary">
                    {metrics.lastProcessingTime ? 
                      new Date(metrics.lastProcessingTime).toLocaleString() :
                      'N/A'}
                  </Typography>
                </CardContent>
              </Card>
            </Grid>

            {/* Distribuição de Tipos */}
            <Grid item xs={12}>
              <Card 
                sx={{ 
                  background: 'linear-gradient(45deg, rgba(0, 242, 255, 0.05), rgba(255, 0, 242, 0.05))',
                  border: '1px solid rgba(0, 242, 255, 0.1)',
                  '&:hover': {
                    border: '1px solid rgba(0, 242, 255, 0.2)',
                    boxShadow: '0 0 20px rgba(0, 242, 255, 0.1)',
                  },
                }}
              >
                <CardContent>
                  <Typography variant="h6" gutterBottom>
                    Distribuição de Tipos de Features
                  </Typography>
                  <Stack spacing={2}>
                    <Box>
                      <Typography variant="body2" color="textSecondary">
                        Numéricas
                      </Typography>
                      <LinearProgress 
                        variant="determinate" 
                        value={(metrics.featureStats.numerical / metrics.totalFeatures) * 100}
                        sx={{
                          background: 'rgba(0, 242, 255, 0.1)',
                          '& .MuiLinearProgress-bar': {
                            background: 'linear-gradient(45deg, #00f2ff 30%, #ff00f2 90%)',
                          },
                        }}
                      />
                    </Box>
                    <Box>
                      <Typography variant="body2" color="textSecondary">
                        Categóricas
                      </Typography>
                      <LinearProgress 
                        variant="determinate" 
                        value={(metrics.featureStats.categorical / metrics.totalFeatures) * 100}
                        sx={{
                          background: 'rgba(0, 242, 255, 0.1)',
                          '& .MuiLinearProgress-bar': {
                            background: 'linear-gradient(45deg, #ff00f2 30%, #00f2ff 90%)',
                          },
                        }}
                      />
                    </Box>
                    <Box>
                      <Typography variant="body2" color="textSecondary">
                        Temporais
                      </Typography>
                      <LinearProgress 
                        variant="determinate" 
                        value={(metrics.featureStats.temporal / metrics.totalFeatures) * 100}
                        sx={{
                          background: 'rgba(0, 242, 255, 0.1)',
                          '& .MuiLinearProgress-bar': {
                            background: 'linear-gradient(45deg, #00f2ff 60%, #ff00f2 90%)',
                          },
                        }}
                      />
                    </Box>
                  </Stack>
                </CardContent>
              </Card>
            </Grid>
          </Grid>
        </Grid>

        {/* Lista de Atividades Recentes */}
        <Grid item xs={12} md={4}>
          <Paper 
            sx={{ 
              p: 2,
              background: 'linear-gradient(45deg, rgba(0, 242, 255, 0.05), rgba(255, 0, 242, 0.05))',
              border: '1px solid rgba(0, 242, 255, 0.1)',
              '&:hover': {
                border: '1px solid rgba(0, 242, 255, 0.2)',
                boxShadow: '0 0 20px rgba(0, 242, 255, 0.1)',
              },
            }}
          >
            <Typography variant="h6" gutterBottom>
              Atividade Recente
            </Typography>
            <List>
              {metrics.recentActivity.map((activity, index) => (
                <React.Fragment key={index}>
                  <ListItem>
                    <ListItemText
                      primary={
                        <Typography variant="body2" color="primary">
                          {activity.action}
                        </Typography>
                      }
                      secondary={
                        <Typography variant="caption" color="textSecondary">
                          {new Date(activity.timestamp).toLocaleString()}
                        </Typography>
                      }
                    />
                  </ListItem>
                  {index < metrics.recentActivity.length - 1 && (
                    <Divider 
                      sx={{ 
                        background: 'linear-gradient(45deg, #00f2ff 30%, #ff00f2 90%)',
                        opacity: 0.2 
                      }} 
                    />
                  )}
                </React.Fragment>
              ))}
            </List>
          </Paper>
        </Grid>
      </Grid>
    </Box>
  );
};

export default Monitoring;
