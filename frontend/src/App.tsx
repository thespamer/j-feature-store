import React from 'react';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import { ThemeProvider } from '@mui/material/styles';
import CssBaseline from '@mui/material/CssBaseline';
import { QueryClient, QueryClientProvider } from 'react-query';

// Theme
import theme from './theme';

// Components
import Layout from './components/Layout';
import Dashboard from './pages/Dashboard';
import Features from './pages/Features';
import FeatureGroups from './pages/FeatureGroups';
import Monitoring from './pages/Monitoring';

// Create a client for React Query
const queryClient = new QueryClient();

function App() {
  return (
    <Router>
      <ThemeProvider theme={theme}>
        <QueryClientProvider client={queryClient}>
          <CssBaseline />
          <Layout>
            <Routes>
              <Route path="/" element={<Dashboard />} />
              <Route path="/features" element={<Features />} />
              <Route path="/feature-groups" element={<FeatureGroups />} />
              <Route path="/monitoring" element={<Monitoring />} />
            </Routes>
          </Layout>
        </QueryClientProvider>
      </ThemeProvider>
    </Router>
  );
}

export default App;
