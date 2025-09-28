// SynthForge Dashboard - Main App Component
// Production-grade React TypeScript dashboard with real-time capabilities

import React, { useEffect, useState } from 'react';
import {
  BrowserRouter as Router,
  Routes,
  Route,
  Navigate,
} from 'react-router-dom';
import { ThemeProvider, createTheme } from '@mui/material/styles';
import { CssBaseline, Box } from '@mui/material';
import { QueryClient, QueryClientProvider } from 'react-query';
import { Provider as ReduxProvider } from 'react-redux';
import { store } from './store/store';

// Components
import Sidebar from './components/Layout/Sidebar';
import TopBar from './components/Layout/TopBar';
import LoadingScreen from './components/Common/LoadingScreen';
import ErrorBoundary from './components/Common/ErrorBoundary';
import ProtectedRoute from './components/Auth/ProtectedRoute';

// Pages
import Dashboard from './pages/Dashboard';
import RealTimeMonitoring from './pages/RealTimeMonitoring';
import RiskAnalysis from './pages/RiskAnalysis';
import AlertManagement from './pages/AlertManagement';
import SensorManagement from './pages/SensorManagement';
import Analytics from './pages/Analytics';
import Settings from './pages/Settings';
import Login from './pages/Login';

// Services
import { authService } from './services/authService';
import { websocketService } from './services/websocketService';

// Hooks
import { useAppDispatch, useAppSelector } from './hooks/redux';
import { setUser, clearUser } from './store/slices/authSlice';
import { updateConnectionStatus } from './store/slices/systemSlice';

// React Query client
const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      retry: 3,
      retryDelay: (attemptIndex) => Math.min(1000 * 2 ** attemptIndex, 30000),
      staleTime: 5 * 60 * 1000, // 5 minutes
      cacheTime: 10 * 60 * 1000, // 10 minutes
      refetchOnWindowFocus: false,
    },
  },
});

// Dark theme optimized for industrial dashboards
const darkTheme = createTheme({
  palette: {
    mode: 'dark',
    primary: {
      main: '#1976d2',
      light: '#42a5f5',
      dark: '#1565c0',
    },
    secondary: {
      main: '#f50057',
      light: '#ff5983',
      dark: '#c51162',
    },
    error: {
      main: '#f44336',
      light: '#e57373',
      dark: '#d32f2f',
    },
    warning: {
      main: '#ff9800',
      light: '#ffb74d',
      dark: '#f57c00',
    },
    info: {
      main: '#2196f3',
      light: '#64b5f6',
      dark: '#1976d2',
    },
    success: {
      main: '#4caf50',
      light: '#81c784',
      dark: '#388e3c',
    },
    background: {
      default: '#0a0e1a',
      paper: '#1a1f2e',
    },
    text: {
      primary: '#ffffff',
      secondary: '#b0bec5',
    },
  },
  typography: {
    fontFamily: '"Roboto", "Helvetica", "Arial", sans-serif',
    h1: {
      fontSize: '2.5rem',
      fontWeight: 300,
      lineHeight: 1.2,
    },
    h2: {
      fontSize: '2rem',
      fontWeight: 300,
      lineHeight: 1.2,
    },
    h3: {
      fontSize: '1.75rem',
      fontWeight: 400,
      lineHeight: 1.2,
    },
    h4: {
      fontSize: '1.5rem',
      fontWeight: 400,
      lineHeight: 1.2,
    },
    h5: {
      fontSize: '1.25rem',
      fontWeight: 400,
      lineHeight: 1.2,
    },
    h6: {
      fontSize: '1rem',
      fontWeight: 500,
      lineHeight: 1.2,
    },
  },
  components: {
    MuiCssBaseline: {
      styleOverrides: {
        '*::-webkit-scrollbar': {
          width: '8px',
        },
        '*::-webkit-scrollbar-track': {
          background: '#2d3748',
        },
        '*::-webkit-scrollbar-thumb': {
          background: '#4a5568',
          borderRadius: '4px',
        },
        '*::-webkit-scrollbar-thumb:hover': {
          background: '#718096',
        },
      },
    },
    MuiCard: {
      styleOverrides: {
        root: {
          backgroundImage: 'none',
          border: '1px solid rgba(255, 255, 255, 0.12)',
        },
      },
    },
    MuiButton: {
      styleOverrides: {
        root: {
          textTransform: 'none',
          fontWeight: 500,
        },
      },
    },
  },
});

const App: React.FC = () => {
  const [loading, setLoading] = useState(true);
  const [sidebarOpen, setSidebarOpen] = useState(true);
  
  const dispatch = useAppDispatch();
  const { user, isAuthenticated } = useAppSelector((state) => state.auth);

  useEffect(() => {
    // Initialize authentication
    const initAuth = async () => {
      try {
        const token = localStorage.getItem('authToken');
        if (token) {
          const userData = await authService.validateToken(token);
          if (userData) {
            dispatch(setUser(userData));
            
            // Initialize WebSocket connection
            websocketService.connect(token);
            websocketService.on('connection', () => {
              dispatch(updateConnectionStatus('connected'));
            });
            websocketService.on('disconnect', () => {
              dispatch(updateConnectionStatus('disconnected'));
            });
          } else {
            localStorage.removeItem('authToken');
            dispatch(clearUser());
          }
        }
      } catch (error) {
        console.error('Auth initialization failed:', error);
        localStorage.removeItem('authToken');
        dispatch(clearUser());
      } finally {
        setLoading(false);
      }
    };

    initAuth();

    // Cleanup on unmount
    return () => {
      websocketService.disconnect();
    };
  }, [dispatch]);

  // Show loading screen while initializing
  if (loading) {
    return <LoadingScreen message="Initializing SynthForge..." />;
  }

  // Show login if not authenticated
  if (!isAuthenticated) {
    return (
      <ThemeProvider theme={darkTheme}>
        <CssBaseline />
        <QueryClientProvider client={queryClient}>
          <Router>
            <Routes>
              <Route path="/login" element={<Login />} />
              <Route path="*" element={<Navigate to="/login" replace />} />
            </Routes>
          </Router>
        </QueryClientProvider>
      </ThemeProvider>
    );
  }

  return (
    <ErrorBoundary>
      <ThemeProvider theme={darkTheme}>
        <CssBaseline />
        <QueryClientProvider client={queryClient}>
          <Router>
            <Box sx={{ display: 'flex', minHeight: '100vh' }}>
              <Sidebar 
                open={sidebarOpen} 
                onToggle={() => setSidebarOpen(!sidebarOpen)} 
              />
              <Box
                component="main"
                sx={{
                  flexGrow: 1,
                  minHeight: '100vh',
                  transition: (theme) =>
                    theme.transitions.create(['margin'], {
                      easing: theme.transitions.easing.sharp,
                      duration: theme.transitions.duration.leavingScreen,
                    }),
                  marginLeft: sidebarOpen ? '240px' : '60px',
                }}
              >
                <TopBar 
                  user={user} 
                  onMenuClick={() => setSidebarOpen(!sidebarOpen)}
                />
                <Box sx={{ p: 3 }}>
                  <Routes>
                    <Route 
                      path="/" 
                      element={
                        <ProtectedRoute>
                          <Dashboard />
                        </ProtectedRoute>
                      } 
                    />
                    <Route 
                      path="/monitoring" 
                      element={
                        <ProtectedRoute>
                          <RealTimeMonitoring />
                        </ProtectedRoute>
                      } 
                    />
                    <Route 
                      path="/risk-analysis" 
                      element={
                        <ProtectedRoute>
                          <RiskAnalysis />
                        </ProtectedRoute>
                      } 
                    />
                    <Route 
                      path="/alerts" 
                      element={
                        <ProtectedRoute>
                          <AlertManagement />
                        </ProtectedRoute>
                      } 
                    />
                    <Route 
                      path="/sensors" 
                      element={
                        <ProtectedRoute requiredRoles={['admin', 'operator']}>
                          <SensorManagement />
                        </ProtectedRoute>
                      } 
                    />
                    <Route 
                      path="/analytics" 
                      element={
                        <ProtectedRoute>
                          <Analytics />
                        </ProtectedRoute>
                      } 
                    />
                    <Route 
                      path="/settings" 
                      element={
                        <ProtectedRoute requiredRoles={['admin']}>
                          <Settings />
                        </ProtectedRoute>
                      } 
                    />
                    <Route path="*" element={<Navigate to="/" replace />} />
                  </Routes>
                </Box>
              </Box>
            </Box>
          </Router>
        </QueryClientProvider>
      </ThemeProvider>
    </ErrorBoundary>
  );
};

// Redux-wrapped App component
const AppWithRedux: React.FC = () => (
  <ReduxProvider store={store}>
    <App />
  </ReduxProvider>
);

export default AppWithRedux;