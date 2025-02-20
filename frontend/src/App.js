import React from 'react';
import { Box, Tab, Tabs, Typography } from '@mui/material';
import FeatureGroups from './components/FeatureGroups';
import Features from './components/Features';

function TabPanel(props) {
  const { children, value, index, ...other } = props;

  return (
    <div
      role="tabpanel"
      hidden={value !== index}
      id={`simple-tabpanel-${index}`}
      aria-labelledby={`simple-tab-${index}`}
      {...other}
    >
      {value === index && (
        <Box sx={{ p: 3 }}>
          {children}
        </Box>
      )}
    </div>
  );
}

function App() {
  const [value, setValue] = React.useState(0);

  const handleChange = (event, newValue) => {
    setValue(newValue);
  };

  return (
    <Box sx={{ width: '100%' }}>
      <Box sx={{ borderBottom: 1, borderColor: 'divider' }}>
        <Tabs value={value} onChange={handleChange} aria-label="basic tabs example">
          <Tab label="Feature Groups" />
          <Tab label="Features" />
        </Tabs>
      </Box>
      <TabPanel value={value} index={0}>
        <FeatureGroups />
      </TabPanel>
      <TabPanel value={value} index={1}>
        <Features />
      </TabPanel>
    </Box>
  );
}

export default App;
