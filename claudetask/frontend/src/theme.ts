import { createTheme, ThemeOptions, alpha } from '@mui/material/styles';

// Modern color palette
const modernColors = {
  primary: {
    light: '#818cf8',
    main: '#6366f1',
    dark: '#4f46e5',
    gradient: 'linear-gradient(135deg, #6366f1 0%, #8b5cf6 100%)',
  },
  secondary: {
    light: '#5eead4',
    main: '#14b8a6',
    dark: '#0d9488',
  },
  success: {
    light: '#86efac',
    main: '#22c55e',
    dark: '#16a34a',
  },
  warning: {
    light: '#fcd34d',
    main: '#f59e0b',
    dark: '#d97706',
  },
  error: {
    light: '#fca5a5',
    main: '#ef4444',
    dark: '#dc2626',
  },
  info: {
    light: '#7dd3fc',
    main: '#0ea5e9',
    dark: '#0284c7',
  },
};

// Common theme options
const getCommonTheme = (mode: 'light' | 'dark'): ThemeOptions => ({
  palette: {
    mode,
    primary: modernColors.primary,
    secondary: modernColors.secondary,
    success: modernColors.success,
    warning: modernColors.warning,
    error: modernColors.error,
    info: modernColors.info,
    ...(mode === 'light'
      ? {
          // Light mode
          background: {
            default: '#f9fafb',
            paper: '#ffffff',
          },
          text: {
            primary: '#111827',
            secondary: '#6b7280',
          },
        }
      : {
          // Dark mode
          background: {
            default: '#0f172a',
            paper: '#1e293b',
          },
          text: {
            primary: '#f1f5f9',
            secondary: '#94a3b8',
          },
        }),
  },
  typography: {
    fontFamily: [
      '-apple-system',
      'BlinkMacSystemFont',
      '"Segoe UI"',
      'Roboto',
      '"Helvetica Neue"',
      'Arial',
      'sans-serif',
      '"Apple Color Emoji"',
      '"Segoe UI Emoji"',
      '"Segoe UI Symbol"',
    ].join(','),
    h1: {
      fontWeight: 700,
      fontSize: '3rem',
      lineHeight: 1.2,
      letterSpacing: '-0.02em',
    },
    h2: {
      fontWeight: 700,
      fontSize: '2.25rem',
      lineHeight: 1.3,
      letterSpacing: '-0.01em',
    },
    h3: {
      fontWeight: 600,
      fontSize: '1.875rem',
      lineHeight: 1.4,
    },
    h4: {
      fontWeight: 600,
      fontSize: '1.5rem',
      lineHeight: 1.4,
    },
    h5: {
      fontWeight: 600,
      fontSize: '1.25rem',
      lineHeight: 1.5,
    },
    h6: {
      fontWeight: 600,
      fontSize: '1rem',
      lineHeight: 1.5,
    },
    subtitle1: {
      fontWeight: 500,
      fontSize: '1rem',
      lineHeight: 1.5,
    },
    subtitle2: {
      fontWeight: 500,
      fontSize: '0.875rem',
      lineHeight: 1.57,
    },
    body1: {
      fontSize: '1rem',
      lineHeight: 1.5,
    },
    body2: {
      fontSize: '0.875rem',
      lineHeight: 1.57,
    },
    button: {
      fontWeight: 500,
      textTransform: 'none',
    },
  },
  spacing: 8,
  shape: {
    borderRadius: 12,
  },
  shadows: [
    'none',
    // Subtle shadows for depth
    '0 1px 2px 0 rgb(0 0 0 / 0.05)',
    '0 1px 3px 0 rgb(0 0 0 / 0.1), 0 1px 2px -1px rgb(0 0 0 / 0.1)',
    '0 4px 6px -1px rgb(0 0 0 / 0.1), 0 2px 4px -2px rgb(0 0 0 / 0.1)',
    '0 10px 15px -3px rgb(0 0 0 / 0.1), 0 4px 6px -4px rgb(0 0 0 / 0.1)',
    '0 20px 25px -5px rgb(0 0 0 / 0.1), 0 8px 10px -6px rgb(0 0 0 / 0.1)',
    '0 25px 50px -12px rgb(0 0 0 / 0.25)',
    // Additional shadows (maintaining Material-UI's 25 shadow levels)
    '0 25px 50px -12px rgb(0 0 0 / 0.25)',
    '0 25px 50px -12px rgb(0 0 0 / 0.25)',
    '0 25px 50px -12px rgb(0 0 0 / 0.25)',
    '0 25px 50px -12px rgb(0 0 0 / 0.25)',
    '0 25px 50px -12px rgb(0 0 0 / 0.25)',
    '0 25px 50px -12px rgb(0 0 0 / 0.25)',
    '0 25px 50px -12px rgb(0 0 0 / 0.25)',
    '0 25px 50px -12px rgb(0 0 0 / 0.25)',
    '0 25px 50px -12px rgb(0 0 0 / 0.25)',
    '0 25px 50px -12px rgb(0 0 0 / 0.25)',
    '0 25px 50px -12px rgb(0 0 0 / 0.25)',
    '0 25px 50px -12px rgb(0 0 0 / 0.25)',
    '0 25px 50px -12px rgb(0 0 0 / 0.25)',
    '0 25px 50px -12px rgb(0 0 0 / 0.25)',
    '0 25px 50px -12px rgb(0 0 0 / 0.25)',
    '0 25px 50px -12px rgb(0 0 0 / 0.25)',
    '0 25px 50px -12px rgb(0 0 0 / 0.25)',
    '0 25px 50px -12px rgb(0 0 0 / 0.25)',
  ] as any,
  components: {
    MuiCssBaseline: {
      styleOverrides: {
        body: {
          scrollbarWidth: 'thin',
          scrollbarColor: mode === 'dark' ? '#475569 #1e293b' : '#cbd5e1 #f1f5f9',
          '&::-webkit-scrollbar': {
            width: '8px',
            height: '8px',
          },
          '&::-webkit-scrollbar-track': {
            background: mode === 'dark' ? '#1e293b' : '#f1f5f9',
          },
          '&::-webkit-scrollbar-thumb': {
            background: mode === 'dark' ? '#475569' : '#cbd5e1',
            borderRadius: '4px',
            '&:hover': {
              background: mode === 'dark' ? '#64748b' : '#94a3b8',
            },
          },
        },
        '*': {
          transition: 'background-color 0.2s ease-in-out, color 0.2s ease-in-out',
        },
      },
    },
    MuiButton: {
      styleOverrides: {
        root: {
          borderRadius: 8,
          padding: '8px 16px',
          fontSize: '0.875rem',
          fontWeight: 500,
          boxShadow: 'none',
          '&:hover': {
            boxShadow: '0 4px 6px -1px rgb(0 0 0 / 0.1)',
          },
        },
        contained: {
          background: modernColors.primary.gradient,
          '&:hover': {
            background: modernColors.primary.gradient,
            transform: 'translateY(-1px)',
          },
        },
        sizeSmall: {
          padding: '6px 12px',
          fontSize: '0.8125rem',
        },
        sizeLarge: {
          padding: '10px 20px',
          fontSize: '0.9375rem',
        },
      },
    },
    MuiCard: {
      styleOverrides: {
        root: {
          borderRadius: 16,
          boxShadow: mode === 'dark'
            ? '0 4px 6px -1px rgb(0 0 0 / 0.3)'
            : '0 1px 3px 0 rgb(0 0 0 / 0.1)',
          backdropFilter: 'blur(10px)',
          background: mode === 'dark'
            ? alpha('#1e293b', 0.8)
            : alpha('#ffffff', 0.8),
          transition: 'all 0.3s cubic-bezier(0.4, 0, 0.2, 1)',
          '&:hover': {
            boxShadow: mode === 'dark'
              ? '0 10px 15px -3px rgb(0 0 0 / 0.4)'
              : '0 4px 6px -1px rgb(0 0 0 / 0.1)',
            transform: 'translateY(-2px)',
          },
        },
      },
    },
    MuiPaper: {
      styleOverrides: {
        root: {
          backgroundImage: 'none',
        },
        elevation1: {
          boxShadow: '0 1px 2px 0 rgb(0 0 0 / 0.05)',
        },
        elevation2: {
          boxShadow: '0 1px 3px 0 rgb(0 0 0 / 0.1)',
        },
      },
    },
    MuiChip: {
      styleOverrides: {
        root: {
          borderRadius: 8,
          fontWeight: 500,
          fontSize: '0.8125rem',
        },
        filled: {
          background: mode === 'dark' ? alpha('#6366f1', 0.2) : alpha('#6366f1', 0.1),
        },
      },
    },
    MuiTextField: {
      styleOverrides: {
        root: {
          '& .MuiOutlinedInput-root': {
            borderRadius: 8,
            '&:hover .MuiOutlinedInput-notchedOutline': {
              borderColor: modernColors.primary.main,
            },
          },
        },
      },
    },
    MuiDialog: {
      styleOverrides: {
        paper: {
          borderRadius: 16,
          boxShadow: '0 25px 50px -12px rgb(0 0 0 / 0.25)',
        },
      },
    },
    MuiDrawer: {
      styleOverrides: {
        paper: {
          borderRight: 'none',
          boxShadow: mode === 'dark'
            ? '4px 0 6px -1px rgb(0 0 0 / 0.3)'
            : '4px 0 6px -1px rgb(0 0 0 / 0.1)',
        },
      },
    },
    MuiAppBar: {
      styleOverrides: {
        root: {
          boxShadow: 'none',
          borderBottom: mode === 'dark' ? '1px solid #334155' : '1px solid #e2e8f0',
          backdropFilter: 'blur(10px)',
          background: mode === 'dark'
            ? alpha('#1e293b', 0.8)
            : alpha('#ffffff', 0.8),
        },
      },
    },
    MuiListItemButton: {
      styleOverrides: {
        root: {
          borderRadius: 8,
          margin: '4px 8px',
          '&.Mui-selected': {
            background: modernColors.primary.gradient,
            color: '#ffffff',
            '&:hover': {
              background: modernColors.primary.gradient,
            },
            '& .MuiListItemIcon-root': {
              color: '#ffffff',
            },
          },
        },
      },
    },
    MuiTooltip: {
      styleOverrides: {
        tooltip: {
          borderRadius: 8,
          fontSize: '0.75rem',
          padding: '8px 12px',
        },
      },
    },
  },
});

export const createAppTheme = (mode: 'light' | 'dark') => {
  return createTheme(getCommonTheme(mode));
};

export default createAppTheme;