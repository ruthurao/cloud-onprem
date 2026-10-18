FROM python:3.12-slim

WORKDIR /app
COPY pyproject.toml ./
COPY src ./src
RUN pip install --no-cache-dir .
ENV LLM_PROVIDER=bedrock
ENTRYPOINT ["python", "-m", "underwriting"]
CMD ["APP-1001"]
