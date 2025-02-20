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
      default: '#424242', // Cinza médio
      paper: '#4f4f4f',   // Cinza médio um pouco mais claro
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
      color: '#ffffff',
      textShadow: '0 0 10px rgba(0, 242, 255, 0.5)',
    },
    h2: {
      fontWeight: 600,
      letterSpacing: '0.08em',
      color: '#ffffff',
      textShadow: '0 0 8px rgba(0, 242, 255, 0.4)',
    },
    h3: {
      fontWeight: 600,
      letterSpacing: '0.06em',
      color: '#ffffff',
      textShadow: '0 0 6px rgba(0, 242, 255, 0.3)',
    },
    h4: {
      color: '#ffffff',
      textShadow: '0 0 4px rgba(0, 242, 255, 0.2)',
    },
    h5: {
      color: '#ffffff',
      textShadow: '0 0 3px rgba(0, 242, 255, 0.2)',
    },
    h6: {
      color: '#ffffff',
      textShadow: '0 0 2px rgba(0, 242, 255, 0.2)',
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
          fontWeight: 600,
          letterSpacing: '0.05em',
          padding: '8px 16px',
          background: 'linear-gradient(45deg, rgba(0, 242, 255, 0.1), rgba(255, 0, 242, 0.1))',
          border: '1px solid rgba(0, 242, 255, 0.2)',
          transition: 'all 0.3s ease-in-out',
          '&:hover': {
            background: 'linear-gradient(45deg, rgba(0, 242, 255, 0.2), rgba(255, 0, 242, 0.2))',
            border: '1px solid rgba(0, 242, 255, 0.4)',
            boxShadow: '0 0 20px rgba(0, 242, 255, 0.2)',
          },
        },
      },
    },
    MuiAppBar: {
      styleOverrides: {
        root: {
          background: 'linear-gradient(180deg, #424242 0%, #4f4f4f 100%)',
          boxShadow: '0 0 20px rgba(0, 242, 255, 0.1)',
        },
      },
    },
    MuiDrawer: {
      styleOverrides: {
        paper: {
          background: 'linear-gradient(180deg, #424242 0%, #4f4f4f 100%)',
          borderRight: '1px solid rgba(0, 242, 255, 0.1)',
        },
      },
    },
    MuiCard: {
      styleOverrides: {
        root: {
          background: 'linear-gradient(45deg, rgba(0, 242, 255, 0.05), rgba(255, 0, 242, 0.05))',
          border: '1px solid rgba(0, 242, 255, 0.1)',
          borderRadius: '8px',
          transition: 'all 0.3s ease-in-out',
          '&:hover': {
            border: '1px solid rgba(0, 242, 255, 0.2)',
            boxShadow: '0 0 20px rgba(0, 242, 255, 0.1)',
          },
        },
      },
    },
  },
});

export default theme;
