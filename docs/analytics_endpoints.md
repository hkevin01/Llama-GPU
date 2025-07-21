# Analytics Endpoints & Metrics

This document describes the analytics endpoints and metrics tracked in the Llama-GPU project.

## Endpoints
- `/api/usage` — Logs API usage events to `logs/api_requests.log`
- `/api/performance` — Reports backend performance metrics
- `/api/errors` — Tracks error events and logs to `logs/test_output.log`

## Metrics Tracked
- Request count, latency, and error rate per backend (CPU, CUDA, ROCm)
- Resource utilization (GPU/CPU/memory)
- Model inference time and throughput
- User/session analytics (if enabled)

## Logging
- All analytics logs are stored in the `logs/` folder for review.
- Automated reports can be generated from these logs for monitoring and optimization.

---
_Last updated: July 21, 2025_
