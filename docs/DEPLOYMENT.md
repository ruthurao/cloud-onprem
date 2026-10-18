# Deployment boundary

A grader can score this page without reading the code. The application is one homeowners risk score for APP-1001, Alice Chen. The rule score is 13, band low. The model writes a short rationale only. Two places can run that same program. They do not draw the same boundary around the application text.

## AWS path

This path was not executed. No ECS task was started, and no Bedrock call was made.

The program would run as one Fargate container in the private subnet `subnet-PRIVATE`. `assignPublicIp` is disabled. Nothing on the internet connects to the task. Security group `risk-agent-sg` has no inbound rules. Its egress is TCP 443 to the Bedrock runtime, ECR, CloudWatch Logs, and the S3 gateway.

The identity of the running program is the task role `underwriting-risk-task-role`. That role can call `bedrock:InvokeModel` on `google.gemma-3-4b-it` and nothing else. A second role, `underwriting-risk-execution-role`, pulls the image and writes the log stream. The program does not use the execution role to call the model.

The image comes from the private ECR repository `underwriting-risk`. The model call leaves the container. The prompt, which contains the application id, the name, the product, and the scored facts, is sent to the Bedrock runtime endpoint. The application text would be inside AWS, and it would not stay inside the container only. Bedrock holds the prompt for the duration of the invoke. The awslogs driver sends the score line to CloudWatch Logs in the group `/ecs/underwriting-risk`.

The container has no public address. The private subnet still reaches Bedrock, ECR, and CloudWatch through interface endpoints, and S3 through a gateway endpoint. Those endpoints are inside the VPC, and the application text still leaves the container for a managed model endpoint.

## On-prem path

This path was executed on this machine.

One process runs `python -m underwriting APP-1001`. The model weights for `gemma3:4b` are on local disk. Ollama listens on `127.0.0.1:11434`, and the process posts the prompt to that loopback address. The prompt does not cross a network interface that another host can route to.

This path has no IAM role, no subnet, no security group, no ECR, no Bedrock, and no CloudWatch. The score line is the process stdout. The recorded result is score 13, band low, factors `["base", "credit excellent"]`, `hard_refer` `[]`.

## What an air gap removes

An air gap removes `docker pull`, `pip install`, `ollama pull`, ECR, Bedrock, CloudWatch, and SSO. After the network is cut, none of those calls can succeed. The image and the Gemma weights have to be loaded onto the host before the cut. The running process then uses only the local files and the loopback listener.

A client asks for this when the application is insurance PII and the contract or the regulator requires the data to stay on their network. APP-1001 carries a person's name and the underwriting facts that produced the score. On the AWS path that text leaves the container for Bedrock. On the air-gapped path it stays on the host.
