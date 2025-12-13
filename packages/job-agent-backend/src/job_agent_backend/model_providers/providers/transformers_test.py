"""Tests for TransformersProvider class."""

import os
from unittest.mock import MagicMock, patch


from job_agent_backend.model_providers.providers.transformers import TransformersProvider


class TestTransformersProviderInit:
    """Tests for TransformersProvider initialization."""

    def test_stores_model_name(self) -> None:
        provider = TransformersProvider(model_name="bert-base-uncased")

        assert provider.model_name == "bert-base-uncased"

    def test_uses_default_temperature(self) -> None:
        provider = TransformersProvider(model_name="bert-base-uncased")

        assert provider.temperature == 0.0

    def test_stores_custom_temperature(self) -> None:
        provider = TransformersProvider(model_name="bert-base-uncased", temperature=0.7)

        assert provider.temperature == 0.7

    def test_uses_default_device_auto(self) -> None:
        with patch.dict(os.environ, {}, clear=True):
            os.environ.pop("TRANSFORMERS_DEVICE", None)
            provider = TransformersProvider(model_name="bert-base-uncased")

        assert provider.device == "auto"

    def test_uses_device_from_environment(self) -> None:
        with patch.dict(os.environ, {"TRANSFORMERS_DEVICE": "cuda"}):
            provider = TransformersProvider(model_name="bert-base-uncased")

        assert provider.device == "cuda"

    def test_parameter_device_overrides_environment(self) -> None:
        with patch.dict(os.environ, {"TRANSFORMERS_DEVICE": "cuda"}):
            provider = TransformersProvider(model_name="bert-base-uncased", device="cpu")

        assert provider.device == "cpu"

    def test_uses_default_task_text_generation(self) -> None:
        provider = TransformersProvider(model_name="bert-base-uncased")

        assert provider.task == "text-generation"

    def test_stores_custom_task(self) -> None:
        provider = TransformersProvider(model_name="bert-base-uncased", task="token-classification")

        assert provider.task == "token-classification"

    def test_uses_empty_model_kwargs_by_default(self) -> None:
        provider = TransformersProvider(model_name="bert-base-uncased")

        assert provider.model_kwargs == {}

    def test_stores_custom_model_kwargs(self) -> None:
        provider = TransformersProvider(
            model_name="bert-base-uncased", model_kwargs={"torch_dtype": "float16"}
        )

        assert provider.model_kwargs == {"torch_dtype": "float16"}

    def test_uses_empty_pipeline_kwargs_by_default(self) -> None:
        provider = TransformersProvider(model_name="bert-base-uncased")

        assert provider.pipeline_kwargs == {}

    def test_stores_custom_pipeline_kwargs(self) -> None:
        provider = TransformersProvider(
            model_name="bert-base-uncased", pipeline_kwargs={"max_length": 512}
        )

        assert provider.pipeline_kwargs == {"max_length": 512}

    def test_stores_additional_kwargs(self) -> None:
        provider = TransformersProvider(model_name="bert-base-uncased", custom_param="value")

        assert provider.kwargs == {"custom_param": "value"}


class TestTransformersProviderGetModelEmbedding:
    """Tests for TransformersProvider.get_model with embedding task."""

    def test_returns_huggingface_embeddings_for_embedding_task(self) -> None:
        mock_embeddings = MagicMock()

        with patch("langchain_huggingface.HuggingFaceEmbeddings", mock_embeddings):
            provider = TransformersProvider(
                model_name="sentence-transformers/all-MiniLM-L6-v2",
                task="embedding",
                model_kwargs={"device": "cpu"},
                pipeline_kwargs={"normalize_embeddings": True},
            )
            result = provider.get_model()

        mock_embeddings.assert_called_once_with(
            model_name="sentence-transformers/all-MiniLM-L6-v2",
            model_kwargs={"device": "cpu"},
            encode_kwargs={"normalize_embeddings": True},
        )
        assert result == mock_embeddings.return_value


class TestTransformersProviderGetModelTokenClassification:
    """Tests for TransformersProvider.get_model with token-classification task."""

    def test_returns_pipeline_for_token_classification_task(self) -> None:
        mock_tokenizer = MagicMock()
        mock_model = MagicMock()
        mock_pipeline = MagicMock()

        with (
            patch("transformers.AutoTokenizer") as mock_auto_tokenizer,
            patch("transformers.AutoModelForTokenClassification") as mock_auto_model,
            patch("transformers.pipeline", mock_pipeline),
        ):
            mock_auto_tokenizer.from_pretrained.return_value = mock_tokenizer
            mock_auto_model.from_pretrained.return_value = mock_model

            provider = TransformersProvider(
                model_name="dslim/bert-base-NER",
                task="token-classification",
                device="cpu",
                pipeline_kwargs={"aggregation_strategy": "simple"},
            )
            result = provider.get_model()

        mock_auto_tokenizer.from_pretrained.assert_called_once_with("dslim/bert-base-NER")
        mock_auto_model.from_pretrained.assert_called_once_with(
            "dslim/bert-base-NER", device_map="cpu"
        )
        mock_pipeline.assert_called_once_with(
            "token-classification",
            model=mock_model,
            tokenizer=mock_tokenizer,
            aggregation_strategy="simple",
        )
        assert result == mock_pipeline.return_value


class TestTransformersProviderGetModelTextGeneration:
    """Tests for TransformersProvider.get_model with text-generation task."""

    def test_returns_huggingface_pipeline_for_text_generation_task(self) -> None:
        mock_tokenizer = MagicMock()
        mock_model = MagicMock()
        mock_pipe = MagicMock()
        mock_hf_pipeline = MagicMock()

        with (
            patch("transformers.AutoTokenizer") as mock_auto_tokenizer,
            patch("transformers.AutoModelForCausalLM") as mock_auto_model,
            patch("transformers.pipeline", return_value=mock_pipe) as mock_pipeline_func,
            patch("langchain_huggingface.HuggingFacePipeline", mock_hf_pipeline),
        ):
            mock_auto_tokenizer.from_pretrained.return_value = mock_tokenizer
            mock_auto_model.from_pretrained.return_value = mock_model

            provider = TransformersProvider(
                model_name="gpt2",
                task="text-generation",
                temperature=0.7,
                device="cpu",
                pipeline_kwargs={"max_new_tokens": 50},
            )
            result = provider.get_model()

        mock_auto_tokenizer.from_pretrained.assert_called_once_with("gpt2")
        mock_auto_model.from_pretrained.assert_called_once_with("gpt2", device_map="cpu")
        mock_pipeline_func.assert_called_once_with(
            "text-generation",
            model=mock_model,
            tokenizer=mock_tokenizer,
            temperature=0.7,
            max_new_tokens=50,
        )
        mock_hf_pipeline.assert_called_once_with(pipeline=mock_pipe)
        assert result == mock_hf_pipeline.return_value

    def test_passes_model_kwargs_to_model_loading(self) -> None:
        mock_tokenizer = MagicMock()
        mock_model = MagicMock()
        mock_pipe = MagicMock()
        mock_hf_pipeline = MagicMock()

        with (
            patch("transformers.AutoTokenizer") as mock_auto_tokenizer,
            patch("transformers.AutoModelForCausalLM") as mock_auto_model,
            patch("transformers.pipeline", return_value=mock_pipe),
            patch("langchain_huggingface.HuggingFacePipeline", mock_hf_pipeline),
        ):
            mock_auto_tokenizer.from_pretrained.return_value = mock_tokenizer
            mock_auto_model.from_pretrained.return_value = mock_model

            provider = TransformersProvider(
                model_name="gpt2",
                model_kwargs={"torch_dtype": "float16", "low_cpu_mem_usage": True},
            )
            provider.get_model()

        mock_auto_model.from_pretrained.assert_called_once_with(
            "gpt2",
            device_map="auto",
            torch_dtype="float16",
            low_cpu_mem_usage=True,
        )
