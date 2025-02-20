import React, { useState, useEffect } from 'react';
import {
  Box,
  Grid,
  Card,
  CardContent,
  Typography,
  Paper,
  Stack,
  IconButton,
  Tooltip,
  LinearProgress,
} from '@mui/material';
import StorageIcon from '@mui/icons-material/Storage';
import GroupWorkIcon from '@mui/icons-material/GroupWork';
import SpeedIcon from '@mui/icons-material/Speed';
import UpdateIcon from '@mui/icons-material/Update';
import { useNavigate } from 'react-router-dom';

const DashboardCard = ({ title, value, icon, subtitle, onClick, gradient }) => (
  <Card 
    sx={{ 
      cursor: onClick ? 'pointer' : 'default',
      background: 'linear-gradient(45deg, rgba(0, 242, 255, 0.05), rgba(255, 0, 242, 0.05))',
      border: '1px solid rgba(0, 242, 255, 0.1)',
      transition: 'all 0.3s ease-in-out',
      '&:hover': {
        border: '1px solid rgba(0, 242, 255, 0.2)',
        boxShadow: '0 0 20px rgba(0, 242, 255, 0.1)',
        transform: onClick ? 'translateY(-4px)' : 'none',
      },
    }}
    onClick={onClick}
  >
    <CardContent>
      <Stack direction="row" justifyContent="space-between" alignItems="center" mb={2}>
        <Typography color="textSecondary">
          {title}
        </Typography>
        <IconButton 
          sx={{
            background: gradient,
            '&:hover': {
              background: gradient,
              opacity: 0.8,
            },
          }}
        >
          {icon}
        </IconButton>
      </Stack>
      <Typography variant="h4" component="div" color="primary" gutterBottom>
        {value}
      </Typography>
      {subtitle && (
        <Typography variant="body2" color="textSecondary">
          {subtitle}
        </Typography>
      )}
    </CardContent>
  </Card>
);

const Dashboard = () => {
  const navigate = useNavigate();
  const [stats, setStats] = useState({
    features: {
      total: 0,
      active: 0,
      types: {
        numerical: 0,
        categorical: 0,
        temporal: 0
      }
    },
    groups: {
      total: 0,
      byFrequency: {
        daily: 0,
        hourly: 0,
        weekly: 0,
        monthly: 0
      }
    },
    processing: {
      rate: 0,
      lastUpdate: null
    }
  });

  const fetchStats = async () => {
    try {
      // Buscar features
      const featuresResponse = await fetch('http://localhost:8000/api/v1/features');
      const features = await featuresResponse.json();

      // Buscar grupos
      const groupsResponse = await fetch('http://localhost:8000/api/v1/feature-groups');
      const groups = await groupsResponse.json();

      // Buscar métricas de processamento
      const metricsResponse = await fetch('http://localhost:8000/api/v1/monitoring/metrics');
      const metrics = await metricsResponse.json();

      // Atualizar estatísticas
      setStats({
        features: {
          total: features.length,
          active: features.filter(f => f.active).length,
          types: {
            numerical: features.filter(f => f.type === 'numerical').length,
            categorical: features.filter(f => f.type === 'categorical').length,
            temporal: features.filter(f => f.type === 'temporal').length
          }
        },
        groups: {
          total: groups.length,
          byFrequency: {
            daily: groups.filter(g => g.frequency === 'daily').length,
            hourly: groups.filter(g => g.frequency === 'hourly').length,
            weekly: groups.filter(g => g.frequency === 'weekly').length,
            monthly: groups.filter(g => g.frequency === 'monthly').length
          }
        },
        processing: {
          rate: metrics.processingRate,
          lastUpdate: metrics.lastProcessingTime
        }
      });
    } catch (error) {
      console.error('Error fetching dashboard stats:', error);
    }
  };

  useEffect(() => {
    fetchStats();
    const interval = setInterval(fetchStats, 30000);
    return () => clearInterval(interval);
  }, []);

  return (
    <Box sx={{ p: 3 }}>
      <Typography variant="h4" gutterBottom>
        Dashboard
      </Typography>

      <Grid container spacing={3}>
        {/* Cards Principais */}
        <Grid item xs={12} sm={6} md={3}>
          <DashboardCard
            title="Total Features"
            value={stats.features.total}
            icon={<StorageIcon />}
            subtitle={`${stats.features.active} ativas`}
            onClick={() => navigate('/features')}
            gradient="linear-gradient(45deg, #00f2ff 30%, #ff00f2 90%)"
          />
        </Grid>
        <Grid item xs={12} sm={6} md={3}>
          <DashboardCard
            title="Grupos de Features"
            value={stats.groups.total}
            icon={<GroupWorkIcon />}
            subtitle="Ver todos os grupos"
            onClick={() => navigate('/feature-groups')}
            gradient="linear-gradient(45deg, #ff00f2 30%, #00f2ff 90%)"
          />
        </Grid>
        <Grid item xs={12} sm={6} md={3}>
          <DashboardCard
            title="Taxa de Processamento"
            value={`${stats.processing.rate}/s`}
            icon={<SpeedIcon />}
            subtitle="Features por segundo"
            onClick={() => navigate('/monitoring')}
            gradient="linear-gradient(45deg, #00f2ff 60%, #ff00f2 90%)"
          />
        </Grid>
        <Grid item xs={12} sm={6} md={3}>
          <DashboardCard
            title="Última Atualização"
            value={stats.processing.lastUpdate ? 
              new Date(stats.processing.lastUpdate).toLocaleTimeString() :
              'N/A'
            }
            icon={<UpdateIcon />}
            subtitle={stats.processing.lastUpdate ? 
              new Date(stats.processing.lastUpdate).toLocaleDateString() :
              'Sem atualizações'
            }
            gradient="linear-gradient(45deg, #ff00f2 60%, #00f2ff 90%)"
          />
        </Grid>

        {/* Distribuição de Tipos de Features */}
        <Grid item xs={12} md={6}>
          <Paper 
            sx={{ 
              p: 3,
              background: 'linear-gradient(45deg, rgba(0, 242, 255, 0.05), rgba(255, 0, 242, 0.05))',
              border: '1px solid rgba(0, 242, 255, 0.1)',
              '&:hover': {
                border: '1px solid rgba(0, 242, 255, 0.2)',
                boxShadow: '0 0 20px rgba(0, 242, 255, 0.1)',
              },
            }}
          >
            <Typography variant="h6" gutterBottom>
              Tipos de Features
            </Typography>
            <Stack spacing={2}>
              <Box>
                <Stack direction="row" justifyContent="space-between">
                  <Typography variant="body2" color="textSecondary">
                    Numéricas
                  </Typography>
                  <Typography variant="body2" color="primary">
                    {stats.features.types.numerical}
                  </Typography>
                </Stack>
                <LinearProgress 
                  variant="determinate" 
                  value={(stats.features.types.numerical / stats.features.total) * 100}
                  sx={{
                    mt: 1,
                    background: 'rgba(0, 242, 255, 0.1)',
                    '& .MuiLinearProgress-bar': {
                      background: 'linear-gradient(45deg, #00f2ff 30%, #ff00f2 90%)',
                    },
                  }}
                />
              </Box>
              <Box>
                <Stack direction="row" justifyContent="space-between">
                  <Typography variant="body2" color="textSecondary">
                    Categóricas
                  </Typography>
                  <Typography variant="body2" color="primary">
                    {stats.features.types.categorical}
                  </Typography>
                </Stack>
                <LinearProgress 
                  variant="determinate" 
                  value={(stats.features.types.categorical / stats.features.total) * 100}
                  sx={{
                    mt: 1,
                    background: 'rgba(0, 242, 255, 0.1)',
                    '& .MuiLinearProgress-bar': {
                      background: 'linear-gradient(45deg, #ff00f2 30%, #00f2ff 90%)',
                    },
                  }}
                />
              </Box>
              <Box>
                <Stack direction="row" justifyContent="space-between">
                  <Typography variant="body2" color="textSecondary">
                    Temporais
                  </Typography>
                  <Typography variant="body2" color="primary">
                    {stats.features.types.temporal}
                  </Typography>
                </Stack>
                <LinearProgress 
                  variant="determinate" 
                  value={(stats.features.types.temporal / stats.features.total) * 100}
                  sx={{
                    mt: 1,
                    background: 'rgba(0, 242, 255, 0.1)',
                    '& .MuiLinearProgress-bar': {
                      background: 'linear-gradient(45deg, #00f2ff 60%, #ff00f2 90%)',
                    },
                  }}
                />
              </Box>
            </Stack>
          </Paper>
        </Grid>

        {/* Distribuição de Frequências */}
        <Grid item xs={12} md={6}>
          <Paper 
            sx={{ 
              p: 3,
              background: 'linear-gradient(45deg, rgba(0, 242, 255, 0.05), rgba(255, 0, 242, 0.05))',
              border: '1px solid rgba(0, 242, 255, 0.1)',
              '&:hover': {
                border: '1px solid rgba(0, 242, 255, 0.2)',
                boxShadow: '0 0 20px rgba(0, 242, 255, 0.1)',
              },
            }}
          >
            <Typography variant="h6" gutterBottom>
              Frequência de Atualização
            </Typography>
            <Stack spacing={2}>
              <Box>
                <Stack direction="row" justifyContent="space-between">
                  <Typography variant="body2" color="textSecondary">
                    Horária
                  </Typography>
                  <Typography variant="body2" color="primary">
                    {stats.groups.byFrequency.hourly}
                  </Typography>
                </Stack>
                <LinearProgress 
                  variant="determinate" 
                  value={(stats.groups.byFrequency.hourly / stats.groups.total) * 100}
                  sx={{
                    mt: 1,
                    background: 'rgba(0, 242, 255, 0.1)',
                    '& .MuiLinearProgress-bar': {
                      background: 'linear-gradient(45deg, #00f2ff 30%, #ff00f2 90%)',
                    },
                  }}
                />
              </Box>
              <Box>
                <Stack direction="row" justifyContent="space-between">
                  <Typography variant="body2" color="textSecondary">
                    Diária
                  </Typography>
                  <Typography variant="body2" color="primary">
                    {stats.groups.byFrequency.daily}
                  </Typography>
                </Stack>
                <LinearProgress 
                  variant="determinate" 
                  value={(stats.groups.byFrequency.daily / stats.groups.total) * 100}
                  sx={{
                    mt: 1,
                    background: 'rgba(0, 242, 255, 0.1)',
                    '& .MuiLinearProgress-bar': {
                      background: 'linear-gradient(45deg, #ff00f2 30%, #00f2ff 90%)',
                    },
                  }}
                />
              </Box>
              <Box>
                <Stack direction="row" justifyContent="space-between">
                  <Typography variant="body2" color="textSecondary">
                    Semanal
                  </Typography>
                  <Typography variant="body2" color="primary">
                    {stats.groups.byFrequency.weekly}
                  </Typography>
                </Stack>
                <LinearProgress 
                  variant="determinate" 
                  value={(stats.groups.byFrequency.weekly / stats.groups.total) * 100}
                  sx={{
                    mt: 1,
                    background: 'rgba(0, 242, 255, 0.1)',
                    '& .MuiLinearProgress-bar': {
                      background: 'linear-gradient(45deg, #00f2ff 60%, #ff00f2 90%)',
                    },
                  }}
                />
              </Box>
              <Box>
                <Stack direction="row" justifyContent="space-between">
                  <Typography variant="body2" color="textSecondary">
                    Mensal
                  </Typography>
                  <Typography variant="body2" color="primary">
                    {stats.groups.byFrequency.monthly}
                  </Typography>
                </Stack>
                <LinearProgress 
                  variant="determinate" 
                  value={(stats.groups.byFrequency.monthly / stats.groups.total) * 100}
                  sx={{
                    mt: 1,
                    background: 'rgba(0, 242, 255, 0.1)',
                    '& .MuiLinearProgress-bar': {
                      background: 'linear-gradient(45deg, #ff00f2 60%, #00f2ff 90%)',
                    },
                  }}
                />
              </Box>
            </Stack>
          </Paper>
        </Grid>
      </Grid>
    </Box>
  );
};

export default Dashboard;
