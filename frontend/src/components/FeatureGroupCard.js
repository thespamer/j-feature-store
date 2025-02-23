import React from 'react';
import { 
  Card, 
  CardContent,
  Typography,
  Box,
  Chip
} from '@mui/material';

const FeatureGroupCard = ({ group }) => {
  if (!group) return null;

  return (
    <Card>
      <CardContent>
        <Typography variant="h6" gutterBottom>
          {group.name}
        </Typography>
        <Typography variant="body2" color="textSecondary" paragraph>
          {group.description || 'No description'}
        </Typography>
        <Typography variant="body2" color="textSecondary">
          Entity ID: {group.entity_id || 'Not specified'}
        </Typography>
        <Box mt={2}>
          {group.tags && group.tags.map((tag, index) => (
            <Chip
              key={index}
              label={tag}
              size="small"
              style={{ margin: '0 4px 4px 0' }}
            />
          ))}
        </Box>
      </CardContent>
    </Card>
  );
};

export default FeatureGroupCard;
