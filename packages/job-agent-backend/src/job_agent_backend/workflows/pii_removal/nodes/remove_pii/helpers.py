"""Helper functions for PII removal."""

from typing import Callable

from job_agent_backend.model_providers import IModelFactory

from .prompts import REMOVE_PII_PROMPT


def create_anonymize_text(model_factory: IModelFactory) -> Callable[[str], str]:
    """
    Factory function to create an anonymize_text function with injected dependencies.

    Args:
        model_factory: Factory used to create model instances

    Returns:
        Configured anonymize_text function
    """

    def anonymize_text(text: str) -> str:
        """
        Anonymize PII in the given text using phi3:mini via Ollama.

        Args:
            text: Text containing potential PII

        Returns:
            Anonymized text with PII removed

        Raises:
            RuntimeError: If anonymization fails or returns invalid content
        """
        model = model_factory.get_model(model_id="pii-removal")

        messages = REMOVE_PII_PROMPT.format_messages(cv_content=text)

        try:
            response = model.invoke(messages)
        except Exception as e:
            raise RuntimeError(f"Failed to invoke PII anonymization model: {e}") from e

        if hasattr(response, "content"):
            content = response.content
            anonymized_text = content if isinstance(content, str) else str(content)
        else:
            anonymized_text = str(response)

        anonymized_text = anonymized_text.strip()

        if not anonymized_text:
            raise RuntimeError("PII anonymization returned empty content")

        return anonymized_text

    return anonymize_text
