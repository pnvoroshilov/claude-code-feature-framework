import React from 'react';
import { Paper, Box, Typography, alpha, useTheme } from '@mui/material';
import { TrendingUp, TrendingDown } from '@mui/icons-material';

interface MetricCardProps {
  title: string;
  value: number | string;
  icon: React.ReactNode;
  color: string; // Theme color (e.g., theme.palette.primary.main)
  subtitle?: string;
  trend?: {
    value: string;
    direction: 'up' | 'down';
  };
  onClick?: () => void;
}

const MetricCard: React.FC<MetricCardProps> = ({
  title,
  value,
  icon,
  color,
  subtitle,
  trend,
  onClick,
}) => {
  const theme = useTheme();

  return (
    <Paper
      onClick={onClick}
      sx={{
        p: 3,
        borderRadius: 2,
        background: `linear-gradient(145deg, ${alpha(color, 0.05)}, ${alpha(color, 0.02)})`,
        border: `1px solid ${alpha(color, 0.15)}`,
        transition: 'all 0.3s cubic-bezier(0.4, 0, 0.2, 1)',
        position: 'relative',
        overflow: 'hidden',
        cursor: onClick ? 'pointer' : 'default',
        height: '100%',
        '&:hover': {
          transform: 'translateY(-4px)',
          boxShadow: `0 12px 24px -6px ${alpha(color, 0.2)}`,
          border: `1px solid ${alpha(color, 0.3)}`,
        },
        '&::before': {
          content: '""',
          position: 'absolute',
          top: 0,
          left: 0,
          right: 0,
          height: 4,
          background: `linear-gradient(90deg, ${color}, ${alpha(color, 0.5)})`,
        },
      }}
    >
      <Box display="flex" alignItems="start" justifyContent="space-between" mb={2}>
        <Box
          sx={{
            width: 48,
            height: 48,
            borderRadius: 2,
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            background: `linear-gradient(135deg, ${alpha(color, 0.2)}, ${alpha(color, 0.1)})`,
            border: `1px solid ${alpha(color, 0.3)}`,
          }}
        >
          {React.isValidElement(icon) ? (
            React.cloneElement(icon as React.ReactElement, {
              sx: { color: color, fontSize: 24 },
            })
          ) : (
            icon
          )}
        </Box>
      </Box>

      <Typography
        variant="body2"
        color="text.secondary"
        gutterBottom
        sx={{ fontSize: '0.85rem' }}
      >
        {title}
      </Typography>

      <Typography variant="h3" sx={{ fontWeight: 700, color: color, mb: 0.5 }}>
        {value}
      </Typography>

      {subtitle && (
        <Typography variant="caption" color="text.secondary">
          {subtitle}
        </Typography>
      )}

      {trend && (
        <Box sx={{ display: 'flex', alignItems: 'center', mt: 1, gap: 0.5 }}>
          {trend.direction === 'up' ? (
            <TrendingUp
              sx={{
                fontSize: 16,
                color: theme.palette.success.main,
              }}
            />
          ) : (
            <TrendingDown
              sx={{
                fontSize: 16,
                color: theme.palette.error.main,
              }}
            />
          )}
          <Typography
            variant="caption"
            sx={{
              color: trend.direction === 'up' ? 'success.main' : 'error.main',
              fontWeight: 600,
            }}
          >
            {trend.value}
          </Typography>
          <Typography variant="caption" color="text.secondary">
            vs last period
          </Typography>
        </Box>
      )}
    </Paper>
  );
};

export default MetricCard;