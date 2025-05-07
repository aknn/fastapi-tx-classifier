# ML Infrastructure Phasing Plan

## Phase 0: MLOps & Baseline Setup (0.5–1 day)
- Add MLflow for experiment tracking
- Ensure data versioning (Git-LFS or DVC)
- Wire up basic CI/CD for model artifacts

## Phase 1: Pluggable Model + Experimentation (1–2 days)
- Define `ModelInterface` and registry in `model_registry.py`
- Implement rules-based & LLM based classifiers
- Inject A/B test flag (header or user-hash) at inference time
- Collect per-model metrics (accuracy, latency) to MLflow

## Phase 2: Explainability & Investigator UX (1–2 days)
- Add SHAP wrapper around active model
- Extend Pydantic response with `explanation: List[TokenContribution]`
- Expose `/transactions?with_explanations=true`
- Document how to interpret the "why" column in Swagger

## Phase 3: Online Learning & Drift Detection (2–3 days)
- Stream recent transactions into RedisStream
- Schedule nightly retrain via APScheduler/Cron in container
- Hot-swap model in `model_registry` on success
- Add simple drift alert (e.g. % change in accuracy) to `/health`

## Phase 4: Dashboard & Statistical Significance (1 day)
- Build lightweight dashboard endpoint for A/B results
- Run basic significance tests (χ² for classification)
- Surface "winner" model dynamically

## Implementation Notes

### Key Dependencies
- MLflow/W&B for experiment tracking
- scikit-learn for baseline models
- SHAP for explainability
- Redis for streaming storage
- FastAPI for API endpoints

### A/B Testing Integration
- Request-based model assignment
- Metrics collection (accuracy, latency, confidence)
- Simple experiment dashboard
- Statistical significance testing

### Monitoring & Alerts
- Model performance metrics
- Drift detection
- Response latency
- Training pipeline status
