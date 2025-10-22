# EC2 Instance

**Name:** `wiki-ec2-sandbox`

## Purpose
- Host the sandbox environment for MCP server testing and related workloads.

## Configuration
- **Instance Profile:** `wiki-ec2-execution-role` — grants required read/write and read-only AWS permissions.
- **Security Group:** — configure inbound rules so MCP traffic and management access remain available.

## Network and Access
- Expose the MCP port for inbound access (commonly `8000`, adjust as needed, in this sample we use HTTP port `80`).
- Example inbound rule:
  - Type: Custom TCP Rule
  - Protocol: TCP
  - Port Range: 8000
  - Source: `<trusted source CIDR or security group>`
- At least allow outbound HTTPS (`443`) to reach AWS APIs and Bedrock services.

## Launch MCP Server

After launching the EC2 instance:

1. **Install prerequisites**
   - Ensure both **Docker** and **Docker Compose** are installed and running.
   - Verify installation:
     ```bash
     docker --version
     docker compose version
     ```

2. **Configure AWS credentials**
   - Run the following command to set up a default AWS CLI configuration:
     ```bash
     aws configure
     ```
   - Assuming we use instance profile, only fill the region when prompted (left other's blank).

3. **Start the MCP server**
   - Navigate to the `aws-api-mcp-server` directory in the repository containing the `docker-compose.yaml` file.
   - Launch the MCP server using that docker-compose configuration:
     ```bash
     docker compose up -d
     ```

4. **Verify**
   - Check that the MCP server container is running:
     ```bash
     docker ps
     ```
   - Ensure the exposed MCP port (e.g., `8000`) is open and accessible from the Lambda environment.