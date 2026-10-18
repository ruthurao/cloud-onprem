# Client recommendation

The recommendation names the client and the deployment. Cost, complexity, and output quality are the reasons. No dollar figure is given for a Bedrock call. That call was not made.

The cost shape on AWS is one `RunTask` that starts, prints the score, and exits. It is not a service left on. Fargate would bill the seconds the task runs. Bedrock would add a per-token charge for the one rationale. CloudWatch would keep the score line as the audit trail. On the laptop, Ollama has no per-token bill. The cost is the host and the disk for the `gemma3:4b` weights.

The AWS path has more moving parts: two IAM roles, a private subnet, interface endpoints, an ECR repository, a task definition, and a log group. The laptop path is one process and a loopback listener. The Fargate deployment was not run.

Output quality is scored from the real Ollama response only. For APP-1001 the model wrote that Alice Chen's excellent credit and the base factor support a low band at score 13. Those are the rule factors, `["base", "credit excellent"]`. The Bedrock rationale was not produced, so the two wordings are not compared. Both sides use Gemma 3 4B and the same prompt. The graded correct result on either side is the rule score, 13, band low.

## Strict data residency

Use Ollama, or the same open weights on the client's own hosts.

A private subnet plus Bedrock still sends the application to a managed endpoint. The prompt leaves the container for `bedrock-runtime`. That fails a residency requirement even when the IAM role is perfect. APP-1001 is insurance PII: a person's name and the facts behind the score. The contract or the regulator that requires the data to stay on the client network is the reason to keep the weights and the process inside that network.

## No residency requirement

Use Fargate plus Bedrock once `underwriting-risk-task-role` exists.

This client can accept the application text inside AWS. The extra moving parts buy a task role scoped to one model, a private subnet with no public address, and a CloudWatch log of the score line. The charge is one exiting task plus the tokens for one rationale. The rule score stays 13, band low. This deployment was not run.
