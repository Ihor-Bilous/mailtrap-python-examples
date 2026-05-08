from dataclasses import dataclass


@dataclass(frozen=True)
class ClassificationResult:
    category: str
    urgency: str
    reason: str
