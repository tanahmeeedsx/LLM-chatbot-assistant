import requests
from pydantic import BaseModel, ValidationError
from typing import Literal


class Incident(BaseModel):
    severity: Literal["low", "medium", "high"]
    issue: str
    action: str


schema = Incident.model_json_schema()

response = requests.post(
    "http://localhost:11434/api/generate",
    json={
        "model": "qwen2.5:1.5b",
        "prompt": (
            "Analyze this incident: CPU usage is 95% for 10 minutes. "
            "Return severity, issue, and a recommended action."
        ),
        "format": schema,
        "stream": False
    },
    timeout=120
)

response.raise_for_status()
raw_output = response.json()["response"]
print("Raw JSON:", raw_output)

try:
    incident = Incident.model_validate_json(raw_output)
    print("\nVALIDATED OUTPUT:")
    print(incident.model_dump())
except ValidationError as error:
    print("Validation failed:", error)
