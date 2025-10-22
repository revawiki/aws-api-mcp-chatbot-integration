# EventBridge Rules

## Telegram Chaining Rule
**Name:** `wiki-mcp-bridge-telegram-chaining`

### Event Pattern
- Matches events with `source: lambda.telegram.listener` on the default event bus.

### Targets
- **Lambda ARN:** `arn:${AWS::Partition}:lambda:${AWS::Region}:${AWS::AccountId}:function:wiki-aws-mcp-bridge-telegram-responder`
- **Execution Role:** `arn:aws:iam::${AWS::AccountId}:role/service-role/wiki-eventbridge-execution-role`

## WhatsApp Chaining Rule
**Name:** `wiki-mcp-bridge-whatsapp-chaining`

### Event Pattern
- Matches events with `source: lambda.whatsapp.listener` on the default event bus.

### Targets
- **Lambda ARN:** `arn:${AWS::Partition}:lambda:${AWS::Region}:${AWS::AccountId}:function:wiki-aws-mcp-bridge-whatsapp-responder`
- **Execution Role:** `arn:aws:iam::${AWS::AccountId}:role/service-role/wiki-eventbridge-execution-role`

## Deploying with CloudFormation
1. Using `eventbridge/cf-template.yaml`, deploy directly with the AWS CLI.
2. Create or update the stack:
   ```bash
   aws cloudformation deploy \
     --template-file eventbridge/cf-template.yaml \
     --stack-name wiki-mcp-eventbridge
   ```
3. Verify two EventBridge rules exist on the default bus, each targeting the corresponding Lambda responder.

## Manual Console Setup
1. Open EventBridge in the AWS console and choose the **default** event bus.
2. Create a rule named `wiki-mcp-bridge-telegram-chaining`:
   - Event pattern: `{"source":["lambda.telegram.listener"]}`
   - Target: Lambda function `wiki-aws-mcp-bridge-telegram-responder`
   - Execution role: `wiki-eventbridge-execution-role`
3. Create a second rule named `wiki-mcp-bridge-whatsapp-chaining`:
   - Event pattern: `{"source":["lambda.whatsapp.listener"]}`
   - Target: Lambda function `wiki-aws-mcp-bridge-whatsapp-responder`
   - Execution role: `wiki-eventbridge-execution-role`
4. Confirm both rules are enabled and that the IAM role grants `lambda:InvokeFunction` on the responder Lambdas.
