from typing import Protocol

from app.types import ClassificationResult


class ClassifierProtocol(Protocol):
    def classify(self, subject: str, message: str) -> ClassificationResult: ...


class MailerProtocol(Protocol):
    def send_notification(
        self,
        name: str,
        email: str,
        subject: str,
        message: str,
        result: ClassificationResult,
        team_email: str,
    ) -> None: ...

    def send_auto_reply(self, name: str, email: str, subject: str) -> None: ...
