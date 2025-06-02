# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added
- Initial FastAPI transaction classifier implementation
- Redis integration for transaction storage
- Rule-based classification logic
- RESTful API endpoints for transaction management
- Comprehensive test suite with performance benchmarks
- Docker containerization support
- CI/CD pipeline with GitHub Actions

### Performance Metrics
- Rule-based classifier baseline accuracy: TBD
- API response time (P95): TBD
- Throughput (req/sec): TBD

## [0.1.0] - 2025-06-02

### Added
- Project structure and initial implementation
- Basic transaction classification endpoints
- Redis client integration
- Configuration management
- Error handling and logging
- Development environment setup

### Architecture
- Clean package structure with `fastapi_tx_classifier/`
- Modular router design for API endpoints
- Dependency injection for Redis connections
- Pydantic models for data validation
- Centralized configuration management

---

## Performance Tracking

| Version | Accuracy | Precision | Recall | F1-Score | Notes |
|---------|----------|-----------|---------|----------|-------|
| 0.1.0   | TBD      | TBD       | TBD     | TBD      | Baseline rule-based |

## Future Improvements

- [ ] Machine learning model integration
- [ ] Enhanced feature engineering
- [ ] Model versioning and A/B testing
- [ ] Real-time performance monitoring
- [ ] Advanced caching strategies
