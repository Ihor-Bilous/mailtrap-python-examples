from dataclasses import dataclass


@dataclass
class WelcomeContent:
    headline: str
    body: str
    cta_text: str
