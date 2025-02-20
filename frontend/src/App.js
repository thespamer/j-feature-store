import React from 'react';
import { Box, Typography, Container } from '@mui/material';

function App() {
  return (
    <Container maxWidth="lg">
      <Box sx={{ my: 4 }}>
        <Typography variant="h4" component="h1" gutterBottom>
          FStore Platform
        </Typography>
        <Typography variant="body1">
          Welcome to the Feature Store Platform
        </Typography>
      </Box>
    </Container>
  );
}

export default App;
