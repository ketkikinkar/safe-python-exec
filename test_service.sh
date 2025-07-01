#!/bin/bash

# Safe Python Script Execution Service - Test Suite
# Usage: ./test_service.sh [URL]
# Default URL: http://localhost:8080 (for local testing)
# For Cloud Run: ./test_service.sh https://your-service-url

BASE_URL=${1:-"http://localhost:8080"}

echo "🧪 Testing Safe Python Script Execution Service"
echo "📍 Base URL: $BASE_URL"
echo "================================================"

# Test 1: Health Check
echo "🔍 Test 1: Health Check"
curl -s "$BASE_URL/health" | jq .
echo -e "\n"

# Test 2: Simple Script
echo "🔍 Test 2: Simple Script Execution"
curl -s -X POST "$BASE_URL/execute" \
  -H "Content-Type: application/json" \
  -d '{"script": "def main():\n    return {\"message\": \"Hello, World!\", \"status\": \"success\"}"}' | jq .
echo -e "\n"

# Test 3: Script with Print Statements
echo "🔍 Test 3: Script with Print Statements (stdout capture)"
curl -s -X POST "$BASE_URL/execute" \
  -H "Content-Type: application/json" \
  -d '{"script": "def main():\n    print(\"Processing data...\")\n    print(\"Calculations complete!\")\n    return {\"result\": 42, \"operation\": \"calculation\"}"}' | jq .
echo -e "\n"

# Test 4: Pandas and Numpy Test
echo "🔍 Test 4: Pandas and Numpy Support"
curl -s -X POST "$BASE_URL/execute" \
  -H "Content-Type: application/json" \
  -d '{"script": "import pandas as pd\nimport numpy as np\ndef main():\n    df = pd.DataFrame({\"A\": [1, 2, 3], \"B\": [4, 5, 6]})\n    arr = np.array([1, 2, 3, 4, 5])\n    return {\"dataframe_shape\": df.shape, \"array_sum\": int(arr.sum()), \"mean\": float(arr.mean())}"}' | jq .
echo -e "\n"

# Test 5: JSON Libraries
echo "🔍 Test 5: JSON and Math Libraries"
curl -s -X POST "$BASE_URL/execute" \
  -H "Content-Type: application/json" \
  -d '{"script": "import json\nimport math\ndef main():\n    data = {\"numbers\": [1, 2, 3, 4, 5]}\n    return {\"json_test\": json.dumps(data), \"sqrt_16\": math.sqrt(16), \"pi\": round(math.pi, 2)}"}' | jq .
echo -e "\n"

# Test 6: Error Handling - Missing main function
echo "🔍 Test 6: Error Handling - Missing main()"
curl -s -X POST "$BASE_URL/execute" \
  -H "Content-Type: application/json" \
  -d '{"script": "def other_function():\n    return \"no main function\""}' | jq .
echo -e "\n"

# Test 7: Security - Dangerous operations blocked
echo "🔍 Test 7: Security - Dangerous Operations Blocked"
curl -s -X POST "$BASE_URL/execute" \
  -H "Content-Type: application/json" \
  -d '{"script": "import os\ndef main():\n    os.system(\"ls\")\n    return {\"result\": \"hacked\"}"}' | jq .
echo -e "\n"

# Test 8: Security - eval() blocked
echo "🔍 Test 8: Security - eval() Blocked"
curl -s -X POST "$BASE_URL/execute" \
  -H "Content-Type: application/json" \
  -d '{"script": "def main():\n    eval(\"print(\\\"hack\\\")\")\n    return {\"result\": \"hacked\"}"}' | jq .
echo -e "\n"

echo "✅ Test Suite Complete!"
echo "📊 Summary: If all tests show expected results, your service is working correctly!" 