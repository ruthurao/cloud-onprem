# Private subnet for the risk task

This is the network design. No VPC, subnet, security group, or endpoint was created. No EC2 API was called. The screenshot was not taken because this account has no VPC from this work to photograph. `APPROVED_REGION` stays a placeholder until the SSO portal shows a region where `google.gemma-3-4b-it` is enabled.

The task is one shot. `RunTask` would start it, the process would score APP-1001, write one log line, and exit. Nothing on the internet calls this scorer, so it does not belong in a public subnet.

## Subnet

The task runs in a private subnet. The design label for that subnet is `subnet-PRIVATE`. That label is not a live subnet id.

The route table for `subnet-PRIVATE` has the VPC local route only. It has no `0.0.0.0/0` route. The task has no path to the internet.

`assignPublicIp` is `DISABLED` on the awsvpc configuration. The task receives a private address and no public address.

```json
{
  "awsvpcConfiguration": {
    "subnets": ["subnet-PRIVATE"],
    "securityGroups": ["sg-risk-agent"],
    "assignPublicIp": "DISABLED"
  }
}
```

## Security group `risk-agent-sg`

The design label is `sg-risk-agent`. It is not a live security group id.

Inbound rules: none. The task accepts no connections. There is no listener, no load balancer, and no inbound port.

Egress rules: TCP 443 only. The destinations are the interface endpoints below and the S3 gateway prefix list. There is no egress rule to `0.0.0.0/0`.

| Direction | Protocol | Port | Destination | Why |
| --- | --- | --- | --- | --- |
| Inbound |  |  | none | Nothing connects to a one-shot scorer. |
| Egress | TCP | 443 | `risk-endpoint-sg` on the Bedrock runtime interface endpoint | The task role calls `bedrock:InvokeModel`. |
| Egress | TCP | 443 | `risk-endpoint-sg` on the `ecr.api` interface endpoint | The execution role calls `ecr:GetAuthorizationToken` and the image APIs. |
| Egress | TCP | 443 | `risk-endpoint-sg` on the `ecr.dkr` interface endpoint | Fargate downloads the image layers through the ECR Docker endpoint. |
| Egress | TCP | 443 | `risk-endpoint-sg` on the CloudWatch Logs interface endpoint | The awslogs driver writes the score line. |
| Egress | TCP | 443 | S3 gateway prefix list for `APPROVED_REGION` | ECR layer blobs are fetched through the S3 gateway. |

`risk-endpoint-sg` is the security group on the interface endpoints. Its inbound rule is TCP 443 from `risk-agent-sg` only. Its rule set does not allow the open internet.

## Endpoints

The private subnet reaches AWS through endpoints, so it does not need an internet route.

| Endpoint | Type | Service name |
| --- | --- | --- |
| Bedrock runtime | interface | `com.amazonaws.APPROVED_REGION.bedrock-runtime` |
| ECR API | interface | `com.amazonaws.APPROVED_REGION.ecr.api` |
| ECR Docker | interface | `com.amazonaws.APPROVED_REGION.ecr.dkr` |
| CloudWatch Logs | interface | `com.amazonaws.APPROVED_REGION.logs` |
| S3 | gateway | `com.amazonaws.APPROVED_REGION.s3`, associated with the private route table |

The interface endpoints sit in the private subnet and use `risk-endpoint-sg`. Private DNS is enabled on each interface endpoint so the task uses the normal `bedrock-runtime`, `ecr`, and `logs` hostnames and still stays on the endpoint ENIs.

## NAT gateway

A NAT gateway would also let the task run. The private route table would send `0.0.0.0/0` at the NAT, and the NAT would sit in a public subnet. That path reaches Bedrock, ECR, and CloudWatch Logs, and it also opens the whole internet. The endpoint design is the one this task uses, because the task only needs those four services plus S3.

## Commands that were not run

```text
aws ec2 create-vpc
aws ec2 create-subnet
aws ec2 create-route-table
aws ec2 create-security-group --group-name risk-agent-sg
aws ec2 authorize-security-group-egress
aws ec2 create-vpc-endpoint --service-name com.amazonaws.APPROVED_REGION.bedrock-runtime
aws ec2 create-vpc-endpoint --service-name com.amazonaws.APPROVED_REGION.ecr.api
aws ec2 create-vpc-endpoint --service-name com.amazonaws.APPROVED_REGION.ecr.dkr
aws ec2 create-vpc-endpoint --service-name com.amazonaws.APPROVED_REGION.logs
aws ec2 create-vpc-endpoint --service-name com.amazonaws.APPROVED_REGION.s3 --vpc-endpoint-type Gateway
```

Not run. There is no VPC id, no subnet id, and no screenshot.
