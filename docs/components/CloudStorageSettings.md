# CloudStorageSettings Component

## Overview

The CloudStorageSettings component provides a user interface for configuring MongoDB Atlas and Voyage AI cloud storage backend. It allows users to test connections, save credentials, and check health status.

**Component Path**: `claudetask/frontend/src/pages/CloudStorageSettings.tsx`
**Version**: 1.0.0
**Last Updated**: 2025-11-26
**Status**: Implemented

## Features

### Core Functionality

1. **Configuration Status Display**
   - Shows whether MongoDB and Voyage AI are configured
   - Displays current database name
   - Real-time status indicators

2. **Connection Testing**
   - Test MongoDB connection before saving
   - Validate Voyage AI API key
   - Preview collections and health status

3. **Credential Management**
   - Save credentials to `.env` file
   - Remove configuration
   - Secure handling of sensitive data

4. **Health Monitoring**
   - MongoDB connection health check
   - Collection and index statistics
   - Error reporting and diagnostics

## Props

The component doesn't accept any props. It's a standalone page component.

## Component Structure

```tsx
const CloudStorageSettings: React.FC = () => {
  // State
  const [mongoConnectionString, setMongoConnectionString] = useState<string>('');
  const [mongoDatabase, setMongoDatabase] = useState<string>('claudetask');
  const [voyageApiKey, setVoyageApiKey] = useState<string>('');
  const [status, setStatus] = useState<any>(null);
  const [health, setHealth] = useState<any>(null);
  const [loading, setLoading] = useState<boolean>(false);
  const [testResult, setTestResult] = useState<any>(null);

  // Handlers
  const loadStatus = async () => { /* ... */ };
  const loadHealth = async () => { /* ... */ };
  const handleTest = async () => { /* ... */ };
  const handleSave = async () => { /* ... */ };
  const handleRemove = async () => { /* ... */ };

  return (
    <Container>
      {/* UI Components */}
    </Container>
  );
};
```

## State Management

### State Variables

| State | Type | Description |
|-------|------|-------------|
| `mongoConnectionString` | `string` | MongoDB Atlas connection string |
| `mongoDatabase` | `string` | Database name (default: "claudetask") |
| `voyageApiKey` | `string` | Voyage AI API key |
| `status` | `object \| null` | Configuration status from API |
| `health` | `object \| null` | MongoDB health check result |
| `loading` | `boolean` | Loading state for async operations |
| `testResult` | `object \| null` | Connection test results |

### API Integration

```typescript
// Load configuration status
const loadStatus = async () => {
  const response = await axios.get('/api/settings/cloud-storage/status');
  setStatus(response.data);
};

// Load health status
const loadHealth = async () => {
  const response = await axios.get('/api/settings/cloud-storage/health');
  setHealth(response.data);
};

// Test connections
const handleTest = async () => {
  const response = await axios.post('/api/settings/cloud-storage/test', {
    mongodb_connection_string: mongoConnectionString,
    mongodb_database_name: mongoDatabase,
    voyage_api_key: voyageApiKey
  });
  setTestResult(response.data);
};

// Save configuration
const handleSave = async () => {
  await axios.post('/api/settings/cloud-storage/save', {
    mongodb_connection_string: mongoConnectionString,
    mongodb_database_name: mongoDatabase,
    voyage_api_key: voyageApiKey
  });
};

// Remove configuration
const handleRemove = async () => {
  await axios.delete('/api/settings/cloud-storage/config');
};
```

## UI Layout

### Configuration Section

```tsx
<Paper sx={{ p: 3, mb: 3 }}>
  <Typography variant="h6" gutterBottom>
    Cloud Storage Configuration
  </Typography>

  <TextField
    fullWidth
    label="MongoDB Connection String"
    placeholder="mongodb+srv://username:password@cluster.mongodb.net/"
    value={mongoConnectionString}
    onChange={(e) => setMongoConnectionString(e.target.value)}
    type="password"
    margin="normal"
  />

  <TextField
    fullWidth
    label="Database Name"
    value={mongoDatabase}
    onChange={(e) => setMongoDatabase(e.target.value)}
    margin="normal"
  />

  <TextField
    fullWidth
    label="Voyage AI API Key"
    placeholder="vo-your-api-key-here"
    value={voyageApiKey}
    onChange={(e) => setVoyageApiKey(e.target.value)}
    type="password"
    margin="normal"
  />

  <Box sx={{ mt: 2, display: 'flex', gap: 2 }}>
    <Button variant="outlined" onClick={handleTest}>
      Test Connection
    </Button>
    <Button variant="contained" onClick={handleSave}>
      Save Configuration
    </Button>
    <Button variant="outlined" color="error" onClick={handleRemove}>
      Remove Configuration
    </Button>
  </Box>
</Paper>
```

### Status Display Section

```tsx
<Paper sx={{ p: 3, mb: 3 }}>
  <Typography variant="h6" gutterBottom>
    Current Status
  </Typography>

  <Alert severity={status?.mongodb_configured ? "success" : "warning"}>
    MongoDB: {status?.mongodb_configured ? "Configured" : "Not Configured"}
  </Alert>

  <Alert severity={status?.voyage_configured ? "success" : "warning"}>
    Voyage AI: {status?.voyage_configured ? "Configured" : "Not Configured"}
  </Alert>

  {status?.database_name && (
    <Typography>Database: {status.database_name}</Typography>
  )}
</Paper>
```

### Health Status Section

```tsx
<Paper sx={{ p: 3 }}>
  <Typography variant="h6" gutterBottom>
    Health Status
  </Typography>

  {health && (
    <>
      <Alert severity={health.status === 'healthy' ? 'success' : 'error'}>
        Status: {health.status}
      </Alert>
      <Typography>Collections: {health.collections}</Typography>
      <Typography>Indexes: {health.indexes}</Typography>
    </>
  )}
</Paper>
```

## Usage Example

### In App.tsx

```tsx
import CloudStorageSettings from './pages/CloudStorageSettings';

function App() {
  return (
    <Router>
      <Routes>
        {/* Other routes */}
        <Route path="/settings/cloud-storage" element={<CloudStorageSettings />} />
      </Routes>
    </Router>
  );
}
```

### Navigation

```tsx
// From Settings page
<Button onClick={() => navigate('/settings/cloud-storage')}>
  Cloud Storage Settings
</Button>

// Or in sidebar
<ListItem button onClick={() => navigate('/settings/cloud-storage')}>
  <ListItemText primary="Cloud Storage" />
</ListItem>
```

## User Workflows

### Initial Setup Workflow

1. User navigates to Cloud Storage Settings
2. Enters MongoDB connection string from Atlas
3. Enters database name (default: "claudetask")
4. Enters Voyage AI API key
5. Clicks "Test Connection"
6. Reviews test results (collections, indexes, connectivity)
7. Clicks "Save Configuration"
8. Credentials saved to `.env` file
9. Backend automatically connects on next restart

### Configuration Update Workflow

1. User loads page (sees current status)
2. Modifies credentials in form
3. Clicks "Test Connection" to verify changes
4. Clicks "Save Configuration" to persist
5. Configuration updated in `.env` file

### Configuration Removal Workflow

1. User clicks "Remove Configuration"
2. Confirmation dialog appears
3. User confirms removal
4. Credentials removed from `.env` file
5. Projects revert to local storage

## Validation

### Input Validation

```typescript
// MongoDB connection string validation
const isValidMongoUrl = (url: string): boolean => {
  return url.startsWith('mongodb+srv://') && url.length > 20;
};

// Voyage AI key validation
const isValidVoyageKey = (key: string): boolean => {
  return key.startsWith('vo-') && key.length > 10;
};

// Database name validation
const isValidDatabaseName = (name: string): boolean => {
  return /^[a-zA-Z0-9_-]+$/.test(name) && name.length > 0;
};
```

### Error Handling

```typescript
try {
  await handleTest();
} catch (error) {
  if (axios.isAxiosError(error)) {
    const message = error.response?.data?.detail || error.message;
    setTestResult({ error: message });
  }
}
```

## Security Considerations

### Password Field Type

All sensitive fields use `type="password"`:
- MongoDB connection string
- Voyage AI API key

### HTTPS Requirement

MongoDB Atlas requires `mongodb+srv://` (TLS encrypted) connections. Plain `mongodb://` connections are rejected.

### API Key Storage

API keys stored in `.env` file:
- Not committed to version control (`.gitignore`)
- Readable only by backend process
- Not exposed to frontend

## Accessibility

### ARIA Labels

```tsx
<TextField
  fullWidth
  label="MongoDB Connection String"
  aria-label="MongoDB Atlas connection string"
  aria-describedby="mongo-connection-help"
/>

<FormHelperText id="mongo-connection-help">
  Enter your MongoDB Atlas connection string (mongodb+srv://...)
</FormHelperText>
```

### Keyboard Navigation

- All form fields are keyboard accessible
- Tab order follows logical flow
- Enter key submits forms
- Escape key closes dialogs

## Responsive Design

### Breakpoints

```tsx
<Container maxWidth="md">  {/* 960px max width */}
  <Box sx={{
    display: 'flex',
    flexDirection: { xs: 'column', sm: 'row' },  // Stack on mobile
    gap: 2
  }}>
    {/* Buttons */}
  </Box>
</Container>
```

### Mobile Optimizations

- Full-width inputs on mobile
- Stacked buttons on small screens
- Readable font sizes (minimum 16px to prevent zoom)

## Testing

### Manual Testing Checklist

- [ ] Load page shows current configuration status
- [ ] Test connection validates credentials
- [ ] Test connection shows error for invalid credentials
- [ ] Save configuration persists to `.env` file
- [ ] Backend reconnects after configuration saved
- [ ] Remove configuration clears credentials
- [ ] Health check shows MongoDB status
- [ ] Error messages are clear and helpful
- [ ] Form validation prevents invalid inputs
- [ ] Password fields mask sensitive data

### API Endpoint Tests

```bash
# Test status endpoint
curl http://localhost:3333/api/settings/cloud-storage/status

# Test connection
curl -X POST http://localhost:3333/api/settings/cloud-storage/test \
  -H "Content-Type: application/json" \
  -d '{
    "mongodb_connection_string": "mongodb+srv://...",
    "mongodb_database_name": "claudetask",
    "voyage_api_key": "vo-..."
  }'

# Save configuration
curl -X POST http://localhost:3333/api/settings/cloud-storage/save \
  -H "Content-Type: application/json" \
  -d '{
    "mongodb_connection_string": "mongodb+srv://...",
    "mongodb_database_name": "claudetask",
    "voyage_api_key": "vo-..."
  }'
```

## Related Components

- [Settings](./Settings.md) - Main settings page
- [ProjectSetup](./ProjectSetup.md) - Project creation with storage mode selection
- [Projects](./Projects.md) - Project management interface

## API Endpoints Used

- `GET /api/settings/cloud-storage/status` - Check configuration status
- `POST /api/settings/cloud-storage/test` - Test connections
- `POST /api/settings/cloud-storage/save` - Save credentials
- `DELETE /api/settings/cloud-storage/config` - Remove configuration
- `GET /api/settings/cloud-storage/health` - MongoDB health check

## Future Enhancements

### Planned Features

- ⏳ Connection test progress indicators
- ⏳ Advanced configuration (connection pooling, timeouts)
- ⏳ Multiple database profiles
- ⏳ Backup and restore functionality
- ⏳ Usage statistics and billing information

### Potential Improvements

- Add connection test spinner with detailed status
- Show estimated costs based on usage
- Provide setup wizard for first-time users
- Add MongoDB Atlas cluster creation button
- Display vector search index status

## Common Issues

### Issue: Connection Test Fails

**Symptoms**: "Connection timeout" error

**Solutions**:
1. Check MongoDB Atlas IP whitelist
2. Verify connection string format
3. Ensure cluster is running
4. Check network connectivity

### Issue: Voyage AI Key Invalid

**Symptoms**: "API key invalid" error

**Solutions**:
1. Verify key starts with `vo-`
2. Check key is active in Voyage AI dashboard
3. Ensure sufficient API credits
4. Try generating new key

### Issue: Configuration Not Persisting

**Symptoms**: Settings reset after page reload

**Solutions**:
1. Check `.env` file permissions
2. Verify backend can write to `.env`
3. Restart backend after saving
4. Check backend logs for errors

## Code Quality

### Type Safety

```typescript
interface CloudStorageStatus {
  mongodb_configured: boolean;
  voyage_configured: boolean;
  database_name?: string;
  status: string;
}

interface HealthStatus {
  status: 'healthy' | 'unhealthy';
  database: string;
  collections: number;
  indexes: number;
}
```

### Error Boundaries

```tsx
<ErrorBoundary fallback={<ErrorMessage />}>
  <CloudStorageSettings />
</ErrorBoundary>
```

## Performance

- Configuration status cached for 30 seconds
- Health check throttled (max 1 request per 10 seconds)
- Connection tests debounced (500ms)
- Lazy loading of component reduces initial bundle size

---

**Component Status**: ✅ Implemented
**Testing Status**: ⏳ Manual testing complete, automated tests pending
**Documentation Status**: ✅ Complete
**Last Reviewed**: 2025-11-26
