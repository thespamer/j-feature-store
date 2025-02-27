import React, { useState } from 'react';
import {
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  Button,
  TextField,
  FormControl,
  InputLabel,
  Select,
  MenuItem,
  Box,
  Typography,
} from '@mui/material';
import CodeEditor from '@uiw/react-textarea-code-editor';

const API_URL = 'http://localhost:8000/api/v1';

const transformationTypes = [
  { value: 'sql', label: 'SQL' },
  { value: 'python', label: 'Python' },
  { value: 'pandas', label: 'Pandas' },
];

const scheduleIntervals = [
  { value: 'hourly', label: 'Horário' },
  { value: 'daily', label: 'Diário' },
  { value: 'weekly', label: 'Semanal' },
  { value: 'monthly', label: 'Mensal' },
  { value: 'custom', label: 'Customizado' },
];

const CreatePipelineDialog = ({ open, onClose, featureGroupId, onPipelineCreated }) => {
  const [name, setName] = useState('');
  const [transformationType, setTransformationType] = useState('sql');
  const [code, setCode] = useState('');
  const [scheduleInterval, setScheduleInterval] = useState('daily');
  const [customSchedule, setCustomSchedule] = useState('');
  const [error, setError] = useState(null);

  const handleSubmit = async () => {
    try {
      const response = await fetch(`${API_URL}/pipelines`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          name,
          feature_group_id: featureGroupId,
          transformation_type: transformationType,
          code,
          schedule_interval: scheduleInterval,
          custom_schedule: scheduleInterval === 'custom' ? customSchedule : null,
        }),
      });

      if (!response.ok) {
        throw new Error('Erro ao criar pipeline');
      }

      const pipeline = await response.json();
      onPipelineCreated(pipeline);
      onClose();
    } catch (error) {
      setError(error.message);
    }
  };

  return (
    <Dialog open={open} onClose={onClose} maxWidth="md" fullWidth>
      <DialogTitle>Criar Pipeline</DialogTitle>
      <DialogContent>
        {error && (
          <Typography color="error" gutterBottom>
            {error}
          </Typography>
        )}
        <Box sx={{ display: 'flex', flexDirection: 'column', gap: 2, mt: 2 }}>
          <TextField
            label="Nome do Pipeline"
            value={name}
            onChange={(e) => setName(e.target.value)}
            fullWidth
            required
          />

          <FormControl fullWidth>
            <InputLabel>Tipo de Transformação</InputLabel>
            <Select
              value={transformationType}
              onChange={(e) => setTransformationType(e.target.value)}
              label="Tipo de Transformação"
            >
              {transformationTypes.map((type) => (
                <MenuItem key={type.value} value={type.value}>
                  {type.label}
                </MenuItem>
              ))}
            </Select>
          </FormControl>

          <Box sx={{ border: '1px solid #ccc', borderRadius: 1 }}>
            <CodeEditor
              value={code}
              language={transformationType === 'sql' ? 'sql' : 'python'}
              placeholder={
                transformationType === 'sql'
                  ? 'SELECT * FROM table'
                  : 'def transform(df):\n    return df'
              }
              onChange={(e) => setCode(e.target.value)}
              padding={15}
              style={{
                fontSize: 12,
                backgroundColor: '#f5f5f5',
                fontFamily: 'ui-monospace,SFMono-Regular,SF Mono,Consolas,Liberation Mono,Menlo,monospace',
              }}
            />
          </Box>

          <FormControl fullWidth>
            <InputLabel>Intervalo de Execução</InputLabel>
            <Select
              value={scheduleInterval}
              onChange={(e) => setScheduleInterval(e.target.value)}
              label="Intervalo de Execução"
            >
              {scheduleIntervals.map((interval) => (
                <MenuItem key={interval.value} value={interval.value}>
                  {interval.label}
                </MenuItem>
              ))}
            </Select>
          </FormControl>

          {scheduleInterval === 'custom' && (
            <TextField
              fullWidth
              label="Expressão Cron"
              value={customSchedule}
              onChange={(e) => setCustomSchedule(e.target.value)}
              helperText="Ex: 0 0 * * * (Todo dia à meia-noite)"
              required
            />
          )}
        </Box>
      </DialogContent>
      <DialogActions>
        <Button onClick={onClose}>Cancelar</Button>
        <Button onClick={handleSubmit} variant="contained" color="primary">
          Criar
        </Button>
      </DialogActions>
    </Dialog>
  );
};

export default CreatePipelineDialog;
