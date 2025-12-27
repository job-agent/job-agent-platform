"""HuggingFace Transformers provider for local model inference.

This provider loads models directly into your application's memory.
NO separate server needed - the model runs in the same Python process.

Models are downloaded once to ~/.cache/huggingface/ and loaded from there.
Requires significant RAM/VRAM (8-16GB+ for larger models).
"""

import os
from typing import Any, Optional

from .base import BaseModelProvider
from ..contracts.provider_interface import ModelInstance


class TransformersProvider(BaseModelProvider):
    """HuggingFace Transformers provider for running models in-process.

    Unlike Ollama (server-based), this loads the model directly into your
    Python application's memory. No HTTP calls, no separate server process.
    """

    def __init__(
        self,
        model_name: str,
        temperature: float = 0.0,
        device: Optional[str] = None,
        model_kwargs: Optional[dict] = None,
        pipeline_kwargs: Optional[dict] = None,
        task: str = "text-generation",
        **kwargs: Any,
    ):
        """Initialize Transformers provider.

        Args:
            model_name: HuggingFace model identifier (e.g., 'ai4privacy/llama-ai4privacy-english-anonymiser-openpii')
            temperature: Temperature for generation
            device: Device to run on ('cuda', 'cpu', or None for auto)
            model_kwargs: Additional arguments for model loading
            pipeline_kwargs: Additional arguments for pipeline creation
            task: Task type ('text-generation', 'token-classification')
            **kwargs: Additional HuggingFacePipeline parameters
        """
        super().__init__(model_name, temperature, **kwargs)
        self.device = device or os.getenv("TRANSFORMERS_DEVICE", "auto")
        self.model_kwargs = model_kwargs or {}
        self.pipeline_kwargs = pipeline_kwargs or {}
        self.task = task

    def get_model(self) -> ModelInstance:
        """Get HuggingFace pipeline model instance."""
        try:
            from langchain_huggingface import HuggingFacePipeline, HuggingFaceEmbeddings
            from transformers import (
                AutoTokenizer,
                AutoModelForCausalLM,
                AutoModelForTokenClassification,
                pipeline,
            )
        except ImportError:
            raise ImportError(
                "transformers and langchain-huggingface not installed. "
                "Install them with: pip install transformers langchain-huggingface"
            )

        if self.task == "embedding":
            return HuggingFaceEmbeddings(
                model_name=self.model_name,
                model_kwargs=self.model_kwargs,
                encode_kwargs=self.pipeline_kwargs,
                **self.kwargs,
            )

        # Load tokenizer
        tokenizer = AutoTokenizer.from_pretrained(self.model_name)

        if self.task == "token-classification":
            # Load model for token classification
            model = AutoModelForTokenClassification.from_pretrained(
                self.model_name, device_map=self.device, **self.model_kwargs
            )

            # Create token classification pipeline
            # Note: For token classification, we return the raw pipeline
            # as LangChain's HuggingFacePipeline is designed for text generation
            return pipeline(
                "token-classification", model=model, tokenizer=tokenizer, **self.pipeline_kwargs
            )

        # Default: text-generation
        model = AutoModelForCausalLM.from_pretrained(
            self.model_name, device_map=self.device, **self.model_kwargs
        )

        # Create text generation pipeline
        pipe = pipeline(
            "text-generation",
            model=model,
            tokenizer=tokenizer,
            temperature=self.temperature,
            **self.pipeline_kwargs,
        )

        # Wrap in LangChain HuggingFacePipeline
        return HuggingFacePipeline(pipeline=pipe, **self.kwargs)
