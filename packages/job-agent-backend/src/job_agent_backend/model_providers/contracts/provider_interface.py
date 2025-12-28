"""Abstract interface for model providers."""

from typing import TYPE_CHECKING, Protocol, Union

if TYPE_CHECKING:
    from langchain_core.embeddings import Embeddings
    from langchain_core.language_models import BaseChatModel, BaseLLM
    from transformers import Pipeline as TransformersPipeline

    # Union of all model types that providers can return:
    # - BaseChatModel: Chat models (ChatOpenAI, ChatOllama, etc.)
    # - BaseLLM: LLM wrappers (HuggingFacePipeline, etc.)
    # - Embeddings: Embedding models (HuggingFaceEmbeddings, etc.)
    # - TransformersPipeline: Raw HuggingFace pipelines for token classification
    ModelInstance = Union[BaseChatModel, BaseLLM, Embeddings, TransformersPipeline]
else:
    # At runtime, we use a type alias that allows any type
    # This avoids importing heavy ML libraries just for type hints
    from typing import Any

    ModelInstance = Any


class IModelProvider(Protocol):
    """Protocol for all AI model providers.

    This interface defines the contract that all model providers must implement.
    Concrete implementations (OpenAI, Ollama, Transformers, etc.) inherit from
    BaseModelProvider which implements this interface.
    """

    def get_model(self) -> ModelInstance:
        """Get the model instance.

        Returns:
            A model instance. Expected types:
            - BaseChatModel: LangChain chat models (ChatOpenAI, ChatOllama, etc.)
            - Embeddings: LangChain embedding models (HuggingFaceEmbeddings, etc.)
            - Pipeline: HuggingFace transformers pipeline for token classification
        """
        ...
