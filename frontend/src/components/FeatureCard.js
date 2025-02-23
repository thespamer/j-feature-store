import React from 'react';
import { 
  Card, 
  CardContent,
  Typography,
  Box,
  Chip,
  Divider
} from '@mui/material';

const FeatureCard = ({ feature }) => {
  if (!feature) return null;

  const getTypeColor = (type) => {
    switch (type.toLowerCase()) {
      case 'float':
      case 'numerical':
        return '#4CAF50';
      case 'string':
      case 'categorical':
        return '#2196F3';
      case 'datetime':
      case 'temporal':
        return '#9C27B0';
      default:
        return '#757575';
    }
  };

  const getTagColor = (tag) => {
    switch (tag.toLowerCase()) {
      case 'financial':
        return '#00C853';
      case 'customer':
        return '#2962FF';
      case 'transaction':
        return '#FF6D00';
      case 'temporal':
        return '#6200EA';
      case 'categorical':
        return '#00BFA5';
      default:
        return '#757575';
    }
  };

  return (
    <Card sx={{ 
      height: '100%',
      display: 'flex',
      flexDirection: 'column',
      transition: 'transform 0.2s, box-shadow 0.2s',
      '&:hover': {
        transform: 'translateY(-4px)',
        boxShadow: '0 4px 20px rgba(0,0,0,0.1)'
      }
    }}>
      <CardContent sx={{ flexGrow: 1 }}>
        <Typography variant="h6" gutterBottom sx={{ 
          color: '#1A237E',
          fontWeight: 600
        }}>
          {feature.name}
        </Typography>
        <Typography variant="body2" color="textSecondary" paragraph>
          {feature.description || 'No description'}
        </Typography>
        
        <Divider sx={{ my: 1.5 }} />
        
        <Box display="flex" alignItems="center" mb={1}>
          <Typography variant="body2" color="textSecondary" sx={{ mr: 1 }}>
            Type:
          </Typography>
          <Chip
            label={feature.type}
            size="small"
            sx={{
              backgroundColor: getTypeColor(feature.type),
              color: 'white',
              fontWeight: 500
            }}
          />
        </Box>

        <Typography variant="body2" color="textSecondary" gutterBottom>
          Entity ID: {feature.entity_id || 'Not specified'}
        </Typography>

        <Typography variant="body2" color="textSecondary" gutterBottom>
          Group ID: {feature.feature_group_id || 'Not specified'}
        </Typography>

        <Box mt={2}>
          <Typography variant="body2" color="textSecondary" gutterBottom>
            Tags:
          </Typography>
          <Box display="flex" flexWrap="wrap" gap={0.5}>
            {feature.tags && feature.tags.map((tag, index) => (
              <Chip
                key={index}
                label={tag}
                size="small"
                sx={{
                  backgroundColor: getTagColor(tag),
                  color: 'white',
                  fontWeight: 500
                }}
              />
            ))}
            {(!feature.tags || feature.tags.length === 0) && (
              <Typography variant="body2" color="textSecondary">
                No tags
              </Typography>
            )}
          </Box>
        </Box>
      </CardContent>
    </Card>
  );
};

export default FeatureCard;
