# Architecture Overview

This document outlines the architectural decisions and design patterns used in the FastAPI Transaction Classifier.

## System Architecture

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Client Apps   │    │   Load Balancer │    │   Monitoring    │
│  (Web, Mobile)  │◄──►│    (Optional)   │◄──►│   (Grafana)     │
└─────────────────┘    └─────────────────┘    └─────────────────┘
                                │
                                ▼
┌─────────────────────────────────────────────────────────────────┐
│                        FastAPI Application                      │
├─────────────────┬─────────────────┬─────────────────────────────┤
│   API Routers   │   Core Logic    │       Data Models           │
│                 │                 │                             │
│ • /transactions │ • Classification│ • Transaction               │
│ • /classify     │ • Validation    │ • TransactionCategory       │
│ • /system       │ • Error Handling│ • Configuration             │
│ • /messages     │ • Logging       │                             │
└─────────────────┴─────────────────┴─────────────────────────────┘
                                │
                                ▼
┌─────────────────────────────────────────────────────────────────┐
│                      Data Storage Layer                         │
├─────────────────┬─────────────────┬─────────────────────────────┤
│     Redis       │   File System   │       Future: DB            │
│                 │                 │                             │
│ • Transactions  │ • Configuration │ • PostgreSQL/MongoDB        │
│ • Cache         │ • Logs          │ • Model Artifacts           │
│ • Session Data  │ • Static Files  │ • Analytics Data            │
└─────────────────┴─────────────────┴─────────────────────────────┘
```

## Design Decisions

### 1. Package Structure

**Decision**: Single package (`fastapi_tx_classifier/`) with clear module separation

**Rationale**:
- **Single Source of Truth**: All core logic in one package prevents duplication
- **Import Clarity**: Relative imports within package, absolute imports from outside
- **Distribution Ready**: Easy to package and distribute via PyPI
- **Testing Isolation**: Clear separation between application code and tests

### 2. Router-Based API Design

**Decision**: Modular routers (`/routers/`) rather than monolithic main.py

**Rationale**:
- **Separation of Concerns**: Each router handles specific domain logic
- **Scalability**: Easy to add new endpoints without bloating main application
- **Team Development**: Different developers can work on different routers
- **Testing**: Each router can be tested independently

### 3. Dependency Injection Pattern

**Decision**: FastAPI's dependency injection for Redis connections

**Rationale**:
- **Testability**: Easy to mock dependencies in tests
- **Resource Management**: Automatic connection pooling and cleanup
- **Configuration**: Environment-specific configurations without code changes
- **Monitoring**: Centralized place to add connection monitoring

### 4. Pydantic Data Models

**Decision**: Comprehensive Pydantic models for all data structures

**Rationale**:
- **Type Safety**: Compile-time and runtime type checking
- **Validation**: Automatic data validation with clear error messages
- **Documentation**: Self-documenting API with OpenAPI schema generation
- **Serialization**: Consistent JSON serialization/deserialization

### 5. Configuration Management

**Decision**: Centralized configuration with environment variable support

**Rationale**:
- **Environment Parity**: Same code runs in dev, staging, and production
- **Security**: Sensitive data via environment variables, not code
- **Flexibility**: Easy to adjust settings without code deployment
- **Validation**: Configuration validation at startup

## Data Flow

### Transaction Classification Flow

```
1. Client Request
   ↓
2. FastAPI Router (validation)
   ↓
3. Classification Logic
   ↓
4. Redis Storage
   ↓
5. Response to Client
```

### Transaction Retrieval Flow

```
1. Client Request
   ↓
2. FastAPI Router
   ↓
3. Redis Query
   ↓
4. Data Transformation
   ↓
5. JSON Response
```

## Error Handling Strategy

### Layered Error Handling

1. **Pydantic Validation**: Catches malformed input data
2. **Business Logic**: Custom exceptions for domain-specific errors
3. **Infrastructure**: Redis connection, file system errors
4. **Global Handler**: Catches unexpected exceptions

### Error Response Format

```json
{
  "error": {
    "code": "VALIDATION_ERROR",
    "message": "Invalid transaction data",
    "details": {
      "field": "amount",
      "issue": "must be a positive number"
    }
  }
}
```

## Performance Considerations

### Caching Strategy

- **Redis**: Primary cache for frequently accessed transactions
- **Application Level**: Configuration and model artifacts cached in memory
- **CDN**: Static assets served via CDN (future)

### Database Optimization

- **Connection Pooling**: Redis connection pool for concurrent requests
- **Indexing**: Strategic indexing on transaction categories and timestamps
- **Pagination**: Large datasets returned with cursor-based pagination

## Security Architecture

### Authentication & Authorization

- **API Keys**: For service-to-service communication
- **Rate Limiting**: Prevent abuse and ensure fair usage
- **Input Validation**: All inputs validated before processing
- **CORS**: Configured for web client integration

### Data Protection

- **Encryption**: Sensitive data encrypted at rest and in transit
- **Logging**: No sensitive data in logs
- **Audit Trail**: All data modifications logged
- **Backup**: Regular automated backups with encryption

## Monitoring & Observability

### Metrics

- **Application Metrics**: Response times, error rates, throughput
- **Business Metrics**: Classification accuracy, category distribution
- **Infrastructure Metrics**: Redis performance, memory usage, CPU

### Logging

- **Structured Logging**: JSON format for easy parsing
- **Log Levels**: Appropriate levels for different environments
- **Correlation IDs**: Request tracing across services
- **Performance Logging**: Slow query identification

## Deployment Architecture

### Container Strategy

- **Multi-stage Builds**: Optimized Docker images
- **Base Images**: Official Python slim images for security
- **Layer Caching**: Efficient image builds and deployments
- **Health Checks**: Kubernetes/Docker health check endpoints

### Scaling Strategy

- **Horizontal Scaling**: Stateless application design
- **Load Balancing**: Round-robin or least-connections
- **Auto-scaling**: CPU/memory-based scaling rules
- **Circuit Breakers**: Prevent cascade failures

## Future Architectural Considerations

### Machine Learning Integration

- **Model Serving**: Separate ML model serving layer
- **Feature Store**: Centralized feature management
- **A/B Testing**: Framework for model comparison
- **Real-time Inference**: Low-latency prediction pipeline

### Microservices Evolution

- **Service Decomposition**: Split by business domain
- **Event-Driven Architecture**: Async communication via message queues
- **API Gateway**: Centralized routing and cross-cutting concerns
- **Service Mesh**: Advanced traffic management and security
