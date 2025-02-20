import { createTheme } from '@mui/material/styles';

const theme = createTheme({
  palette: {
    mode: 'dark',
    primary: {
      main: '#00f2ff', // Azul neon
      light: '#5cffff',
      dark: '#00bfcc',
      contrastText: '#000000',
    },
    secondary: {
      main: '#ff00f2', // Rosa neon
      light: '#ff5cff',
      dark: '#cc00bf',
      contrastText: '#000000',
    },
    background: {
      default: '#0a0b1e', // Azul escuro profundo
      paper: '#13142b',   // Azul escuro um pouco mais claro
    },
    text: {
      primary: '#ffffff',
      secondary: 'rgba(255, 255, 255, 0.7)',
    },
  },
  typography: {
    fontFamily: '"Orbitron", "Roboto", "Helvetica", "Arial", sans-serif',
    h1: {
      fontWeight: 700,
      letterSpacing: '0.1em',
      textTransform: 'uppercase',
    },
    h2: {
      fontWeight: 600,
      letterSpacing: '0.08em',
    },
    h3: {
      fontWeight: 600,
      letterSpacing: '0.06em',
    },
    button: {
      fontWeight: 600,
      letterSpacing: '0.05em',
      textTransform: 'uppercase',
    },
  },
  components: {
    MuiButton: {
      styleOverrides: {
        root: {
          borderRadius: '4px',
          textTransform: 'uppercase',
          padding: '10px 24px',
          position: 'relative',
          overflow: 'hidden',
          '&::before': {
            content: '""',
            position: 'absolute',
            top: 0,
            left: 0,
            right: 0,
            bottom: 0,
            background: 'linear-gradient(45deg, rgba(255,255,255,0) 0%, rgba(255,255,255,0.1) 50%, rgba(255,255,255,0) 100%)',
            transform: 'translateX(-100%)',
            transition: 'transform 0.6s',
          },
          '&:hover::before': {
            transform: 'translateX(100%)',
          },
        },
        contained: {
          background: 'linear-gradient(45deg, #00f2ff 30%, #00bfcc 90%)',
          boxShadow: '0 0 10px rgba(0, 242, 255, 0.5)',
          '&:hover': {
            boxShadow: '0 0 20px rgba(0, 242, 255, 0.7)',
          },
        },
        outlined: {
          borderColor: '#00f2ff',
          borderWidth: '2px',
          '&:hover': {
            borderWidth: '2px',
            boxShadow: '0 0 15px rgba(0, 242, 255, 0.3)',
          },
        },
      },
    },
    MuiAppBar: {
      styleOverrides: {
        root: {
          background: 'linear-gradient(90deg, #0a0b1e 0%, #13142b 100%)',
          boxShadow: '0 0 20px rgba(0, 242, 255, 0.2)',
        },
      },
    },
    MuiDrawer: {
      styleOverrides: {
        paper: {
          background: 'linear-gradient(180deg, #0a0b1e 0%, #13142b 100%)',
          borderRight: '1px solid rgba(0, 242, 255, 0.1)',
        },
      },
    },
    MuiCard: {
      styleOverrides: {
        root: {
          background: 'linear-gradient(135deg, #13142b 0%, #1a1b35 100%)',
          borderRadius: '8px',
          boxShadow: '0 4px 20px rgba(0, 0, 0, 0.5)',
          border: '1px solid rgba(0, 242, 255, 0.1)',
          '&:hover': {
            boxShadow: '0 4px 25px rgba(0, 242, 255, 0.15)',
          },
        },
      },
    },
    MuiListItem: {
      styleOverrides: {
        root: {
          '&:hover': {
            background: 'linear-gradient(90deg, rgba(0, 242, 255, 0.1) 0%, rgba(0, 242, 255, 0) 100%)',
          },
        },
      },
    },
  },
});

export default theme;
