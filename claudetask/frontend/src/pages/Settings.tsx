import React from 'react';
import {
  Box,
  Card,
  CardContent,
  Typography,
  Alert,
} from '@mui/material';

const Settings: React.FC = () => {
  return (
    <Box>
      <Typography variant="h4" gutterBottom>
        Settings
      </Typography>
      
      <Card>
        <CardContent>
          <Typography variant="h6" gutterBottom>
            Project Settings
          </Typography>
          <Alert severity="info">
            Project settings will be available in a future version.
            Current configuration is managed through the initialization process.
          </Alert>
        </CardContent>
      </Card>
    </Box>
  );
};

export default Settings;