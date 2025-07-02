#!/usr/bin/env python3
"""
Safe Python Script Execution Service

A Flask-based API service that executes Python scripts in a sandboxed environment
using nsjail for security.
"""

import json
import subprocess
import os
import re
import sys
from flask import Flask, request, jsonify
from werkzeug.exceptions import BadRequest

app = Flask(__name__)

# nsjail configuration (Cloud Run compatible - minimal privileged operations)
NSJAIL_CONFIG = [
    '/usr/local/bin/nsjail',
    '--mode', 'o',  # Once mode - run once and exit
    '--time_limit', '30',  # 30 seconds timeout
    '--log', '/tmp/nsjail.log',  # Log to temp directory
    '--disable_proc',  # Disable /proc access
    # Remove ALL rlimit options - they require elevated privileges in Cloud Run
    # Cloud Run container limits will handle resource constraints instead
    '--disable_clone_newnet',    # Disable network namespace
    '--disable_clone_newuser',   # Disable user namespace
    '--disable_clone_newns',     # Disable mount namespace
    '--disable_clone_newpid',    # Disable PID namespace
    '--disable_clone_newipc',    # Disable IPC namespace
    '--disable_clone_newuts',    # Disable UTS namespace
    '--disable_clone_newcgroup', # Disable cgroup namespace
    # Pass essential environment variables for Python libraries
    '--env', 'PYTHONPATH=/usr/local/lib/python3.11/site-packages:/usr/lib/python3/dist-packages',
    '--env', 'PATH=/usr/local/bin:/usr/bin:/bin',
    '--env', 'HOME=/tmp',
    '--env', 'LANG=C.UTF-8',
    '--env', 'LC_ALL=C.UTF-8',
    '--env', 'OPENBLAS_NUM_THREADS=1',  # Limit OpenBLAS threads for container compatibility
    '--env', 'OMP_NUM_THREADS=1',       # Limit OpenMP threads
    '--env', 'NUMBA_DISABLE_JIT=1',     # Disable numba JIT compilation
    '--env', 'MPLBACKEND=Agg',          # Non-interactive matplotlib backend
    '--env', 'PYTHONDONTWRITEBYTECODE=1',  # Don't create .pyc files
    '--env', 'PYTHONIOENCODING=utf-8',     # Set Python IO encoding
    '--env', 'TZ=UTC',                     # Set timezone
    '--env', 'TMPDIR=/tmp',                # Temp directory
    '--quiet',  # Reduce verbosity
    '--',  # End of nsjail options
    '/usr/bin/python3',
    '-c'
]

def validate_script(script):
    """
    Validate the Python script for security and structure.
    
    Args:
        script (str): The Python script to validate
        
    Returns:
        bool: True if valid, raises BadRequest if invalid
    """
    if not script or not isinstance(script, str):
        raise BadRequest("Script must be a non-empty string")
    
    # Check for main function
    if 'def main()' not in script:
        raise BadRequest("Script must contain a 'main()' function")
    
    # Check for dangerous imports/operations
    dangerous_patterns = [
        r'import\s+subprocess',
        r'from\s+os\s+import',  # Block dangerous os imports
        r'os\.system',          # Block dangerous os operations
        r'os\.popen',
        r'os\.exec',
        r'os\.spawn',
        r'__import__\s*\(',
        r'eval\s*\(',
        r'exec\s*\(',
        r'compile\s*\(',
        r'open\s*\(',
        r'file\s*\(',
        r'input\s*\(',
        r'raw_input\s*\(',
        r'globals\s*\(',
        r'locals\s*\(',
        r'vars\s*\(',
        r'dir\s*\(',
        r'help\s*\(',
        r'breakpoint\s*\(',
        r'quit\s*\(',
        r'exit\s*\(',
    ]
    
    for pattern in dangerous_patterns:
        if re.search(pattern, script, re.MULTILINE | re.IGNORECASE):
            raise BadRequest(f"Dangerous operation detected: {pattern}")
    
    # Check script length
    if len(script) > 10000:  # 10KB limit
        raise BadRequest("Script too long (max 10KB)")
    
    return True



def execute_script_safely(script):
    """
    Execute the Python script in a sandboxed environment using nsjail.
    
    Args:
        script (str): The Python script to execute
        
    Returns:
        tuple: (result, stdout, stderr)
    """
    # Prepare the execution script that will run inside nsjail
    exec_script = f"""
import sys
import json
import io
from contextlib import redirect_stdout

# Redirect stdout to capture print statements
stdout_capture = io.StringIO()

try:
    # Execute the user script
    exec('''{script}''')
    
    # Get the main function and execute it with stdout capture
    if 'main' in globals():
        with redirect_stdout(stdout_capture):
            result = main()
        
        # Validate that result is JSON serializable
        json.dumps(result)
        
        # Return result and stdout
        output = {{
            'result': result,
            'stdout': stdout_capture.getvalue()
        }}
        print(json.dumps(output))
    else:
        print(json.dumps({{
            'error': 'main() function not found'
        }}))
        sys.exit(1)
        
except Exception as e:
    print(json.dumps({{
        'error': str(e)
    }}))
    sys.exit(1)
"""
    
    try:
        # Build nsjail command
        nsjail_cmd = NSJAIL_CONFIG + [exec_script]
        
        # Execute with nsjail and timeout
        process = subprocess.run(
            nsjail_cmd,
            capture_output=True,
            text=True,
            timeout=35  # 5 seconds more than nsjail's internal timeout
        )
        
        if process.returncode != 0:
            # Check if it's a timeout or other error
            if process.returncode == 109:  # SIGKILL - likely timeout
                raise Exception("Script execution timeout (30 seconds)")
            else:
                error_msg = f"nsjail failed with code {process.returncode}"
                if process.stderr:
                    error_msg += f": {process.stderr}"
                if process.stdout:
                    error_msg += f" (stdout: {process.stdout})"
                raise Exception(error_msg)
        
        # Parse the output
        try:
            output = json.loads(process.stdout.strip())
            if 'error' in output:
                raise Exception(output['error'])
            return output['result'], output['stdout'], process.stderr
        except json.JSONDecodeError:
            raise Exception("Invalid output format from script execution")
            
    except subprocess.TimeoutExpired:
        raise Exception("Script execution timeout (35 seconds)")

@app.route('/', methods=['GET'])
def root():
    """Root endpoint with service information."""
    return jsonify({
        'service': 'Safe Python Script Execution Service',
        'version': '1.0.0',
        'endpoints': {
            '/health': 'GET - Health check',
            '/execute': 'POST - Execute Python script'
        },
        'usage': {
            'health_check': 'GET /health',
            'execute_script': 'POST /execute with JSON body: {"script": "def main():\\n    return {\\"result\\": \\"success\\"}"}'
        },
        'documentation': 'https://github.com/ketkikinkar/safe-python-exec'
    })

@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint."""
    return jsonify({'status': 'healthy', 'service': 'python-executor'})

@app.route('/execute', methods=['POST'])
def execute():
    """
    Execute a Python script and return the result.
    
    Expected JSON payload:
    {
        "script": "def main():\n    return {'result': 'success'}"
    }
    
    Returns:
    {
        "result": {...},
        "stdout": "..."
    }
    """
    try:
        # Parse request
        if not request.is_json:
            raise BadRequest("Content-Type must be application/json")
        
        data = request.get_json()
        if not data or 'script' not in data:
            raise BadRequest("Request must contain 'script' field")
        
        script = data['script']
        
        # Validate script
        validate_script(script)
        
        # Execute script safely
        result, stdout, stderr = execute_script_safely(script)
        
        # Return response
        return jsonify({
            'result': result,
            'stdout': stdout
        })
        
    except BadRequest as e:
        return jsonify({'error': str(e)}), 400
    except Exception as e:
        app.logger.error(f"Execution error: {str(e)}")
        return jsonify({'error': f'Execution failed: {str(e)}'}), 500

@app.errorhandler(404)
def not_found(error):
    return jsonify({'error': 'Endpoint not found'}), 404

@app.errorhandler(405)
def method_not_allowed(error):
    return jsonify({'error': 'Method not allowed'}), 405

if __name__ == '__main__':
    import os
    port = int(os.environ.get('PORT', 8080))
    app.run(host='0.0.0.0', port=port, debug=False) 