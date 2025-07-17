# Safe Python Script Execution Service

A secure API service that allows users to execute Python scripts in a sandboxed environment using nsjail.

## Features

- **Secure Execution**: Uses nsjail for sandboxing to prevent malicious code execution
- **Simple API**: RESTful endpoint for script execution
- **Docker Ready**: Containerized for easy deployment
- **Cloud Run Compatible**: Optimized for Google Cloud Run deployment
- **Input Validation**: Basic validation for script structure and content

## Quick Start

### Live Cloud Run Service

**Service URL**: `https://safe-python-exec-16734073749.europe-west1.run.app`

**Test the live service now:**
```bash
# Health check
curl https://safe-python-exec-16734073749.europe-west1.run.app/health

# Execute a Python script
curl -X POST https://safe-python-exec-16734073749.europe-west1.run.app/execute \
  -H "Content-Type: application/json" \
  -d '{
    "script": "import pandas as pd\nimport numpy as np\ndef main():\n    df = pd.DataFrame({\"numbers\": [1, 2, 3, 4, 5]})\n    return {\"sum\": int(df[\"numbers\"].sum()), \"mean\": float(df[\"numbers\"].mean())}"
  }'

# Run comprehensive test suite
./test_service.sh https://safe-python-exec-16734073749.europe-west1.run.app
```

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
curl -X POST https://safe-python-exec-16734073749.europe-west1.run.app/execute \
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

- **nsjail Sandboxing**: **IMPLEMENTED** - Uses Google's nsjail for robust process isolation
- **Resource Limits**: CPU (30s), memory (512MB), file size (1MB), process count (50) limits enforced
- **Network Isolation**: Disabled network namespace for container compatibility  
- **File System Restrictions**: Read-only access to system directories
- **Process Isolation**: Proper process sandboxing with nsjail's security features
- **Container Compatible**: Configured to work in Docker and Cloud Run environments

## Supported Libraries

The execution environment includes a comprehensive set of pre-installed libraries:

### Scientific Computing & Data Analysis
- `pandas` - Data manipulation and analysis
- `numpy` - Numerical computing
- `scipy` - Scientific computing algorithms
- `matplotlib` - Plotting and visualization
- `seaborn` - Statistical data visualization

### Data Processing & I/O
- `openpyxl` - Excel file reading/writing
- `xlsxwriter` - Excel file creation
- `python-dateutil` - Advanced date parsing
- `pytz` - Timezone handling

### Web & Network
- `requests` - HTTP library
- `urllib3` - HTTP client
- `beautifulsoup4` - HTML/XML parsing
- `lxml` - XML/HTML parser

### Data Validation & Serialization
- `jsonschema` - JSON schema validation
- `json` - JSON handling (built-in)

### Standard Libraries (with restrictions)
- `os` (limited operations)
- `math`
- `datetime`
- `collections`
- `io`
- `sys` (limited)

## Architecture

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Client        │    │   Flask API     │    │   nsjail        │
│                 │───▶│                 │───▶│   Sandbox       │
│   (cURL, etc.)  │    │   /execute      │    │   Python Exec   │
└─────────────────┘    └─────────────────┘    └─────────────────┘
```

### nsjail Implementation Details

- **Sandboxing Tool**: Google's nsjail (v3.4+) compiled from source
- **Security Configuration**: Resource limits without privileged namespaces for container compatibility
- **Process Isolation**: Each script execution runs in an isolated process environment
- **Resource Enforcement**: Hard limits on CPU time, memory usage, file operations, and process count
- **Container Optimized**: Designed to work in Docker containers and Cloud Run without requiring privileged mode

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

# Run comprehensive library test
python3 test_libraries.py http://localhost:8080

# Test all functionality with existing test suite
./test_service.sh http://localhost:8080
```
