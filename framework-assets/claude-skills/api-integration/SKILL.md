---
name: api-integration
description: Expert skill for seamless integration between React frontend and Python FastAPI backend with REST API patterns, axios configuration, and production-ready strategies
version: 1.0.0
tags: [api, integration, react, fastapi, frontend-backend]
---

# API Integration - React + Python FastAPI

Expert skill for seamless integration between React frontend and Python FastAPI backend in MVP projects. Master REST API patterns, axios configuration, API client architecture, error handling, state management, and production-ready integration strategies.

## Overview

This skill provides comprehensive guidance for building robust API integrations in modern web applications using React (TypeScript) on the frontend and Python FastAPI on the backend. Whether you're building a new MVP or enhancing an existing application, this skill covers everything from basic axios setup to advanced patterns like request interceptors, retry logic, and optimistic updates.

**Target Stack:**
- **Frontend**: React 18+, TypeScript, Axios
- **Backend**: Python 3.9+, FastAPI, Pydantic
- **State Management**: React Query, Context API, or Redux
- **Authentication**: JWT, OAuth2
- **Development**: Environment-based configuration, mocking, testing

## Quick Start

### Basic API Integration (5 minutes)

```typescript
// 1. Install axios
npm install axios

// 2. Create API client
// src/api/client.ts
import axios from 'axios';

export const apiClient = axios.create({
  baseURL: process.env.REACT_APP_API_URL || 'http://localhost:8000',
  headers: {
    'Content-Type': 'application/json',
  },
});

// 3. Make your first API call
// src/api/users.ts
import { apiClient } from './client';

export const getUsers = async () => {
  const response = await apiClient.get('/users');
  return response.data;
};

// 4. Use in React component
function UserList() {
  const [users, setUsers] = useState([]);

  useEffect(() => {
    getUsers().then(setUsers);
  }, []);

  return <div>{/* render users */}</div>;
}
```

### FastAPI Backend Setup

```python
# backend/app/main.py
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

# Enable CORS for React frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/users")
async def get_users():
    return [{"id": 1, "name": "John"}]
```

## Core Capabilities

This skill covers 20+ essential API integration capabilities:

### 1. API Client Configuration
- Axios instance setup and configuration
- Base URL management across environments
- Default headers and request configuration
- Timeout configuration and retry logic
- Custom axios adapters

### 2. Request/Response Interceptors
- Authentication token injection
- Request transformation and logging
- Response data normalization
- Error response handling
- Request/response timing and metrics

### 3. Error Handling Strategies
- Global error handling architecture
- HTTP status code mapping
- Network error recovery
- Retry logic with exponential backoff
- User-friendly error messages

### 4. Authentication Integration
- JWT token storage and refresh
- OAuth2 flow implementation
- Auth headers management
- Token expiration handling
- Secure credential storage

### 5. TypeScript Type Safety
- API response type definitions
- Request payload types
- Generic API client types
- Type-safe API hooks
- Pydantic model to TypeScript conversion

### 6. API State Management
- React Query integration
- Cache invalidation strategies
- Optimistic updates
- Background refetching
- Mutation handling

### 7. Loading and Error States
- Loading indicators
- Skeleton screens
- Error boundaries
- Retry UI components
- Success notifications

### 8. API Organization Patterns
- Service layer architecture
- Resource-based API modules
- API client class patterns
- Repository pattern
- Facade pattern for complex APIs

### 9. Environment Configuration
- Development vs production URLs
- Environment variable management
- Feature flags via API
- Multi-environment setup
- Local vs remote API switching

### 10. API Mocking and Testing
- MSW (Mock Service Worker) setup
- API response mocking
- Test fixtures and factories
- Integration testing
- E2E testing with mocked APIs

### 11. File Upload/Download
- Multipart form data handling
- File upload progress tracking
- Chunked file uploads
- Download with progress
- File type validation

### 12. Real-time Communication
- WebSocket integration
- Server-Sent Events (SSE)
- Polling strategies
- Real-time data synchronization
- Connection management

### 13. Request Cancellation
- AbortController usage
- Cancelling pending requests
- Cleanup in useEffect
- Request deduplication
- Race condition prevention

### 14. Data Transformation
- Response data mapping
- Request payload formatting
- Date/time serialization
- Nested data normalization
- Pagination data handling

### 15. Performance Optimization
- Request batching
- Response caching
- Debouncing and throttling
- Lazy loading data
- Prefetching strategies

### 16. Security Best Practices
- CSRF token handling
- XSS prevention
- Secure headers
- Input sanitization
- HTTPS enforcement

### 17. API Versioning
- URL-based versioning
- Header-based versioning
- Backward compatibility
- Migration strategies
- Deprecation handling

### 18. Rate Limiting and Throttling
- Client-side rate limiting
- Retry-After header handling
- Request queue management
- Backoff strategies
- Usage quota tracking

### 19. Monitoring and Logging
- API call logging
- Error tracking (Sentry)
- Performance monitoring
- Analytics integration
- Debug mode utilities

### 20. Advanced Patterns
- GraphQL integration
- API composition
- Backend-for-Frontend (BFF)
- API gateway patterns
- Microservices integration

## Documentation

Explore comprehensive documentation for deep understanding:

**Core Concepts**: See [docs/core-concepts.md](docs/core-concepts.md)
- Axios fundamentals
- HTTP request lifecycle
- RESTful API principles
- Client-server communication
- Request/response anatomy
- CORS and preflight requests
- Content negotiation
- API contracts and OpenAPI

**Best Practices**: See [docs/best-practices.md](docs/best-practices.md)
- API client architecture
- Error handling patterns
- Security considerations
- Performance optimization
- Code organization
- Testing strategies
- Documentation standards
- Deployment checklist

**Patterns**: See [docs/patterns.md](docs/patterns.md)
- Service layer pattern
- Repository pattern
- Factory pattern for API clients
- Singleton vs multiple instances
- Adapter pattern
- Facade pattern
- Observer pattern for real-time
- Strategy pattern for auth

**Advanced Topics**: See [docs/advanced-topics.md](docs/advanced-topics.md)
- Request interceptor chains
- Response transformation pipelines
- Custom axios adapters
- Retry logic with exponential backoff
- Request deduplication
- Offline-first strategies
- API composition patterns
- WebSocket integration

**Troubleshooting**: See [docs/troubleshooting.md](docs/troubleshooting.md)
- CORS errors and solutions
- Authentication failures
- Network timeouts
- 4xx and 5xx error handling
- Type mismatch issues
- Environment configuration problems
- React Query cache issues
- Common FastAPI errors

**API Reference**: See [docs/api-reference.md](docs/api-reference.md)
- Axios API complete reference
- Custom API client methods
- React Query hooks
- TypeScript interfaces
- Environment variables
- Configuration options
- Utility functions
- Helper methods

## Examples

### Basic Examples
Start with fundamental integration patterns:

- [Example 1: Basic GET Request](examples/basic/example-1.md) - Fetch data from API endpoint
- [Example 2: POST Request with Data](examples/basic/example-2.md) - Submit form data to API
- [Example 3: API Client Setup](examples/basic/example-3.md) - Configure axios instance

### Intermediate Examples
Explore more complex integration scenarios:

- [Pattern 1: Authentication Flow](examples/intermediate/pattern-1.md) - JWT login and token refresh
- [Pattern 2: Error Handling](examples/intermediate/pattern-2.md) - Global error management
- [Pattern 3: React Query Integration](examples/intermediate/pattern-3.md) - State management with caching

### Advanced Examples
Master expert-level patterns:

- [Advanced 1: Request Interceptors](examples/advanced/advanced-pattern-1.md) - Auth, logging, transformation
- [Advanced 2: Optimistic Updates](examples/advanced/advanced-pattern-2.md) - Instant UI feedback
- [Advanced 3: WebSocket Integration](examples/advanced/advanced-pattern-3.md) - Real-time bidirectional communication

## Templates

Ready-to-use templates for rapid development:

- [Template 1: Basic API Client](templates/template-1.md) - Simple axios setup with TypeScript
- [Template 2: Full-Featured API Client](templates/template-2.md) - Auth, interceptors, error handling
- [Template 3: Production-Ready Setup](templates/template-3.md) - Complete integration with monitoring

## Resources

Additional resources for API integration mastery:

- [Quality Checklists](resources/checklists.md) - Pre-deployment validation
- [Complete Glossary](resources/glossary.md) - API integration terminology
- [External References](resources/references.md) - Official docs and tutorials
- [Step-by-Step Workflows](resources/workflows.md) - Common integration workflows

## Common Integration Scenarios

### Scenario 1: New MVP Project
Starting from scratch? Follow this path:
1. Read [docs/core-concepts.md](docs/core-concepts.md) for fundamentals
2. Use [Template 1: Basic API Client](templates/template-1.md) for initial setup
3. Study [Example 1: Basic GET Request](examples/basic/example-1.md)
4. Add authentication with [Pattern 1: Authentication Flow](examples/intermediate/pattern-1.md)
5. Review [resources/checklists.md](resources/checklists.md) before deploying

### Scenario 2: Adding API to Existing Project
Integrating API into existing React app:
1. Review [docs/patterns.md](docs/patterns.md) for architecture patterns
2. Implement [Template 2: Full-Featured API Client](templates/template-2.md)
3. Add error handling from [Pattern 2: Error Handling](examples/intermediate/pattern-2.md)
4. Optimize with [docs/advanced-topics.md](docs/advanced-topics.md)

### Scenario 3: Improving Existing API Integration
Enhancing current implementation:
1. Audit current setup against [docs/best-practices.md](docs/best-practices.md)
2. Add interceptors from [Advanced 1: Request Interceptors](examples/advanced/advanced-pattern-1.md)
3. Implement caching with [Pattern 3: React Query Integration](examples/intermediate/pattern-3.md)
4. Add real-time features from [Advanced 3: WebSocket Integration](examples/advanced/advanced-pattern-3.md)

### Scenario 4: Troubleshooting API Issues
Debugging integration problems:
1. Check [docs/troubleshooting.md](docs/troubleshooting.md) for common issues
2. Review error handling in [Pattern 2: Error Handling](examples/intermediate/pattern-2.md)
3. Validate CORS setup in [docs/core-concepts.md](docs/core-concepts.md)
4. Test with mocks from [resources/workflows.md](resources/workflows.md)

## Usage in Claude Code

This skill is automatically available when working with React + FastAPI projects. Claude Code will:

- Suggest appropriate API patterns for your use case
- Generate type-safe API client code
- Implement error handling and retry logic
- Configure interceptors for authentication
- Set up React Query or other state management
- Create TypeScript types from FastAPI models
- Handle CORS and security configurations
- Optimize API performance and caching

**Example invocation:**
```
"Implement a user authentication API client with JWT tokens,
request interceptors, and React Query integration"
```

Claude Code will use this skill to create production-ready API integration code following all best practices.

## Integration with Backend

This skill assumes a FastAPI backend with:
- RESTful endpoints returning JSON
- Pydantic models for request/response validation
- CORS middleware configured
- JWT or OAuth2 authentication
- OpenAPI documentation at `/docs`

Backend setup examples are included in each pattern and example for complete full-stack integration.

## Technology Prerequisites

**Frontend:**
- Node.js 16+ and npm/yarn
- React 18+
- TypeScript 4.5+
- Axios 1.0+

**Backend:**
- Python 3.9+
- FastAPI 0.95+
- Uvicorn (ASGI server)
- Pydantic v2

**Optional:**
- React Query (TanStack Query) for state management
- MSW for API mocking
- Zod for runtime validation

## Learning Path

### Beginner (0-2 hours)
1. Read [docs/core-concepts.md](docs/core-concepts.md) - Understand fundamentals
2. Complete [Example 1: Basic GET Request](examples/basic/example-1.md)
3. Complete [Example 2: POST Request](examples/basic/example-2.md)
4. Use [Template 1: Basic API Client](templates/template-1.md)

### Intermediate (2-5 hours)
5. Study [docs/patterns.md](docs/patterns.md) - Learn architecture patterns
6. Implement [Pattern 1: Authentication Flow](examples/intermediate/pattern-1.md)
7. Add [Pattern 2: Error Handling](examples/intermediate/pattern-2.md)
8. Explore [Pattern 3: React Query Integration](examples/intermediate/pattern-3.md)
9. Review [docs/best-practices.md](docs/best-practices.md)

### Advanced (5+ hours)
10. Master [Advanced 1: Request Interceptors](examples/advanced/advanced-pattern-1.md)
11. Implement [Advanced 2: Optimistic Updates](examples/advanced/advanced-pattern-2.md)
12. Add [Advanced 3: WebSocket Integration](examples/advanced/advanced-pattern-3.md)
13. Study [docs/advanced-topics.md](docs/advanced-topics.md)
14. Build production app with [Template 3: Production-Ready Setup](templates/template-3.md)
15. Master troubleshooting with [docs/troubleshooting.md](docs/troubleshooting.md)

## Key Principles

1. **Type Safety**: Use TypeScript for all API interactions
2. **Error Handling**: Never fail silently, always inform users
3. **Loading States**: Show feedback for all async operations
4. **Security**: Protect credentials, validate inputs, use HTTPS
5. **Performance**: Cache responses, debounce requests, optimize payloads
6. **Maintainability**: Organize code, document APIs, write tests
7. **User Experience**: Optimistic updates, offline support, retry logic
8. **Monitoring**: Log errors, track performance, gather metrics

## Next Steps

After mastering this skill, explore:
- GraphQL integration for more flexible APIs
- Offline-first architecture with service workers
- Advanced caching strategies with SWR or React Query
- API gateway patterns for microservices
- Server-side rendering with Next.js and API routes
- Real-time collaboration with WebSockets and CRDTs

---

**Skill Version**: 1.0.0
**Last Updated**: 2025-10-31
**Maintained by**: Claude Code Skills Team
