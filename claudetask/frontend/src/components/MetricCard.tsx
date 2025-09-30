import React from 'react';
import { Card, CardContent, Box, Typography, alpha, useTheme } from '@mui/material';
import { SvgIconComponent } from '@mui/icons-material';

interface MetricCardProps {
  title: string;
  value: number | string;
  icon: SvgIconComponent;
  color?: 'primary' | 'success' | 'warning' | 'error' | 'info';
  subtitle?: string;
  trend?: {
    value: number;
    isPositive: boolean;
  };
}

const MetricCard: React.FC<MetricCardProps> = ({
  title,
  value,
  icon: Icon,
  color = 'primary',
  subtitle,
  trend,
}) => {
  const theme = useTheme();

  const colorMap = {
    primary: theme.palette.primary.main,
    success: theme.palette.success.main,
    warning: theme.palette.warning.main,
    error: theme.palette.error.main,
    info: theme.palette.info.main,
  };

  const selectedColor = colorMap[color];

  return (
    <Card
      sx={{
        height: '100%',
        position: 'relative',
        overflow: 'hidden',
        transition: 'all 0.3s cubic-bezier(0.4, 0, 0.2, 1)',
        '&:hover': {
          transform: 'translateY(-4px)',
          boxShadow: theme.shadows[8],
        },
        '&::before': {
          content: '""',
          position: 'absolute',
          top: 0,
          left: 0,
          right: 0,
          height: '4px',
          background: `linear-gradient(90deg, ${selectedColor} 0%, ${alpha(
            selectedColor,
            0.6
          )} 100%)`,
        },
      }}
    >
      <CardContent sx={{ p: 3 }}>
        <Box
          sx={{
            display: 'flex',
            alignItems: 'flex-start',
            justifyContent: 'space-between',
            mb: 2,
          }}
        >
          <Box sx={{ flex: 1 }}>
            <Typography
              variant="body2"
              color="text.secondary"
              sx={{
                fontWeight: 500,
                textTransform: 'uppercase',
                letterSpacing: '0.05em',
                fontSize: '0.75rem',
                mb: 1,
              }}
            >
              {title}
            </Typography>
            <Typography
              variant="h3"
              sx={{
                fontWeight: 700,
                color: 'text.primary',
                lineHeight: 1,
                mb: 0.5,
              }}
            >
              {value}
            </Typography>
            {subtitle && (
              <Typography variant="body2" color="text.secondary">
                {subtitle}
              </Typography>
            )}
            {trend && (
              <Box sx={{ display: 'flex', alignItems: 'center', mt: 1 }}>
                <Typography
                  variant="caption"
                  sx={{
                    color: trend.isPositive ? 'success.main' : 'error.main',
                    fontWeight: 600,
                    mr: 0.5,
                  }}
                >
                  {trend.isPositive ? '+' : '-'}
                  {Math.abs(trend.value)}%
                </Typography>
                <Typography variant="caption" color="text.secondary">
                  vs last period
                </Typography>
              </Box>
            )}
          </Box>
          <Box
            sx={{
              width: 56,
              height: 56,
              borderRadius: 2,
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
              background: `linear-gradient(135deg, ${selectedColor} 0%, ${alpha(
                selectedColor,
                0.7
              )} 100%)`,
              boxShadow: `0 8px 16px ${alpha(selectedColor, 0.3)}`,
            }}
          >
            <Icon sx={{ fontSize: 32, color: 'white' }} />
          </Box>
        </Box>
      </CardContent>
    </Card>
  );
};

export default MetricCard;