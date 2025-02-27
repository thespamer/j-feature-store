import React, { useState } from 'react';
import {
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  Button,
  TextField,
  Typography,
  Box,
  CircularProgress,
  Alert,
} from '@mui/material';
import { DateTimePicker } from '@mui/x-date-pickers/DateTimePicker';
import { AdapterDateFns } from '@mui/x-date-pickers/AdapterDateFns';
import { LocalizationProvider } from '@mui/x-date-pickers/LocalizationProvider';
import { format } from 'date-fns';
import CodeEditor from '@uiw/react-textarea-code-editor';

const API_URL = 'http://localhost:8000/api/v1';

const ExportDatasetDialog = ({ open, onClose, featureGroupId }) => {
  const [startTime, setStartTime] = useState(new Date());
  const [endTime, setEndTime] = useState(new Date());
  const [entityData, setEntityData] = useState('{\n  "entity_id": ["customer1", "customer2"],\n  "timestamp": ["2025-01-01T00:00:00", "2025-01-02T00:00:00"]\n}');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [downloadUrl, setDownloadUrl] = useState(null);

  const handleExport = async () => {
    try {
      setLoading(true);
      setError(null);
      setDownloadUrl(null);

      let entityDf;
      try {
        entityDf = JSON.parse(entityData);
      } catch (e) {
        throw new Error('Entity data deve ser um JSON válido');
      }

      const response = await fetch(`${API_URL}/feature-groups/${featureGroupId}/training-dataset`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          start_time: format(startTime, "yyyy-MM-dd'T'HH:mm:ss"),
          end_time: format(endTime, "yyyy-MM-dd'T'HH:mm:ss"),
          entity_df: entityDf,
        }),
      });

      if (!response.ok) {
        throw new Error('Erro ao exportar dataset');
      }

      const blob = await response.blob();
      const url = window.URL.createObjectURL(blob);
      setDownloadUrl(url);
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  const handleDownload = () => {
    if (downloadUrl) {
      const link = document.createElement('a');
      link.href = downloadUrl;
      link.download = `training_dataset_${format(new Date(), 'yyyyMMdd_HHmmss')}.csv`;
      document.body.appendChild(link);
      link.click();
      document.body.removeChild(link);
      window.URL.revokeObjectURL(downloadUrl);
    }
  };

  return (
    <LocalizationProvider dateAdapter={AdapterDateFns}>
      <Dialog open={open} onClose={onClose} maxWidth="md" fullWidth>
        <DialogTitle>Exportar Dataset de Treinamento</DialogTitle>
        <DialogContent>
          {error && (
            <Alert severity="error" sx={{ mb: 2 }}>
              {error}
            </Alert>
          )}

          <Box sx={{ mb: 3 }}>
            <Typography variant="subtitle2" gutterBottom>
              Período do Dataset
            </Typography>
            <Box display="flex" gap={2}>
              <DateTimePicker
                label="Data Inicial"
                value={startTime}
                onChange={setStartTime}
                renderInput={(params) => <TextField {...params} />}
              />
              <DateTimePicker
                label="Data Final"
                value={endTime}
                onChange={setEndTime}
                renderInput={(params) => <TextField {...params} />}
              />
            </Box>
          </Box>

          <Box sx={{ mb: 3 }}>
            <Typography variant="subtitle2" gutterBottom>
              Dados das Entidades (JSON)
            </Typography>
            <Typography variant="caption" color="textSecondary" display="block" gutterBottom>
              Formato: {"{'entity_id': ['id1', 'id2'], 'timestamp': ['2025-01-01', '2025-01-02']}"}
            </Typography>
            <Box sx={{ border: '1px solid #ccc', borderRadius: 1 }}>
              <CodeEditor
                value={entityData}
                language="json"
                placeholder="Enter entity data in JSON format"
                onChange={(e) => setEntityData(e.target.value)}
                padding={15}
                style={{
                  fontSize: 12,
                  backgroundColor: '#f5f5f5',
                  fontFamily: 'ui-monospace,SFMono-Regular,SF Mono,Consolas,Liberation Mono,Menlo,monospace',
                }}
              />
            </Box>
          </Box>

          {downloadUrl && (
            <Alert severity="success" action={
              <Button color="inherit" size="small" onClick={handleDownload}>
                Download
              </Button>
            }>
              Dataset gerado com sucesso!
            </Alert>
          )}
        </DialogContent>
        <DialogActions>
          <Button onClick={onClose} color="inherit">
            Fechar
          </Button>
          <Button
            onClick={handleExport}
            color="primary"
            disabled={loading}
            startIcon={loading && <CircularProgress size={20} />}
          >
            Exportar
          </Button>
        </DialogActions>
      </Dialog>
    </LocalizationProvider>
  );
};

export default ExportDatasetDialog;
