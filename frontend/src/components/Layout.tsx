import React from 'react';
import { useNavigate } from 'react-router-dom';
import {
  AppBar,
  Box,
  Drawer,
  IconButton,
  List,
  ListItem,
  ListItemIcon,
  ListItemText,
  Toolbar,
  Typography,
  useTheme,
} from '@mui/material';
import {
  Menu as MenuIcon,
  Dashboard as DashboardIcon,
  Storage as StorageIcon,
  GroupWork as GroupWorkIcon,
  Timeline as TimelineIcon,
} from '@mui/icons-material';

const drawerWidth = 240;

interface LayoutProps {
  children: React.ReactNode;
}

export default function Layout({ children }: LayoutProps) {
  const navigate = useNavigate();
  const theme = useTheme();
  const [mobileOpen, setMobileOpen] = React.useState(false);

  const handleDrawerToggle = () => {
    setMobileOpen(!mobileOpen);
  };

  const menuItems = [
    { text: 'Dashboard', icon: <DashboardIcon />, path: '/' },
    { text: 'Features', icon: <StorageIcon />, path: '/features' },
    { text: 'Feature Groups', icon: <GroupWorkIcon />, path: '/feature-groups' },
    { text: 'Monitoring', icon: <TimelineIcon />, path: '/monitoring' },
  ];

  const drawer = (
    <Box
      sx={{
        height: '100%',
        background: 'linear-gradient(180deg, #666666 0%, #777777 100%)',
      }}
    >
      <Toolbar
        sx={{
          background: 'linear-gradient(90deg, rgba(0, 242, 255, 0.1) 0%, rgba(0, 242, 255, 0) 100%)',
          borderBottom: '1px solid rgba(0, 242, 255, 0.1)',
        }}
      >
        <Typography
          variant="h6"
          sx={{
            fontFamily: '"Orbitron", sans-serif',
            letterSpacing: '0.1em',
            background: 'linear-gradient(45deg, #00f2ff, #ff00f2)',
            WebkitBackgroundClip: 'text',
            WebkitTextFillColor: 'transparent',
          }}
        >
          FSTORE
        </Typography>
      </Toolbar>
      <List>
        {menuItems.map((item) => (
          <ListItem
            button
            key={item.text}
            onClick={() => navigate(item.path)}
            sx={{
              margin: '8px',
              borderRadius: '4px',
              '&:hover': {
                background: 'linear-gradient(90deg, rgba(0, 242, 255, 0.1) 0%, rgba(0, 242, 255, 0) 100%)',
                boxShadow: '0 0 10px rgba(0, 242, 255, 0.2)',
              },
            }}
          >
            <ListItemIcon
              sx={{
                color: theme.palette.primary.main,
                minWidth: '40px',
              }}
            >
              {item.icon}
            </ListItemIcon>
            <ListItemText
              primary={item.text}
              sx={{
                '& .MuiTypography-root': {
                  fontFamily: '"Orbitron", sans-serif',
                  letterSpacing: '0.05em',
                },
              }}
            />
          </ListItem>
        ))}
      </List>
    </Box>
  );

  return (
    <Box sx={{ display: 'flex', minHeight: '100vh', background: theme.palette.background.default }}>
      <AppBar
        position="fixed"
        sx={{
          zIndex: (theme) => theme.zIndex.drawer + 1,
          background: 'linear-gradient(90deg, #0a0b1e 0%, #13142b 100%)',
          borderBottom: '1px solid rgba(0, 242, 255, 0.1)',
          boxShadow: '0 0 20px rgba(0, 242, 255, 0.2)',
        }}
      >
        <Toolbar>
          <IconButton
            color="inherit"
            aria-label="open drawer"
            edge="start"
            onClick={handleDrawerToggle}
            sx={{
              mr: 2,
              display: { sm: 'none' },
              '&:hover': {
                background: 'rgba(0, 242, 255, 0.1)',
              },
            }}
          >
            <MenuIcon />
          </IconButton>
          <Typography
            variant="h6"
            noWrap
            component="div"
            sx={{
              fontFamily: '"Orbitron", sans-serif',
              letterSpacing: '0.1em',
              background: 'linear-gradient(45deg, #00f2ff, #ff00f2)',
              WebkitBackgroundClip: 'text',
              WebkitTextFillColor: 'transparent',
            }}
          >
            FEATURE STORE
          </Typography>
        </Toolbar>
      </AppBar>
      <Box
        component="nav"
        sx={{ width: { sm: drawerWidth }, flexShrink: { sm: 0 } }}
      >
        <Drawer
          variant="temporary"
          open={mobileOpen}
          onClose={handleDrawerToggle}
          ModalProps={{
            keepMounted: true,
          }}
          sx={{
            display: { xs: 'block', sm: 'none' },
            '& .MuiDrawer-paper': {
              boxSizing: 'border-box',
              width: drawerWidth,
              background: 'linear-gradient(180deg, #666666 0%, #777777 100%)',
              borderRight: '1px solid rgba(0, 242, 255, 0.1)',
            },
          }}
        >
          {drawer}
        </Drawer>
        <Drawer
          variant="permanent"
          sx={{
            display: { xs: 'none', sm: 'block' },
            '& .MuiDrawer-paper': {
              boxSizing: 'border-box',
              width: drawerWidth,
              background: 'linear-gradient(180deg, #666666 0%, #777777 100%)',
              borderRight: '1px solid rgba(0, 242, 255, 0.1)',
            },
          }}
          open
        >
          {drawer}
        </Drawer>
      </Box>
      <Box
        component="main"
        sx={{
          flexGrow: 1,
          p: 3,
          width: { sm: `calc(100% - ${drawerWidth}px)` },
          background: 'linear-gradient(135deg, #0a0b1e 0%, #13142b 100%)',
        }}
      >
        <Toolbar />
        {children}
      </Box>
    </Box>
  );
}
