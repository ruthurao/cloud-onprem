# APP-1001 on both deployments

One input for both runs: APP-1001, Alice Chen, homeowners. The graded correct result is the rule score, 13, band low. The same model and the same prompt are used on both sides, so the rationale wording can still differ.

The model is Gemma 3 4B IT: Ollama `gemma3:4b`, Bedrock `google.gemma-3-4b-it`. The shared prompt asks for a short JSON rationale only. `score_facts` owns the score.

The AWS task was not executed. Its result below is simulated from the rule score.

## Ollama

Run. `LLM_PROVIDER=ollama`. The listener is `http://127.0.0.1:11434/api/chat`. The transcript below is the unedited command output saved in `docs/captures/app-1001-ollama.txt`.

```text
application: APP-1001
name: Alice Chen
product: homeowners
score: 13
band: low
factors: ["base", "credit excellent"]
hard_refer: []
provider: ollama
rationale: Alice Chen's excellent credit score and strong base factors contribute to a low risk profile, justifying this homeowner's application at a score of 13 and band.
```

## AWS

Not run. The ECS task was not run. `deploy/aws-process.md` marks `aws ecs run-task` and `aws logs tail` as not run. There is no CloudWatch score line. The block below is a simulated result, not a log line.

The task definition that would have been used is `deploy/ecs/task-definition.json`: Fargate, command `APP-1001`, `LLM_PROVIDER=bedrock`, model `google.gemma-3-4b-it`.

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
