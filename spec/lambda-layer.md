# Lambda Layer

## MCP + AnyIO + Requests
**Name:** `wiki-pymcp`

### Prerequisites
- `python3`
- `pip`

### Creation Steps
1. Install dependencies into the `python` folder for Lambda:
   ```bash
   pip install -r requirements.txt \
     --implementation cp \
     --platform manylinux2014_x86_64 \
     --python-version 3.13 \
     --target ./python \
     --only-binary=:all:
   ```
2. Zip the resulting `python` directory.
3. Upload the archive as Lambda layer.
