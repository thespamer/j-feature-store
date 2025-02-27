import React, { useState } from 'react';
import {
  Card,
  CardContent,
  Typography,
  IconButton,
  Box,
  Menu,
  MenuItem,
  Button,
  Chip,
} from '@mui/material';
import MoreVertIcon from '@mui/icons-material/MoreVert';
import DeleteIcon from '@mui/icons-material/Delete';
import FeaturesIcon from '@mui/icons-material/Extension';
import KeyboardArrowUpIcon from '@mui/icons-material/KeyboardArrowUp';
import KeyboardArrowDownIcon from '@mui/icons-material/KeyboardArrowDown';
import DownloadIcon from '@mui/icons-material/Download';
import ManageGroupFeaturesDialog from './ManageGroupFeaturesDialog';
import PipelineList from './PipelineList';
import ExportDatasetDialog from './ExportDatasetDialog';

const FeatureGroupCard = ({ group, onUpdate, onDelete }) => {
  const [anchorEl, setAnchorEl] = useState(null);
  const [manageFeaturesOpen, setManageFeaturesOpen] = useState(false);
  const [showPipelines, setShowPipelines] = useState(false);
  const [exportDialogOpen, setExportDialogOpen] = useState(false);

  const handleMenuClick = (event) => {
    setAnchorEl(event.currentTarget);
  };

  const handleMenuClose = () => {
    setAnchorEl(null);
  };

  const handleDeleteClick = () => {
    handleMenuClose();
    onDelete(group);
  };

  return (
    <>
      <Card sx={{ height: '100%', display: 'flex', flexDirection: 'column' }}>
        <CardContent sx={{ flexGrow: 1 }}>
          <Box display="flex" justifyContent="space-between" alignItems="flex-start">
            <Typography variant="h5" component="div">
              {group.name}
            </Typography>
            <IconButton onClick={handleMenuClick} size="small">
              <MoreVertIcon />
            </IconButton>
          </Box>

          <Typography color="text.secondary" gutterBottom>
            {group.description}
          </Typography>

          <Typography variant="body2" color="text.secondary">
            Entity Type: {group.entity_type}
          </Typography>
          <Typography variant="body2" color="text.secondary">
            Features: {group.features ? group.features.length : 0}
          </Typography>

          {group.tags && group.tags.length > 0 && (
            <Box sx={{ mt: 1 }}>
              {group.tags.map((tag) => (
                <Chip key={tag} label={tag} size="small" sx={{ mr: 0.5 }} />
              ))}
            </Box>
          )}

          <Box sx={{ mt: 2, display: 'flex', gap: 1, flexWrap: 'wrap' }}>
            <Button
              startIcon={<FeaturesIcon />}
              onClick={() => setManageFeaturesOpen(true)}
              color="primary"
              variant="outlined"
              size="small"
            >
              Gerenciar Features
            </Button>
            
            <Button
              startIcon={<DownloadIcon />}
              onClick={() => setExportDialogOpen(true)}
              color="primary"
              variant="outlined"
              size="small"
            >
              Exportar Dataset
            </Button>

            <Button
              startIcon={showPipelines ? <KeyboardArrowUpIcon /> : <KeyboardArrowDownIcon />}
              onClick={() => setShowPipelines(!showPipelines)}
              color="primary"
              variant="outlined"
              size="small"
            >
              {showPipelines ? 'Ocultar Pipelines' : 'Mostrar Pipelines'}
            </Button>
          </Box>

          {showPipelines && (
            <Box sx={{ mt: 2 }}>
              <PipelineList featureGroupId={group.id} />
            </Box>
          )}
        </CardContent>

        <Menu
          anchorEl={anchorEl}
          open={Boolean(anchorEl)}
          onClose={handleMenuClose}
        >
          <MenuItem onClick={handleDeleteClick}>
            <DeleteIcon fontSize="small" sx={{ mr: 1 }} />
            Excluir
          </MenuItem>
        </Menu>
      </Card>

      <ManageGroupFeaturesDialog
        open={manageFeaturesOpen}
        onClose={() => setManageFeaturesOpen(false)}
        group={group}
        onUpdate={onUpdate}
      />

      <ExportDatasetDialog
        open={exportDialogOpen}
        onClose={() => setExportDialogOpen(false)}
        featureGroupId={group.id}
      />
    </>
  );
};

export default FeatureGroupCard;
