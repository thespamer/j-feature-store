import React, { useState } from 'react';
import {
  Card,
  CardContent,
  Typography,
  IconButton,
  Box,
  Chip,
  Menu,
  MenuItem,
  Button,
} from '@mui/material';
import MoreVertIcon from '@mui/icons-material/MoreVert';
import EditIcon from '@mui/icons-material/Edit';
import DeleteIcon from '@mui/icons-material/Delete';
import FeaturesIcon from '@mui/icons-material/Extension';
import ManageGroupFeaturesDialog from './ManageGroupFeaturesDialog';

const FeatureGroupCard = ({ group, onEdit, onDelete, onUpdate }) => {
  const [anchorEl, setAnchorEl] = useState(null);
  const [manageFeaturesOpen, setManageFeaturesOpen] = useState(false);

  const handleMenuClick = (event) => {
    setAnchorEl(event.currentTarget);
  };

  const handleMenuClose = () => {
    setAnchorEl(null);
  };

  const handleEditClick = () => {
    handleMenuClose();
    onEdit(group);
  };

  const handleDeleteClick = () => {
    handleMenuClose();
    onDelete(group);
  };

  const handleManageFeaturesClick = () => {
    handleMenuClose();
    setManageFeaturesOpen(true);
  };

  return (
    <>
      <Card sx={{ height: '100%', display: 'flex', flexDirection: 'column' }}>
        <CardContent sx={{ flexGrow: 1 }}>
          <Box display="flex" justifyContent="space-between" alignItems="flex-start">
            <Typography variant="h6" component="h2" gutterBottom>
              {group.name}
            </Typography>
            <IconButton onClick={handleMenuClick} size="small">
              <MoreVertIcon />
            </IconButton>
          </Box>
          <Typography color="textSecondary" gutterBottom>
            {group.description}
          </Typography>
          <Box mt={2}>
            <Typography variant="subtitle2" gutterBottom>
              Entity Type: {group.entity_type}
            </Typography>
            <Typography variant="subtitle2" gutterBottom>
              Features: {group.features ? group.features.length : 0}
            </Typography>
          </Box>
          {group.tags && group.tags.length > 0 && (
            <Box mt={2} display="flex" gap={1} flexWrap="wrap">
              {group.tags.map((tag) => (
                <Chip key={tag} label={tag} size="small" />
              ))}
            </Box>
          )}
        </CardContent>
        <Box p={2} display="flex" justifyContent="flex-end">
          <Button
            startIcon={<FeaturesIcon />}
            onClick={handleManageFeaturesClick}
            color="primary"
            size="small"
          >
            Gerenciar Features
          </Button>
        </Box>
      </Card>

      <Menu
        anchorEl={anchorEl}
        open={Boolean(anchorEl)}
        onClose={handleMenuClose}
      >
        <MenuItem onClick={handleEditClick}>
          <EditIcon fontSize="small" sx={{ mr: 1 }} />
          Editar
        </MenuItem>
        <MenuItem onClick={handleDeleteClick}>
          <DeleteIcon fontSize="small" sx={{ mr: 1 }} />
          Excluir
        </MenuItem>
        <MenuItem onClick={handleManageFeaturesClick}>
          <FeaturesIcon fontSize="small" sx={{ mr: 1 }} />
          Gerenciar Features
        </MenuItem>
      </Menu>

      <ManageGroupFeaturesDialog
        open={manageFeaturesOpen}
        onClose={() => setManageFeaturesOpen(false)}
        group={group}
        onUpdate={onUpdate}
      />
    </>
  );
};

export default FeatureGroupCard;
