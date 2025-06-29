# AlphaGenome Backend API

This is the Python backend service for the AlphaGenome webapp, deployed on Render.

## Features

- Full AlphaGenome Python library integration
- Variant effect prediction
- RNA expression analysis
- Splicing and chromatin accessibility predictions
- CORS-enabled for frontend integration

## API Endpoints

- `GET /` - Service information
- `GET /health` - Health check
- `POST /api/analyze_snps` - Analyze genetic variants

## Deployment

This service is deployed on Render and provides the computational backend for AlphaGenome analysis.

## Environment Variables

- `ALPHAGENOME_API_KEY` - Your AlphaGenome API key from DeepMind
- `PORT` - Port to run the service (default: 5000)