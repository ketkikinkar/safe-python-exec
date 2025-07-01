# Safe Python Script Execution Service

A secure API service that allows users to execute Python scripts in a sandboxed environment using nsjail.

## Features

- **Secure Execution**: Uses nsjail for sandboxing to prevent malicious code execution
- **Simple API**: RESTful endpoint for script execution
- **Docker Ready**: Containerized for easy deployment
- **Cloud Run Compatible**: Optimized for Google Cloud Run deployment
- **Input Validation**: Basic validation for script structure and content

## Quick Start

### Local Development

1. Build the Docker image:
```bash
docker build -t python-executor .
```

2. Run the service:
```bash
docker run -p 8080:8080 python-executor
```

3. Test with cURL:
```bash
curl -X POST http://localhost:8080/execute \
  -H "Content-Type: application/json" \
  -d '{
    "script": "import json\ndef main():\n    return {\"message\": \"Hello, World!\", \"numbers\": [1, 2, 3, 4, 5]}"
  }'
```

### Cloud Run Deployment

1. Build and push to Google Container Registry:
```bash
docker build -t gcr.io/YOUR_PROJECT_ID/python-executor .
docker push gcr.io/YOUR_PROJECT_ID/python-executor
```

2. Deploy to Cloud Run:
```bash
gcloud run deploy python-executor \
  --image gcr.io/YOUR_PROJECT_ID/python-executor \
  --platform managed \
  --region us-central1 \
  --allow-unauthenticated
```

3. Test with the deployed URL:
```bash
curl -X POST https://YOUR_SERVICE_URL/execute \
  -H "Content-Type: application/json" \
  -d '{
    "script": "import json\ndef main():\n    return {\"message\": \"Hello from Cloud Run!\", \"status\": \"success\"}"
  }'
```

## API Reference

### POST /execute

Executes a Python script and returns the result.

**Request Body:**
```json
{
  "script": "def main():\n    return {\"result\": \"success\"}"
}
```

**Response:**
```json
{
  "result": {"result": "success"},
  "stdout": "Any print statements output here"
}
```

**Requirements:**
- Script must contain a `main()` function
- `main()` function must return a JSON-serializable object
- Script will be executed in a sandboxed environment

**Error Responses:**
- `400 Bad Request`: Invalid script format or missing main() function
- `500 Internal Server Error`: Execution error or non-JSON return value

## Security Features

- **nsjail Sandboxing**: Isolates script execution from the host system
- **Resource Limits**: CPU and memory constraints
- **Network Isolation**: No network access by default
- **File System Restrictions**: Limited file system access
- **Process Isolation**: Prevents access to host processes

## Supported Libraries

The execution environment includes:
- Standard Python libraries
- `os` (with restrictions)
- `pandas`
- `numpy`
- `json`
- `math`
- `datetime`
- `collections`

## Architecture

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Client        │    │   Flask API     │    │   nsjail        │
│                 │───▶│                 │───▶│   Sandbox       │
│   (cURL, etc.)  │    │   /execute      │    │   Python Exec   │
└─────────────────┘    └─────────────────┘    └─────────────────┘
```

## Development

### Prerequisites

- Docker
- Python 3.9+
- nsjail (included in Docker image)

### Local Setup

1. Clone the repository
2. Build the Docker image
3. Run the service
4. Test with the provided examples

### Testing

```bash
# Test basic functionality
curl -X POST http://localhost:8080/execute \
  -H "Content-Type: application/json" \
  -d '{
    "script": "import json\ndef main():\n    return {\"test\": \"passed\"}"
  }'

# Test with pandas
curl -X POST http://localhost:8080/execute \
  -H "Content-Type: application/json" \
  -d '{
    "script": "import pandas as pd\ndef main():\n    df = pd.DataFrame({\"A\": [1, 2, 3]})\n    return {\"shape\": df.shape[0]}"
  }'
```

## License

MIT License 