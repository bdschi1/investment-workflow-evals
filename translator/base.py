"""Base translator ABC."""
from __future__ import annotations
from abc import ABC, abstractmethod
from .audience import AudienceConfig
from .outputs import TranslatedResearch, AccuracyReport


class BaseTranslator(ABC):
    """ABC for research translators."""

    @abstractmethod
    def translate(
        self,
        institutional_text: str,
        audience: AudienceConfig,
        ticker: str = "",
        company_name: str = "",
    ) -> TranslatedResearch:
        """Translate institutional research for target audience."""
        ...

    @abstractmethod
    def validate_accuracy(
        self,
        original: str,
        translated: TranslatedResearch,
        key_facts: list[str] | None = None,
    ) -> AccuracyReport:
        """Check that key facts survived translation."""
        ...
