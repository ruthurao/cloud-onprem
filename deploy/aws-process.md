# Fargate process for the risk task

Every step below was not run. This account has no working SSO session, and it cannot use ECR, ECS, or Fargate. No `ecr`, `ecs`, `logs`, or `sso` API was called. `ACCOUNT_ID` and `APPROVED_REGION` stay placeholders. The 15 points for a live Fargate run are not claimed.

Bedrock model access for `google.gemma-3-4b-it` would have to be enabled in the approved region before step 5. That enablement was not done.

The task definition in `deploy/ecs/task-definition.json` still names `underwriting-risk-task-role` and `underwriting-risk-execution-role`. Those roles were not created.

## 1. Install the AWS CLI and log in with SSO

Not run.

```text
# Install AWS CLI v2 from the official Amazon package for this OS.
aws configure sso --profile underwriting-risk
# start URL: https://d-9067b28fef.awsapps.com/start
# profile name: underwriting-risk
aws sso login --profile underwriting-risk
```

The account id, permission set, and region would come from that portal. They were not read, and they were not guessed.

## 2. Create the two roles

Not run. The role documents are `deploy/iam/task-trust.json`, `deploy/iam/task-policy.json`, `deploy/iam/execution-trust.json`, and `deploy/iam/execution-policy.json`. The `create-role` and `put-role-policy` commands are listed in `deploy/iam/justification.md` and were not run.

## 3. Create the ECR repository, build, tag, and push

Not run. Docker is installed here, and a local image `underwriting-risk:phase1` exists with id `309f5a186dc2`. ECR credentials do not exist, so the repository was not created, the image was not tagged for ECR, and nothing was pushed. There is no push log.

```text
aws ecr create-repository --repository-name underwriting-risk --profile underwriting-risk
aws ecr get-login-password --region APPROVED_REGION --profile underwriting-risk \
  | docker login --username AWS --password-stdin ACCOUNT_ID.dkr.ecr.APPROVED_REGION.amazonaws.com
docker build -t underwriting-risk:phase1 .
docker tag underwriting-risk:phase1 ACCOUNT_ID.dkr.ecr.APPROVED_REGION.amazonaws.com/underwriting-risk:phase1
docker push ACCOUNT_ID.dkr.ecr.APPROVED_REGION.amazonaws.com/underwriting-risk:phase1
```

## 4. Register the task definition

Not run. The file that would be registered is `deploy/ecs/task-definition.json`.

It is Fargate, `awsvpc`, 256 CPU, 512 memory. `taskRoleArn` is `underwriting-risk-task-role`. `executionRoleArn` is `underwriting-risk-execution-role`. The container command is `APP-1001`. `LLM_PROVIDER` is `bedrock`. The log group is `/ecs/underwriting-risk`, the same group the execution policy allows. Public IP is not set on the task definition. `assignPublicIp` is `DISABLED` on the run-task network configuration in step 5.

`AWS_REGION` in the file is still the placeholder `APPROVED_REGION`. The scorer refuses that placeholder, so a real register would replace it with the region from the portal first. That replacement was not made.

```text
aws ecs register-task-definition \
  --cli-input-json file://deploy/ecs/task-definition.json \
  --profile underwriting-risk
```

## 5. Run the task in the private subnet

Not run. The network configuration is the one in `deploy/network/private-subnet.md`: subnet `subnet-PRIVATE`, security group `risk-agent-sg`, `assignPublicIp` `DISABLED`.

```text
aws ecs run-task \
  --cluster underwriting-risk \
  --launch-type FARGATE \
  --task-definition underwriting-risk \
  --network-configuration "awsvpcConfiguration={subnets=[subnet-PRIVATE],securityGroups=[sg-risk-agent],assignPublicIp=DISABLED}" \
  --profile underwriting-risk
```

## 6. Read the score line from logs

Not run. There is no CloudWatch score line. The task was not started. The command below was not run, and the simulated block under it is not a log line.

```text
aws logs tail /ecs/underwriting-risk --follow --profile underwriting-risk
```

```text
simulated result, task not executed
application: APP-1001
name: Alice Chen
product: homeowners
score: 13
band: low
factors: ["base", "credit excellent"]
hard_refer: []
```

The score is the rule score. The model was not called, so this block has no rationale.
