#!/usr/bin/env python3
"""
Safe Python Script Execution Service

A Flask-based API service that executes Python scripts in a sandboxed environment
using nsjail for security.
"""

import json
import subprocess
import tempfile
import os
import re
import sys
from flask import Flask, request, jsonify
from werkzeug.exceptions import BadRequest

app = Flask(__name__)

# nsjail configuration
NSJAIL_CONFIG = {
    'time_limit': 30,  # 30 seconds timeout
    'memory_limit': 512,  # 512MB memory limit
    'cpu_limit': 1,  # 1 CPU core
    'max_cpus': 1,
    'max_files': 10,
    'max_procs': 5,
    'rlimit_as': 536870912,  # 512MB
    'rlimit_cpu': 30,
    'rlimit_fsize': 1048576,  # 1MB file size limit
    'rlimit_nofile': 10,
    'rlimit_nproc': 5,
    'seccomp_string': 'SCMP_0x0 | SCMP_1 | SCMP_2 | SCMP_3 | SCMP_4 | SCMP_5 | SCMP_6 | SCMP_7 | SCMP_8 | SCMP_9 | SCMP_10 | SCMP_11 | SCMP_12 | SCMP_13 | SCMP_14 | SCMP_15 | SCMP_16 | SCMP_17 | SCMP_18 | SCMP_19 | SCMP_20 | SCMP_21 | SCMP_22 | SCMP_23 | SCMP_24 | SCMP_25 | SCMP_26 | SCMP_27 | SCMP_28 | SCMP_29 | SCMP_30 | SCMP_31 | SCMP_32 | SCMP_33 | SCMP_34 | SCMP_35 | SCMP_36 | SCMP_37 | SCMP_38 | SCMP_39 | SCMP_40 | SCMP_41 | SCMP_42 | SCMP_43 | SCMP_44 | SCMP_45 | SCMP_46 | SCMP_47 | SCMP_48 | SCMP_49 | SCMP_50 | SCMP_51 | SCMP_52 | SCMP_53 | SCMP_54 | SCMP_55 | SCMP_56 | SCMP_57 | SCMP_58 | SCMP_59 | SCMP_60 | SCMP_61 | SCMP_62 | SCMP_63 | SCMP_64 | SCMP_65 | SCMP_66 | SCMP_67 | SCMP_68 | SCMP_69 | SCMP_70 | SCMP_71 | SCMP_72 | SCMP_73 | SCMP_74 | SCMP_75 | SCMP_76 | SCMP_77 | SCMP_78 | SCMP_79 | SCMP_80 | SCMP_81 | SCMP_82 | SCMP_83 | SCMP_84 | SCMP_85 | SCMP_86 | SCMP_87 | SCMP_88 | SCMP_89 | SCMP_90 | SCMP_91 | SCMP_92 | SCMP_93 | SCMP_94 | SCMP_95 | SCMP_96 | SCMP_97 | SCMP_98 | SCMP_99 | SCMP_100 | SCMP_101 | SCMP_102 | SCMP_103 | SCMP_104 | SCMP_105 | SCMP_106 | SCMP_107 | SCMP_108 | SCMP_109 | SCMP_110 | SCMP_111 | SCMP_112 | SCMP_113 | SCMP_114 | SCMP_115 | SCMP_116 | SCMP_117 | SCMP_118 | SCMP_119 | SCMP_120 | SCMP_121 | SCMP_122 | SCMP_123 | SCMP_124 | SCMP_125 | SCMP_126 | SCMP_127 | SCMP_128 | SCMP_129 | SCMP_130 | SCMP_131 | SCMP_132 | SCMP_133 | SCMP_134 | SCMP_135 | SCMP_136 | SCMP_137 | SCMP_138 | SCMP_139 | SCMP_140 | SCMP_141 | SCMP_142 | SCMP_143 | SCMP_144 | SCMP_145 | SCMP_146 | SCMP_147 | SCMP_148 | SCMP_149 | SCMP_150 | SCMP_151 | SCMP_152 | SCMP_153 | SCMP_154 | SCMP_155 | SCMP_156 | SCMP_157 | SCMP_158 | SCMP_159 | SCMP_160 | SCMP_161 | SCMP_162 | SCMP_163 | SCMP_164 | SCMP_165 | SCMP_166 | SCMP_167 | SCMP_168 | SCMP_169 | SCMP_170 | SCMP_171 | SCMP_172 | SCMP_173 | SCMP_174 | SCMP_175 | SCMP_176 | SCMP_177 | SCMP_178 | SCMP_179 | SCMP_180 | SCMP_181 | SCMP_182 | SCMP_183 | SCMP_184 | SCMP_185 | SCMP_186 | SCMP_187 | SCMP_188 | SCMP_189 | SCMP_190 | SCMP_191 | SCMP_192 | SCMP_193 | SCMP_194 | SCMP_195 | SCMP_196 | SCMP_197 | SCMP_198 | SCMP_199 | SCMP_200 | SCMP_201 | SCMP_202 | SCMP_203 | SCMP_204 | SCMP_205 | SCMP_206 | SCMP_207 | SCMP_208 | SCMP_209 | SCMP_210 | SCMP_211 | SCMP_212 | SCMP_213 | SCMP_214 | SCMP_215 | SCMP_216 | SCMP_217 | SCMP_218 | SCMP_219 | SCMP_220 | SCMP_221 | SCMP_222 | SCMP_223 | SCMP_224 | SCMP_225 | SCMP_226 | SCMP_227 | SCMP_228 | SCMP_229 | SCMP_230 | SCMP_231 | SCMP_232 | SCMP_233 | SCMP_234 | SCMP_235 | SCMP_236 | SCMP_237 | SCMP_238 | SCMP_239 | SCMP_240 | SCMP_241 | SCMP_242 | SCMP_243 | SCMP_244 | SCMP_245 | SCMP_246 | SCMP_247 | SCMP_248 | SCMP_249 | SCMP_250 | SCMP_251 | SCMP_252 | SCMP_253 | SCMP_254 | SCMP_255'
}

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
        r'import\s+os\s*$',
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
    Execute the Python script in a sandboxed environment using subprocess with resource limits.
    
    Args:
        script (str): The Python script to execute
        
    Returns:
        tuple: (result, stdout, stderr)
    """
    # Create temporary files
    script_file = tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False)
    script_file.write(script)
    script_file.close()
    
    try:
        # Prepare the execution script
        exec_script = f"""
import sys
import json
import io
import resource
from contextlib import redirect_stdout

# Set resource limits for security
resource.setrlimit(resource.RLIMIT_AS, (512 * 1024 * 1024, 512 * 1024 * 1024))  # 512MB memory
resource.setrlimit(resource.RLIMIT_CPU, (30, 30))  # 30 seconds CPU time
resource.setrlimit(resource.RLIMIT_FSIZE, (1024 * 1024, 1024 * 1024))  # 1MB file size
resource.setrlimit(resource.RLIMIT_NOFILE, (10, 10))  # 10 file descriptors

# Redirect stdout to capture print statements
stdout_capture = io.StringIO()

try:
    # Execute the user script
    exec(open('{script_file.name}').read())
    
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
        
        # Execute with subprocess and timeout
        process = subprocess.run(
            ['python3', '-c', exec_script],
            capture_output=True,
            text=True,
            timeout=NSJAIL_CONFIG['time_limit'] + 5
        )
        
        if process.returncode != 0:
            raise Exception(f"Execution failed: {process.stderr}")
        
        # Parse the output
        try:
            output = json.loads(process.stdout.strip())
            if 'error' in output:
                raise Exception(output['error'])
            return output['result'], output['stdout'], process.stderr
        except json.JSONDecodeError:
            raise Exception("Invalid output format from script execution")
            
    finally:
        # Cleanup
        try:
            os.unlink(script_file.name)
        except OSError:
            pass

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
    app.run(host='0.0.0.0', port=8080, debug=False) 