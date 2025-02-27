import React from 'react';
import { 
  Card, 
  CardContent,
  Typography,
  Box,
  Chip,
  IconButton,
  Menu,
  MenuItem
} from '@mui/material';
import MoreVertIcon from '@mui/icons-material/MoreVert';
import { format } from 'date-fns';

const FeatureGroupCard = ({ group, onEdit, onDelete, onViewFeatures }) => {
  const [anchorEl, setAnchorEl] = React.useState(null);

  const handleMenuClick = (event) => {
    setAnchorEl(event.currentTarget);
  };

  const handleMenuClose = () => {
    setAnchorEl(null);
  };

  const handleAction = (action) => {
    handleMenuClose();
    switch (action) {
      case 'edit':
        onEdit(group);
        break;
      case 'delete':
        onDelete(group);
        break;
      case 'viewFeatures':
        onViewFeatures(group);
        break;
      default:
        break;
    }
  };

  if (!group) return null;

  return (
    <Card>
      <CardContent>
        <Box display="flex" justifyContent="space-between" alignItems="flex-start">
          <Typography variant="h6" gutterBottom>
            {group.name}
          </Typography>
          <IconButton size="small" onClick={handleMenuClick}>
            <MoreVertIcon />
          </IconButton>
          <Menu
            anchorEl={anchorEl}
            open={Boolean(anchorEl)}
            onClose={handleMenuClose}
          >
            <MenuItem onClick={() => handleAction('edit')}>Edit</MenuItem>
            <MenuItem onClick={() => handleAction('viewFeatures')}>View Features</MenuItem>
            <MenuItem onClick={() => handleAction('delete')}>Delete</MenuItem>
          </Menu>
        </Box>
        <Typography variant="body2" color="textSecondary" paragraph>
          {group.description || 'No description'}
        </Typography>
        <Typography variant="body2">
          Entity Type: {group.entity_type || "Not specified"}
        </Typography>
        <Typography variant="body2">
          Features: {(group.features || []).length}
        </Typography>
        <Typography variant="body2">
          Owner: {group.owner || "Not assigned"}
        </Typography>
        <Typography variant="body2">
          Update Frequency: {group.frequency || "Not specified"}
        </Typography>
        <Typography variant="body2">
          Last Updated: {group.updated_at ? format(new Date(group.updated_at), 'PPpp') : 'Never'}
        </Typography>
        <Box mt={2}>
          <Typography variant="body2" component="span" mr={1}>
            Status:
          </Typography>
          <Chip
            label={group.status || 'active'}
            size="small"
            color={group.status === 'deprecated' ? 'error' : 'success'}
          />
        </Box>
        <Box mt={2}>
          {(group.tags || []).map((tag, index) => (
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
