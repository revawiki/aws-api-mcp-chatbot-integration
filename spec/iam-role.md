# IAM Roles

## EC2 Instance Profile
**Name:** `wiki-ec2-execution-role`

### Purpose
- Allow EC2 instances to perform both read-write and read-only AWS operations.

### Attached Policies
- `AdministratorAccess` — Provides full administrative access for write operations.
- `ReadOnlyAccess` — Enables safe inspection of AWS resources for read-only queries.

### Trust Policy
- Principal Service: `ec2.amazonaws.com`

## Lambda Execution Role
**Name:** `wiki-lambda-execution-role`

### Purpose
- Support Lambda functions (e.g., Bedrock agent, webhook handler) interacting with Bedrock, DynamoDB, EventBridge, and CloudWatch Logs.

### Attached Policies
- `AmazonBedrockFullAccess` — Full access to Bedrock; minimum need is invoking models via the Converse API.
- `AmazonDynamoDBFullAccess` — Full access to DynamoDB; minimum need is reading and writing session/state tables.
- `AmazonEventBridgeFullAccess` — Allows publishing events (e.g., `PutEvents`) to EventBridge.
- `AWSLambdaBasicExecutionRole` — Grants CloudWatch logging permissions.

### Trust Policy
- Principal Service: `lambda.amazonaws.com`

## EventBridge Execution Role
**Name:** `wiki-eventbridge-execution-role`

### Purpose
- Allow EventBridge rules to invoke target Lambda functions when event patterns are matched.

### Attached Policies
- `AWSLambdaRole` — Permits EventBridge to invoke Lambda targets; minimum requirement is `lambda:InvokeFunction`.

### Trust Policy
- Principal Service: `events.amazonaws.com`

## Notes and Recommendations
- Replace blanket `FullAccess` policies with least-privilege custom policies whenever possible.
- Restrict DynamoDB permissions to the specific tables used for state tracking.
