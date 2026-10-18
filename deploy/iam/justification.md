# Least-privilege roles for the risk agent

These roles were not created. This account cannot manage IAM. No `iam` API was called. `APPROVED_REGION` and `ACCOUNT_ID` stay placeholders until the SSO portal at `https://d-9067b28fef.awsapps.com/start` shows them.

The task role is the identity of the running scorer. The execution role is a separate identity that would pull the image and write the log stream. They are written as two policies so the agent's permissions are not confused with the image-pull permissions.

## Commands that were not run

```text
aws iam create-role \
  --role-name underwriting-risk-task-role \
  --assume-role-policy-document file://deploy/iam/task-trust.json

aws iam put-role-policy \
  --role-name underwriting-risk-task-role \
  --policy-name underwriting-risk-task \
  --policy-document file://deploy/iam/task-policy.json

aws iam create-role \
  --role-name underwriting-risk-execution-role \
  --assume-role-policy-document file://deploy/iam/execution-trust.json

aws iam put-role-policy \
  --role-name underwriting-risk-execution-role \
  --policy-name underwriting-risk-execution \
  --policy-document file://deploy/iam/execution-policy.json
```

Not run. There is no role ARN, no policy version, and no console screenshot.

## Task role `underwriting-risk-task-role`

Trust file: `deploy/iam/task-trust.json`. Policy file: `deploy/iam/task-policy.json`.

The trust principal is `ecs-tasks.amazonaws.com`, and the only trust action is `sts:AssumeRole`. ECS would use that to start the task. The trust does not name the account root, an IAM user, or `ec2.amazonaws.com`.

### Allow

| Permission | Resource | Why it is necessary |
| --- | --- | --- |
| `bedrock:InvokeModel` | `arn:aws:bedrock:APPROVED_REGION::foundation-model/google.gemma-3-4b-it` | The agent calls that one model and no other AWS API. The foundation-model ARN has no account id, which is the Bedrock form for this model. |

### Left off this role

| Permission | Why it is left off |
| --- | --- |
| `bedrock:InvokeModelWithResponseStream` | The process does not stream. It sends one prompt and reads one rationale. |
| `bedrock:*` | A wildcard would allow every Bedrock API and every model. The scorer needs one action on one model. |
| S3 (`s3:*`, `s3:GetObject`, `s3:PutObject`) | The process does not store objects. The application text goes to Bedrock in the invoke body. |
| IAM (`iam:*`, `iam:PassRole`, `iam:CreateRole`) | The process does not change identities and does not launch other tasks. |
| EC2 (`ec2:*`) | The process does not manage the network, subnets, or security groups. |
| ECR (`ecr:*`) | The process does not pull images. Image pull belongs to the execution role. |
| CloudWatch Logs (`logs:*`) | The process does not create log streams. The awslogs driver belongs to the execution role. |
| Secrets Manager (`secretsmanager:*`) | The process does not read secrets. The model id is fixed in the task, and the task role is the credential. |

## Execution role `underwriting-risk-execution-role`

Trust file: `deploy/iam/execution-trust.json`. Policy file: `deploy/iam/execution-policy.json`.

The trust principal is again `ecs-tasks.amazonaws.com` with `sts:AssumeRole` only. Fargate assumes this role to pull the private image and to open the log stream. It is a different role name from the task role.

### Allow

| Permission | Resource | Why it is necessary |
| --- | --- | --- |
| `ecr:GetAuthorizationToken` | `*` | Fargate would pull the private image. ECR requires `Resource: "*"` for this action; it cannot be bound to one repository ARN. |
| `ecr:BatchCheckLayerAvailability` | `arn:aws:ecr:APPROVED_REGION:ACCOUNT_ID:repository/underwriting-risk` | Fargate would check that the layers of this one repository exist. |
| `ecr:GetDownloadUrlForLayer` | same repository | Fargate would obtain the layer URLs for this image. |
| `ecr:BatchGetImage` | same repository | Fargate would read the image manifest for this repository. |
| `logs:CreateLogStream` | `arn:aws:logs:APPROVED_REGION:ACCOUNT_ID:log-group:/ecs/underwriting-risk:*` | The task's log driver would open a stream in that one log group. |
| `logs:PutLogEvents` | same log group | The task's log driver would write the score line. |

The three layer actions are scoped to `underwriting-risk`. The token action stays on `*` because that is the only resource ECR accepts for it.

### Left off this role

| Permission | Why it is left off |
| --- | --- |
| `bedrock:InvokeModel` and `bedrock:InvokeModelWithResponseStream` | The model call is the task role's permission. The execution role pulls the image and writes logs. |
| `bedrock:*` | This role has no Bedrock work. |
| S3 | ECR hands Fargate pre-signed layer URLs. The execution role does not need `s3:GetObject`. |
| `logs:CreateLogGroup` and `logs:*` | The log group `/ecs/underwriting-risk` would be created before the task. This role only opens a stream and writes events in that group. |
| Other ECR actions (`ecr:PutImage`, `ecr:CreateRepository`, `ecr:*`) | This role pulls one existing repository. It does not push or create repositories. |
| IAM, EC2, Secrets Manager | This role does not change identities, manage the network, or read secrets. |
