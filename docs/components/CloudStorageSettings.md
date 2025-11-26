# CloudStorageSettings Component

## Overview

The CloudStorageSettings component provides a user interface for configuring MongoDB Atlas and Voyage AI cloud storage backend. It allows users to test connections, save credentials, check health status, and **migrate storage modes** (local ↔ MongoDB) with automatic data migration.

**Component Path**: `claudetask/frontend/src/pages/CloudStorageSettings.tsx`
**Version**: 2.0.0
**Last Updated**: 2025-11-27
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

5. **Storage Mode Migration** (NEW in v2.0)
   - Switch between Local (SQLite) and MongoDB storage
   - Automatic data migration preview
   - One-click migration with progress tracking
   - Safety checks prevent data loss
   - Rollback support if migration fails

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
| `connectionString` | `string` | MongoDB Atlas connection string |
| `databaseName` | `string` | Database name (default: "claudetask") |
| `voyageApiKey` | `string` | Voyage AI API key |
| `testing` | `boolean` | Connection test in progress |
| `saving` | `boolean` | Configuration save in progress |
| `testResult` | `TestResult \| null` | Connection test results |
| `isConfigured` | `boolean` | Whether MongoDB is configured |
| `currentStorageMode` | `'local' \| 'mongodb'` | Current project storage mode |
| `targetStorageMode` | `'local' \| 'mongodb'` | Target storage mode for migration |
| `mongodbConnected` | `boolean` | MongoDB connection status |
| `migrating` | `boolean` | Migration in progress |
| `migrationProgress` | `MigrationProgress \| null` | Real-time migration progress |
| `migrationPreview` | `MigrationPreview \| null` | Preview of data to be migrated |
| `showMigrationDialog` | `boolean` | Migration confirmation dialog visibility |
| `snackbar` | `object` | Notification message state |

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

### Storage Mode Migration Section (NEW in v2.0)

```tsx
<Paper sx={{ p: 3, mb: 3 }}>
  <Typography variant="h6" gutterBottom>
    <SwapHorizIcon sx={{ mr: 1, verticalAlign: 'middle' }} />
    Storage Mode Migration
  </Typography>

  <Alert severity="info" sx={{ mb: 2 }}>
    Current Mode: <strong>{currentStorageMode}</strong>
  </Alert>

  <RadioGroup
    value={targetStorageMode}
    onChange={(e) => setTargetStorageMode(e.target.value)}
  >
    <FormControlLabel
      value="local"
      control={<Radio />}
      label="Local Storage (SQLite + ChromaDB)"
    />
    <FormControlLabel
      value="mongodb"
      control={<Radio />}
      label="MongoDB Atlas + Vector Search"
      disabled={!mongodbConnected}
    />
  </RadioGroup>

  {migrationPreview && (
    <Alert severity="warning" sx={{ mt: 2 }}>
      <AlertTitle>Migration Preview</AlertTitle>
      <Typography>
        Tasks to migrate: {migrationPreview.sqlite_data.tasks}
      </Typography>
      <Typography>
        Sessions to migrate: {migrationPreview.sqlite_data.sessions}
      </Typography>
      {migrationPreview.warning && (
        <Typography color="error">{migrationPreview.warning}</Typography>
      )}
    </Alert>
  )}

  <Box sx={{ mt: 2, display: 'flex', gap: 2 }}>
    <Button
      variant="outlined"
      onClick={handlePreviewMigration}
      disabled={currentStorageMode === targetStorageMode}
    >
      Preview Migration
    </Button>
    <Button
      variant="contained"
      onClick={() => setShowMigrationDialog(true)}
      disabled={!migrationPreview || migrating}
    >
      Migrate Storage Mode
    </Button>
  </Box>

  {migrating && migrationProgress && (
    <Box sx={{ mt: 3 }}>
      <Typography variant="body2" gutterBottom>
        {migrationProgress.current_step}
      </Typography>
      <LinearProgress
        variant="determinate"
        value={(migrationProgress.steps_completed / migrationProgress.total_steps) * 100}
      />
      <Typography variant="caption">
        Step {migrationProgress.steps_completed} of {migrationProgress.total_steps}
      </Typography>
    </Box>
  )}
</Paper>

{/* Migration Confirmation Dialog */}
<Dialog open={showMigrationDialog} onClose={() => setShowMigrationDialog(false)}>
  <DialogTitle>Confirm Storage Mode Migration</DialogTitle>
  <DialogContent>
    <Typography gutterBottom>
      This will migrate all project data from <strong>{currentStorageMode}</strong>
      to <strong>{targetStorageMode}</strong>.
    </Typography>
    <Alert severity="warning" sx={{ mt: 2 }}>
      This operation cannot be undone. Ensure you have backups before proceeding.
    </Alert>
  </DialogContent>
  <DialogActions>
    <Button onClick={() => setShowMigrationDialog(false)}>Cancel</Button>
    <Button onClick={handleMigrate} variant="contained" color="primary">
      Confirm Migration
    </Button>
  </DialogActions>
</Dialog>
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

### Storage Mode Migration Workflow (NEW in v2.0)

#### Preview Migration

1. User selects target storage mode (Local or MongoDB)
2. System checks if target mode differs from current mode
3. User clicks "Preview Migration"
4. Backend analyzes data to be migrated:
   - Counts tasks, sessions, history entries
   - Checks for existing data in target storage
   - Identifies potential conflicts
5. Migration preview displayed with statistics

#### Execute Migration

1. User reviews migration preview
2. User clicks "Migrate Storage Mode"
3. Confirmation dialog shows:
   - Data to be migrated (tasks, sessions, etc.)
   - Warnings about existing data
   - Safety information
4. User confirms migration
5. Migration executes with real-time progress:
   - Step 1: Backup current data
   - Step 2: Migrate tasks
   - Step 3: Migrate sessions
   - Step 4: Migrate conversation history
   - Step 5: Update project settings
6. Progress bar and status updates displayed
7. Success message or error details shown
8. Page refreshes to reflect new storage mode

#### Migration Safety Features

- **Data validation**: Verify data integrity before and after migration
- **Atomic operations**: All-or-nothing migration (rollback on failure)
- **Backup creation**: Automatic backup before migration
- **Conflict detection**: Warn if target storage has existing data
- **Progress tracking**: Real-time updates during migration
- **Error handling**: Detailed error messages and recovery options

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

#### Cloud Storage Configuration
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

#### Storage Mode Migration (v2.0)
- [ ] Current storage mode displays correctly
- [ ] MongoDB option disabled when not configured
- [ ] Preview migration shows accurate statistics
- [ ] Migration preview detects existing data conflicts
- [ ] Confirmation dialog shows before migration
- [ ] Migration progress updates in real-time
- [ ] Migration completes successfully
- [ ] All data transferred correctly (verify counts)
- [ ] Project settings updated to new storage mode
- [ ] Migration errors handled gracefully with rollback
- [ ] Success message shown after completion
- [ ] Page refreshes to show new storage mode

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

### Cloud Storage Configuration
- `GET /api/settings/cloud-storage/status` - Check configuration status
- `GET /api/settings/cloud-storage/config` - Get current configuration (masked credentials)
- `POST /api/settings/cloud-storage/test` - Test MongoDB and Voyage AI connections
- `POST /api/settings/cloud-storage/save` - Save credentials to `.env` file
- `DELETE /api/settings/cloud-storage/config` - Remove configuration
- `GET /api/settings/cloud-storage/health` - MongoDB health check with collection stats

### Storage Mode Migration (NEW in v2.0)
- `GET /api/projects/{project_id}/storage-mode` - Get current storage mode
- `POST /api/projects/{project_id}/storage-mode/preview` - Preview migration data
- `POST /api/projects/{project_id}/storage-mode/migrate` - Execute storage mode migration
- `GET /api/projects/{project_id}/storage-mode/status` - Get migration progress status

## Future Enhancements

### Planned Features

- ⏳ Advanced configuration (connection pooling, timeouts)
- ⏳ Multiple database profiles
- ⏳ Automated backup scheduling
- ⏳ Usage statistics and billing information
- ⏳ Migration rollback functionality
- ⏳ Batch project migration (migrate all projects at once)

### Completed Features (v2.0)

- ✅ Storage mode migration with data transfer
- ✅ Migration preview with data statistics
- ✅ Real-time migration progress tracking
- ✅ Safety checks and conflict detection
- ✅ Atomic migration operations

### Potential Improvements

- Add connection test spinner with detailed status
- Show estimated costs based on usage
- Provide setup wizard for first-time users
- Add MongoDB Atlas cluster creation button
- Display vector search index status
- Export/import project data (JSON format)
- Schedule automatic backups before migrations

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

### Issue: Migration Fails or Hangs

**Symptoms**: Migration progress stops or shows error

**Solutions**:
1. Check both SQLite and MongoDB connections are healthy
2. Verify sufficient disk space for backups
3. Ensure no other processes are accessing the database
4. Check backend logs for detailed error messages
5. Try migration preview first to identify issues
6. Restart backend and retry migration

### Issue: Data Lost After Migration

**Symptoms**: Tasks or sessions missing after migration

**Solutions**:
1. Check migration preview statistics before migrating
2. Verify data exists in source storage before migration
3. Check migration progress completed all steps
4. Review backend logs for migration errors
5. Contact support with migration logs

### Issue: Cannot Switch to MongoDB Mode

**Symptoms**: MongoDB radio button is disabled

**Solutions**:
1. Verify MongoDB Atlas is configured in Cloud Storage Settings
2. Test MongoDB connection successfully
3. Check MongoDB connection health status
4. Ensure Voyage AI API key is configured
5. Restart backend after configuring MongoDB

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
**Version**: 2.0.0 (Storage Mode Migration)
**Testing Status**: ⏳ Manual testing complete, automated tests pending
**Documentation Status**: ✅ Complete
**Last Reviewed**: 2025-11-27

**Version History**:
- **v2.0.0** (2025-11-27): Added storage mode migration with data transfer
- **v1.0.0** (2025-11-26): Initial implementation with MongoDB configuration
