"""Tests for /v1/chat/completions endpoint and model listing."""

from unittest.mock import patch

from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


class TestListModels:
    def test_returns_12_models(self):
        resp = client.get("/v1/models")
        assert resp.status_code == 200
        data = resp.json()
        assert data["object"] == "list"
        assert len(data["data"]) == 12

    def test_auto_model_present(self):
        resp = client.get("/v1/models")
        models = {m["id"] for m in resp.json()["data"]}
        assert "auto" in models

    def test_antigravity_models_present(self):
        resp = client.get("/v1/models")
        models = {m["id"] for m in resp.json()["data"]}
        assert "claude-sonnet-4-6" in models
        assert "claude-opus-4-6-thinking" in models

    def test_openrouter_models_present(self):
        resp = client.get("/v1/models")
        models = {m["id"] for m in resp.json()["data"]}
        assert "nemotron-ultra" in models
        assert "qwen3-coder" in models
        assert "kimi-k26" in models
        assert "owl-alpha" in models
        assert "nemotron-super" in models
        assert "llama-70b" in models
        assert "qwen3-next" in models
        assert "hermes-405b" in models

    def test_groq_model_present(self):
        resp = client.get("/v1/models")
        models = {m["id"] for m in resp.json()["data"]}
        assert "groq-llama" in models

    def test_antigravity_models_have_correct_owned_by(self):
        resp = client.get("/v1/models")
        for m in resp.json()["data"]:
            if m["id"].startswith("claude"):
                assert m["owned_by"] == "antigravity"


class TestModelMapConsistency:
    def test_every_model_in_list_has_map_entry(self):
        from app.routes.chat import MODELS_LIST, MODEL_MAP
        for m in MODELS_LIST:
            mid = m["id"]
            if mid == "auto":
                continue
            assert mid in MODEL_MAP, f"Model '{mid}' in MODELS_LIST but not in MODEL_MAP"

    def test_every_map_entry_has_model_in_list(self):
        from app.routes.chat import MODELS_LIST, MODEL_MAP
        model_ids = {m["id"] for m in MODELS_LIST}
        for key in MODEL_MAP:
            assert key in model_ids, f"Model '{key}' in MODEL_MAP but not in MODELS_LIST"

    def test_every_map_value_is_valid_provider(self):
        from app.routes.chat import MODEL_MAP
        from app.services.ai import create_provider
        for model_id, provider_name in MODEL_MAP.items():
            p = create_provider(provider_name)
            assert p is not None
            assert hasattr(p, 'generate')


class TestChatCompletionsValidation:
    def test_missing_messages_returns_400(self):
        resp = client.post("/v1/chat/completions", json={})
        assert resp.status_code == 400

    def test_empty_messages_returns_400(self):
        resp = client.post("/v1/chat/completions", json={"messages": []})
        assert resp.status_code == 400

    def test_invalid_model_falls_through_chain(self):
        with patch("app.routes.chat._call_provider") as mock_call:
            mock_call.return_value = {"text": "fallback_response"}
            resp = client.post("/v1/chat/completions", json={
                "model": "nonexistent-model",
                "messages": [{"role": "user", "content": "hello"}],
            })
            assert resp.status_code == 200
            data = resp.json()
            assert "fallback_response" in data["choices"][0]["message"]["content"]

    def test_antigravity_sonnet_specific_model(self):
        with patch("app.routes.chat._call_provider") as mock_call:
            mock_call.return_value = {"text": "sonnet_response"}
            resp = client.post("/v1/chat/completions", json={
                "model": "claude-sonnet-4-6",
                "messages": [{"role": "user", "content": "hello"}],
            })
            assert resp.status_code == 200
            assert "sonnet_response" in resp.json()["choices"][0]["message"]["content"]

    def test_antigravity_opus_specific_model(self):
        with patch("app.routes.chat._call_provider") as mock_call:
            mock_call.return_value = {"text": "opus_response"}
            resp = client.post("/v1/chat/completions", json={
                "model": "claude-opus-4-6-thinking",
                "messages": [{"role": "user", "content": "hello"}],
            })
            assert resp.status_code == 200
            assert "opus_response" in resp.json()["choices"][0]["message"]["content"]

    def test_groq_specific_model(self):
        with patch("app.routes.chat._call_provider") as mock_call:
            mock_call.return_value = {"text": "groq_response"}
            resp = client.post("/v1/chat/completions", json={
                "model": "groq-llama",
                "messages": [{"role": "user", "content": "hello"}],
            })
            assert resp.status_code == 200
            assert "groq_response" in resp.json()["choices"][0]["message"]["content"]

    def test_auto_mode_routes_through_chain(self):
        with patch("app.routes.chat._call_provider") as mock_call:
            mock_call.return_value = {"text": "auto_response"}
            resp = client.post("/v1/chat/completions", json={
                "model": "auto",
                "messages": [{"role": "user", "content": "hello"}],
            })
            assert resp.status_code == 200
            assert "auto_response" in resp.json()["choices"][0]["message"]["content"]

    def test_system_prompt_is_passed(self):
        with patch("app.routes.chat._call_provider") as mock_call:
            mock_call.return_value = {"text": "system_used"}
            resp = client.post("/v1/chat/completions", json={
                "model": "groq-llama",
                "messages": [
                    {"role": "system", "content": "You are a helpful assistant"},
                    {"role": "user", "content": "hello"},
                ],
            })
            assert resp.status_code == 200
            assert "system_used" in resp.json()["choices"][0]["message"]["content"]

    def test_streaming_mode(self):
        with patch("app.routes.chat._call_provider") as mock_call:
            mock_call.return_value = {"text": "stream_text"}
            resp = client.post("/v1/chat/completions", json={
                "model": "groq-llama",
                "messages": [{"role": "user", "content": "hello"}],
                "stream": True,
            })
            assert resp.status_code == 200
            assert resp.headers["content-type"].startswith("text/event-stream")

    def test_temperature_and_max_tokens_passed(self):
        with patch("app.routes.chat._call_provider") as mock_call:
            mock_call.return_value = {"text": "response"}
            resp = client.post("/v1/chat/completions", json={
                "model": "groq-llama",
                "messages": [{"role": "user", "content": "hello"}],
                "temperature": 0.7,
                "max_tokens": 100,
            })
            assert resp.status_code == 200

    def test_all_providers_fail_returns_502(self):
        with patch("app.routes.chat._call_provider") as mock_call:
            mock_call.return_value = {"error": "provider_failed"}
            resp = client.post("/v1/chat/completions", json={
                "model": "auto",
                "messages": [{"role": "user", "content": "hello"}],
            })
            assert resp.status_code == 502
            data = resp.json()
            assert "provider_failed" in data["error"]["message"]
