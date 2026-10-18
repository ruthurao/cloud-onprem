"""One prompt, two transports.

The model writes a short rationale only. score_facts owns the score.
"""

import json
import os
import urllib.request

OLLAMA_URL = "http://127.0.0.1:11434/api/chat"
OLLAMA_MODEL = "gemma3:4b"
BEDROCK_MODEL = "google.gemma-3-4b-it"

PROMPT = (
    "Write a short rationale for this homeowners application. "
    "The score, band, factors, and hard_refer values are already decided and must not change. "
    'Reply with JSON only, shaped {"rationale": "one or two sentences"}.'
)


def prompt_text(application, facts):
    payload = {
        "application_id": application["id"],
        "full_name": application["full_name"],
        "product": application["product"],
        "score": facts["score"],
        "band": facts["band"],
        "factors": facts["factors"],
        "hard_refer": facts["hard_refer"],
    }
    return PROMPT + "\n" + json.dumps(payload, separators=(",", ":"))


def ollama_chat_body(prompt):
    return {
        "model": OLLAMA_MODEL,
        "messages": [{"role": "user", "content": prompt}],
        "stream": False,
    }


def bedrock_invoke_body(prompt):
    return {
        "messages": [{"role": "user", "content": prompt}],
        "max_tokens": 256,
        "temperature": 0.2,
    }


def complete(prompt, provider=None):
    chosen = provider or os.environ.get("LLM_PROVIDER", "ollama")
    if chosen == "ollama":
        return _ollama(prompt)
    if chosen == "bedrock":
        return _bedrock(prompt)
    raise ValueError(f"unknown LLM_PROVIDER {chosen}")


def _ollama(prompt):
    body = json.dumps(ollama_chat_body(prompt)).encode()
    request = urllib.request.Request(
        OLLAMA_URL,
        data=body,
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    with urllib.request.urlopen(request, timeout=180) as response:
        payload = json.loads(response.read().decode())
    return payload["message"]["content"]


def _bedrock(prompt):
    import boto3

    region = os.environ.get("AWS_REGION") or os.environ.get("AWS_DEFAULT_REGION")
    if not region or region == "APPROVED_REGION":
        raise RuntimeError("AWS_REGION is not set to an approved region")
    client = boto3.client("bedrock-runtime", region_name=region)
    response = client.invoke_model(
        modelId=BEDROCK_MODEL,
        body=json.dumps(bedrock_invoke_body(prompt)),
        contentType="application/json",
        accept="application/json",
    )
    payload = json.loads(response["body"].read())
    return bedrock_text(payload)


def bedrock_text(payload):
    choices = payload.get("choices") or []
    if choices:
        content = (choices[0].get("message") or {}).get("content")
        if isinstance(content, str):
            return content
        if isinstance(content, list):
            parts = []
            for part in content:
                if isinstance(part, str):
                    parts.append(part)
                elif isinstance(part, dict):
                    parts.append(part.get("text") or "")
            return "".join(parts)
    generation = payload.get("generation")
    if isinstance(generation, str):
        return generation
    raise ValueError("bedrock response had no rationale text")


def rationale_from_model_text(raw, facts):
    try:
        data = json.loads(_json_object(raw))
        rationale = data["rationale"]
        if not isinstance(rationale, str) or not rationale.strip():
            raise ValueError("empty rationale")
    except (json.JSONDecodeError, KeyError, TypeError, ValueError):
        return {
            "score": facts["score"],
            "rationale": "quality miss: model response was not the expected JSON rationale",
            "quality_miss": True,
        }
    return {
        "score": facts["score"],
        "rationale": rationale.strip(),
        "quality_miss": False,
    }


def _json_object(raw):
    text = (raw or "").strip()
    if text.startswith("```"):
        lines = text.splitlines()[1:]
        if lines and lines[-1].strip().startswith("```"):
            lines = lines[:-1]
        text = "\n".join(lines).strip()
    return text
