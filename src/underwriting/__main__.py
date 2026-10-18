import json
import os
import sys

from underwriting.agents.risk import score_facts
from underwriting.fixtures import APPLICATIONS, enrichment_for
from underwriting.llm import complete, prompt_text, rationale_from_model_text


def format_report(application, facts, outcome, provider):
    lines = [
        f"application: {application['id']}",
        f"name: {application['full_name']}",
        f"product: {application['product']}",
        f"score: {facts['score']}",
        f"band: {facts['band']}",
        f"factors: {json.dumps(facts['factors'])}",
        f"hard_refer: {json.dumps(facts['hard_refer'])}",
        f"provider: {provider}",
        f"rationale: {outcome['rationale']}",
    ]
    if outcome["quality_miss"]:
        lines.append("quality_miss: true")
    return "\n".join(lines) + "\n"


def main(argv=None):
    args = list(sys.argv[1:] if argv is None else argv)
    if len(args) != 1:
        print("usage: python -m underwriting APP-1001", file=sys.stderr)
        return 2
    application = APPLICATIONS.get(args[0])
    if application is None:
        print(f"unknown application {args[0]}", file=sys.stderr)
        return 2
    facts = score_facts(enrichment_for(application))
    provider = os.environ.get("LLM_PROVIDER", "ollama")
    raw = complete(prompt_text(application, facts), provider)
    outcome = rationale_from_model_text(raw, facts)
    sys.stdout.write(format_report(application, facts, outcome, provider))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
