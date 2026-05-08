from typing import Protocol

from app.types import WelcomeContent


class PersonalizerProtocol(Protocol):
    def generate(
        self, name: str, role: str, company_size: str, use_case: str
    ) -> WelcomeContent: ...


class MailerProtocol(Protocol):
    def send_welcome(self, name: str, email: str, content: WelcomeContent) -> None: ...
