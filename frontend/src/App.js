import React from 'react';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import { ThemeProvider } from '@mui/material/styles';
import CssBaseline from '@mui/material/CssBaseline';

// Theme
import theme from './theme';

// Components
import Layout from './components/Layout';
import Dashboard from './pages/Dashboard';
import Features from './pages/Features';
import FeatureGroups from './pages/FeatureGroups';
import Monitoring from './pages/Monitoring';

const App = () => {
  return (
    <Router>
      <ThemeProvider theme={theme}>
        <CssBaseline />
        <Layout>
          <Routes>
            <Route path="/" element={<Dashboard />} />
            <Route path="/features" element={<Features />} />
            <Route path="/feature-groups" element={<FeatureGroups />} />
            <Route path="/monitoring" element={<Monitoring />} />
          </Routes>
        </Layout>
      </ThemeProvider>
    </Router>
  );
};

export default App;
