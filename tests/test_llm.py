from underwriting.agents.risk import score_facts
from underwriting.fixtures import APP_1001, enrichment_for
from underwriting.llm import (
    BEDROCK_MODEL,
    OLLAMA_MODEL,
    OLLAMA_URL,
    bedrock_invoke_body,
    bedrock_text,
    ollama_chat_body,
    prompt_text,
    rationale_from_model_text,
)


def _facts():
    return score_facts(enrichment_for(APP_1001))


def test_one_prompt_for_both_transports():
    prompt = prompt_text(APP_1001, _facts())
    assert ollama_chat_body(prompt)["messages"][0]["content"] == prompt
    assert bedrock_invoke_body(prompt)["messages"][0]["content"] == prompt
    assert ollama_chat_body(prompt)["model"] == OLLAMA_MODEL
    assert "google.gemma-3-4b-it" == BEDROCK_MODEL


def test_ollama_call_is_loopback_chat():
    assert OLLAMA_URL == "http://127.0.0.1:11434/api/chat"
    body = ollama_chat_body("rationale please")
    assert body["stream"] is False
    assert body["model"] == "gemma3:4b"


def test_json_parse_failure_keeps_rule_score_13():
    facts = _facts()
    outcome = rationale_from_model_text("not json", facts)
    assert facts["score"] == 13
    assert outcome["score"] == 13
    assert outcome["quality_miss"] is True
    assert "quality miss" in outcome["rationale"]


def test_json_rationale_keeps_rule_score():
    facts = _facts()
    raw = '{"rationale": "Excellent credit and a clear claims history keep this in the low band."}'
    outcome = rationale_from_model_text(raw, facts)
    assert outcome["score"] == 13
    assert outcome["quality_miss"] is False
    assert outcome["rationale"].startswith("Excellent credit")


def test_fenced_json_is_still_the_same_rationale():
    facts = _facts()
    raw = '```json\n{"rationale": "Low band from the rule score."}\n```'
    outcome = rationale_from_model_text(raw, facts)
    assert outcome["quality_miss"] is False
    assert outcome["score"] == 13


def test_bedrock_invoke_body_names_messages_not_a_stream():
    body = bedrock_invoke_body(prompt_text(APP_1001, _facts()))
    assert "stream" not in body
    assert body["max_tokens"] == 256
    assert body["messages"][0]["role"] == "user"


def test_bedrock_text_reads_message_content():
    payload = {"choices": [{"message": {"role": "assistant", "content": '{"rationale": "ok"}'}}]}
    assert "rationale" in bedrock_text(payload)
