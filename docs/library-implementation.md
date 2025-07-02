# Library Implementation with nsjail

## Overview

This document explains how Python libraries are hardcoded and made available in the nsjail sandboxed execution environment.

## Implementation Strategy

### 1. Global Installation at Build Time

Libraries are installed globally during Docker image build:

```dockerfile
# Copy requirements and install Python dependencies
COPY requirements.txt .
RUN pip3 install --no-cache-dir -r requirements.txt
```

This approach ensures:
- ✅ Libraries are available to all execution contexts
- ✅ Consistent versions across all script executions
- ✅ No need for dynamic installation during runtime
- ✅ Better security (no package installation from user code)

### 2. Environment Variable Configuration

Libraries are made accessible to nsjail via carefully configured environment variables:

```python
'--env', 'PYTHONPATH=/usr/local/lib/python3.11/site-packages:/usr/lib/python3/dist-packages',
'--env', 'PATH=/usr/local/bin:/usr/bin:/bin',
```

Critical environment variables for library compatibility:
- `PYTHONPATH` - Python module search paths
- `OPENBLAS_NUM_THREADS=1` - Prevents threading issues with numpy/scipy
- `OMP_NUM_THREADS=1` - Limits OpenMP threads for container compatibility
- `MPLBACKEND=Agg` - Non-interactive matplotlib backend
- `PYTHONIOENCODING=utf-8` - Ensures proper text encoding

### 3. Container-Compatible Configuration

nsjail is configured with all namespaces disabled for container compatibility:

```python
'--disable_clone_newnet',    # Network namespace disabled
'--disable_clone_newuser',   # User namespace disabled  
'--disable_clone_newns',     # Mount namespace disabled
# ... all other namespaces disabled
```

This is **required** because:
- Docker containers already provide isolation
- Additional namespaces cause "Operation not permitted" errors
- Cloud Run and other container platforms have strict security policies

## Library Categories

### Scientific Computing Stack
- **pandas** - Data manipulation and analysis
- **numpy** - Numerical computing with BLAS optimizations
- **scipy** - Advanced scientific algorithms
- **matplotlib** - Plotting (configured for non-interactive use)
- **seaborn** - Statistical visualization

### Data Processing
- **openpyxl/xlsxwriter** - Excel file support
- **python-dateutil/pytz** - Advanced date/time handling
- **beautifulsoup4/lxml** - HTML/XML parsing

### Networking & Validation
- **requests/urllib3** - HTTP client libraries  
- **jsonschema** - Data validation

## Testing Library Availability

Use the provided test script to validate all libraries:

```bash
python3 test_libraries.py http://localhost:8080
```

This tests:
- Import capability of all libraries
- Basic functionality of each library
- Integration within nsjail environment
- Memory and threading compatibility

## Adding New Libraries

To add new hardcoded libraries:

1. **Add to requirements.txt** with version pinning:
```txt
new-library>=1.0.0,<2.0.0
```

2. **Rebuild Docker image**:
```bash
docker build -t python-executor .
```

3. **Test compatibility** with nsjail environment:
```bash
# Test the new library
curl -X POST http://localhost:8080/execute \
  -H "Content-Type: application/json" \
  -d '{"script": "import new_library\ndef main():\n    return {\"status\": \"ok\"}"}'
```

4. **Add environment variables if needed** (for libraries requiring special configuration)

## Troubleshooting Common Issues

### Library Import Failures
- **Cause**: Missing from PYTHONPATH or not installed
- **Solution**: Verify library is in requirements.txt and PYTHONPATH is correct

### Threading/Performance Issues  
- **Cause**: Libraries trying to use multiple threads in restricted environment
- **Solution**: Add appropriate environment variables (OPENBLAS_NUM_THREADS, etc.)

### Graphics/Display Issues
- **Cause**: Libraries trying to open displays or create GUI elements
- **Solution**: Use non-interactive backends (MPLBACKEND=Agg)

### Permission Errors
- **Cause**: Libraries trying to access restricted system resources
- **Solution**: Review nsjail resource limits and namespace configuration

## Security Considerations

- Libraries are **pre-vetted** and installed at build time
- No dynamic package installation from user code
- Libraries run within nsjail resource limits
- Network access controlled by nsjail configuration
- File system access restricted to read-only system libraries

## Performance Optimizations

- **Pre-compilation**: Libraries compiled during image build
- **Thread limiting**: Prevents resource exhaustion
- **Memory constraints**: nsjail enforces memory limits
- **Timeout protection**: 30-second execution limit

This approach provides a secure, performant, and reliable way to offer a rich set of Python libraries while maintaining strong sandboxing. 