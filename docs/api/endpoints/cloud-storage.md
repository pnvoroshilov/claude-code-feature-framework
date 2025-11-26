# Cloud Storage API Endpoints

## Overview

The Cloud Storage API provides endpoints for configuring and managing MongoDB Atlas and Voyage AI integration for cloud-based storage with vector search capabilities.

**Base Path**: `/api/settings/cloud-storage`
**Version**: 1.0.0
**Last Updated**: 2025-11-26

## Endpoints

### 1. Get Configuration Status

Check if MongoDB Atlas and Voyage AI are configured.

**Endpoint**: `GET /api/settings/cloud-storage/status`

**Authentication**: None (local desktop app)

**Response**:
```json
{
  "mongodb_configured": true,
  "voyage_configured": true,
  "database_name": "claudetask",
  "status": "ok"
}
```

**Response Fields**:
| Field | Type | Description |
|-------|------|-------------|
| `mongodb_configured` | `boolean` | Whether MongoDB connection string is set |
| `voyage_configured` | `boolean` | Whether Voyage AI API key is set |
| `database_name` | `string` | MongoDB database name (if configured) |
| `status` | `string` | Overall status: "ok" or "not_configured" |

**Status Codes**:
- `200 OK`: Configuration status retrieved successfully

**Example**:
```bash
curl http://localhost:3333/api/settings/cloud-storage/status
```

---

### 2. Test Connections

Test MongoDB and Voyage AI connections before saving credentials.

**Endpoint**: `POST /api/settings/cloud-storage/test`

**Authentication**: None

**Request Body**:
```json
{
  "mongodb_connection_string": "mongodb+srv://username:password@cluster.mongodb.net/",
  "mongodb_database_name": "claudetask",
  "voyage_api_key": "vo-your-api-key-here"
}
```

**Request Fields**:
| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `mongodb_connection_string` | `string` | Yes | MongoDB Atlas connection string (must use mongodb+srv://) |
| `mongodb_database_name` | `string` | Yes | Database name to use |
| `voyage_api_key` | `string` | Yes | Voyage AI API key (starts with vo-) |

**Response (Success)**:
```json
{
  "mongodb_status": "connected",
  "voyage_status": "valid",
  "database_name": "claudetask",
  "collections": ["projects", "tasks", "conversation_memory", "task_history", "project_settings"],
  "indexes_count": 12,
  "message": "All connections successful"
}
```

**Response (Failure)**:
```json
{
  "mongodb_status": "connection_failed",
  "voyage_status": "invalid_key",
  "error": "MongoDB: connection timeout; Voyage AI: API key invalid"
}
```

**Response Fields**:
| Field | Type | Description |
|-------|------|-------------|
| `mongodb_status` | `string` | "connected", "connection_failed", or "authentication_failed" |
| `voyage_status` | `string` | "valid", "invalid_key", or "rate_limit_exceeded" |
| `database_name` | `string` | Database name tested |
| `collections` | `array<string>` | List of collections in database (if connected) |
| `indexes_count` | `number` | Number of indexes found (if connected) |
| `error` | `string` | Error message (if any failures) |
| `message` | `string` | Success message |

**Status Codes**:
- `200 OK`: Test completed (check response fields for actual status)
- `400 Bad Request`: Invalid request body
- `500 Internal Server Error`: Unexpected error during testing

**Example**:
```bash
curl -X POST http://localhost:3333/api/settings/cloud-storage/test \
  -H "Content-Type: application/json" \
  -d '{
    "mongodb_connection_string": "mongodb+srv://user:pass@cluster.mongodb.net/",
    "mongodb_database_name": "claudetask",
    "voyage_api_key": "vo-abc123"
  }'
```

**Validation Rules**:
- MongoDB connection string must start with `mongodb+srv://` (TLS required)
- MongoDB database name must be alphanumeric with underscores/hyphens
- Voyage AI API key must start with `vo-`
- All fields are required and non-empty

---

### 3. Save Configuration

Save MongoDB Atlas and Voyage AI credentials to `.env` file.

**Endpoint**: `POST /api/settings/cloud-storage/save`

**Authentication**: None

**Request Body**:
```json
{
  "mongodb_connection_string": "mongodb+srv://username:password@cluster.mongodb.net/",
  "mongodb_database_name": "claudetask",
  "voyage_api_key": "vo-your-api-key-here"
}
```

**Request Fields**: Same as Test Connections

**Response (Success)**:
```json
{
  "success": true,
  "message": "Configuration saved to .env file",
  "restart_required": true
}
```

**Response (Failure)**:
```json
{
  "success": false,
  "error": "Failed to write to .env file: Permission denied"
}
```

**Response Fields**:
| Field | Type | Description |
|-------|------|-------------|
| `success` | `boolean` | Whether save operation succeeded |
| `message` | `string` | Success message |
| `restart_required` | `boolean` | Whether backend restart is needed (always true) |
| `error` | `string` | Error message (if failed) |

**Status Codes**:
- `200 OK`: Configuration saved successfully
- `400 Bad Request`: Invalid request body
- `500 Internal Server Error`: Failed to write to .env file

**Example**:
```bash
curl -X POST http://localhost:3333/api/settings/cloud-storage/save \
  -H "Content-Type: application/json" \
  -d '{
    "mongodb_connection_string": "mongodb+srv://user:pass@cluster.mongodb.net/",
    "mongodb_database_name": "claudetask",
    "voyage_api_key": "vo-abc123"
  }'
```

**Side Effects**:
1. Updates `.env` file with new credentials
2. Creates `.env` file if it doesn't exist
3. Preserves other environment variables
4. Backend must be restarted to use new configuration

**Security Notes**:
- `.env` file should be in `.gitignore` (never commit)
- Credentials stored in plain text on filesystem
- Only accessible by backend process
- Use appropriate file permissions (600 recommended)

---

### 4. Remove Configuration

Remove MongoDB Atlas and Voyage AI configuration from `.env` file.

**Endpoint**: `DELETE /api/settings/cloud-storage/config`

**Authentication**: None

**Response (Success)**:
```json
{
  "success": true,
  "message": "Cloud storage configuration removed from .env file",
  "restart_required": true
}
```

**Response (Failure)**:
```json
{
  "success": false,
  "error": "Failed to update .env file: File not found"
}
```

**Response Fields**:
| Field | Type | Description |
|-------|------|-------------|
| `success` | `boolean` | Whether removal succeeded |
| `message` | `string` | Success message |
| `restart_required` | `boolean` | Whether backend restart needed (always true) |
| `error` | `string` | Error message (if failed) |

**Status Codes**:
- `200 OK`: Configuration removed successfully
- `500 Internal Server Error`: Failed to update .env file

**Example**:
```bash
curl -X DELETE http://localhost:3333/api/settings/cloud-storage/config
```

**Side Effects**:
1. Removes MongoDB and Voyage AI entries from `.env`
2. Preserves other environment variables
3. Projects revert to local storage on next backend restart
4. No data is deleted (original SQLite data preserved)

**Rollback**:
After removal, all projects automatically use local storage (SQLite + ChromaDB). Original data remains intact.

---

### 5. Health Check

Check MongoDB connection health and get statistics.

**Endpoint**: `GET /api/settings/cloud-storage/health`

**Authentication**: None

**Response (Healthy)**:
```json
{
  "status": "healthy",
  "database": "claudetask",
  "collections": 5,
  "indexes": 12,
  "connection_pool": {
    "active": 2,
    "idle": 3,
    "max": 10
  },
  "last_check": "2025-11-26T10:30:00Z"
}
```

**Response (Unhealthy)**:
```json
{
  "status": "unhealthy",
  "error": "Connection timeout",
  "last_successful_check": "2025-11-26T10:00:00Z"
}
```

**Response Fields**:
| Field | Type | Description |
|-------|------|-------------|
| `status` | `string` | "healthy", "unhealthy", or "not_configured" |
| `database` | `string` | Database name (if configured) |
| `collections` | `number` | Number of collections (if healthy) |
| `indexes` | `number` | Total number of indexes (if healthy) |
| `connection_pool` | `object` | Connection pool statistics (if healthy) |
| `last_check` | `string` | ISO 8601 timestamp of this check |
| `error` | `string` | Error message (if unhealthy) |
| `last_successful_check` | `string` | Last successful health check (if unhealthy) |

**Status Codes**:
- `200 OK`: Health check completed
- `503 Service Unavailable`: MongoDB not configured or unreachable

**Example**:
```bash
curl http://localhost:3333/api/settings/cloud-storage/health
```

**Health Check Criteria**:
- MongoDB connection established within 5 seconds
- Can list collections and indexes
- Connection pool has available connections
- No authentication errors

**Monitoring**:
- Poll this endpoint every 30-60 seconds for monitoring
- Alert if status changes from "healthy" to "unhealthy"
- Display status in UI for user visibility

---

## Common Workflows

### Initial Setup

1. User enters credentials in Cloud Storage Settings UI
2. Frontend calls `POST /test` to validate credentials
3. If test passes, frontend calls `POST /save` to persist
4. User restarts backend to apply configuration
5. Projects can now be migrated to MongoDB

### Configuration Update

1. User modifies credentials in UI
2. Frontend calls `POST /test` with new credentials
3. If test passes, frontend calls `POST /save`
4. User restarts backend
5. New configuration takes effect

### Configuration Removal

1. User clicks "Remove Configuration"
2. Frontend calls `DELETE /config`
3. Credentials removed from `.env`
4. User restarts backend
5. All projects revert to local storage

### Health Monitoring

1. Frontend polls `GET /health` every 30 seconds
2. Displays status indicator (green/red dot)
3. Shows error message if unhealthy
4. Alerts user if status degrades

---

## Error Handling

### Common Errors

#### MongoDB Connection Timeout

**Response**:
```json
{
  "mongodb_status": "connection_failed",
  "error": "Connection timeout after 5 seconds"
}
```

**Solutions**:
1. Check MongoDB Atlas IP whitelist
2. Verify network connectivity
3. Ensure cluster is running
4. Check firewall settings

#### Invalid Connection String

**Response**:
```json
{
  "error": "Invalid MongoDB connection string format"
}
```

**Solutions**:
1. Verify connection string starts with `mongodb+srv://`
2. Check for typos in username/password
3. Ensure connection string includes cluster address
4. Verify format: `mongodb+srv://user:pass@cluster.mongodb.net/`

#### Voyage AI API Key Invalid

**Response**:
```json
{
  "voyage_status": "invalid_key",
  "error": "Voyage AI API key is invalid"
}
```

**Solutions**:
1. Verify key starts with `vo-`
2. Check key is active in Voyage AI dashboard
3. Ensure sufficient API credits
4. Try generating new key

#### .env File Write Failed

**Response**:
```json
{
  "success": false,
  "error": "Failed to write to .env file: Permission denied"
}
```

**Solutions**:
1. Check file permissions on `.env`
2. Ensure backend has write access to project root
3. Verify disk space available
4. Check if `.env` is locked by another process

---

## Security Considerations

### TLS Encryption

- Only `mongodb+srv://` connections accepted (TLS enforced)
- Plain `mongodb://` connections rejected
- All data encrypted in transit

### Credential Storage

- Credentials stored in `.env` file
- `.env` file should be in `.gitignore`
- Use file permissions 600 (read/write owner only)
- Never commit `.env` to version control

### API Key Masking

- API keys never returned in responses
- Only boolean status returned (configured/not configured)
- Frontend uses `type="password"` for input fields

### Input Validation

- Connection strings validated for format
- Database names validated (alphanumeric only)
- API keys validated for format (starts with vo-)
- SQL injection not applicable (no SQL queries with user input)

---

## Rate Limiting

**Current**: No rate limiting implemented (local desktop app)

**Future**: Consider rate limiting for multi-user deployments:
- 10 requests per minute per IP for test endpoint
- 5 requests per minute for save/delete endpoints
- No limit on status/health checks

---

## Testing

### Unit Tests

```python
# Test connection validation
def test_mongodb_connection_validation():
    # Valid connection string
    assert validate_mongodb_connection("mongodb+srv://user:pass@cluster.mongodb.net/")

    # Invalid format
    assert not validate_mongodb_connection("mongodb://localhost:27017")
    assert not validate_mongodb_connection("invalid-connection-string")

# Test Voyage AI key validation
def test_voyage_key_validation():
    assert validate_voyage_key("vo-abc123xyz")
    assert not validate_voyage_key("invalid-key")
    assert not validate_voyage_key("sk-openai-key")
```

### Integration Tests

```python
# Test full configuration workflow
async def test_configuration_workflow():
    # Test connections
    response = await client.post("/api/settings/cloud-storage/test", json={
        "mongodb_connection_string": VALID_MONGO_URL,
        "mongodb_database_name": "test_db",
        "voyage_api_key": VALID_VOYAGE_KEY
    })
    assert response.status_code == 200

    # Save configuration
    response = await client.post("/api/settings/cloud-storage/save", json={
        "mongodb_connection_string": VALID_MONGO_URL,
        "mongodb_database_name": "test_db",
        "voyage_api_key": VALID_VOYAGE_KEY
    })
    assert response.json()["success"] == True

    # Check status
    response = await client.get("/api/settings/cloud-storage/status")
    assert response.json()["mongodb_configured"] == True
```

---

## Related Documentation

- [MongoDB Atlas Storage](../../features/mongodb-atlas-storage.md) - Complete storage backend guide
- [CloudStorageSettings Component](../../components/CloudStorageSettings.md) - Frontend UI documentation
- [Repository Pattern](../../../claudetask/backend/app/repositories/README.md) - Storage abstraction
- [Settings API](./settings.md) - Project settings endpoints

---

**API Version**: 1.0.0
**Backend Status**: ✅ Implemented
**Testing Status**: ⏳ Manual testing complete, automated tests pending
**Documentation Status**: ✅ Complete
**Last Updated**: 2025-11-26
