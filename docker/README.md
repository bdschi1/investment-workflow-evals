# Docker

Reproducible container for the eval runner (`iwe-eval`) and Streamlit RLHF Studio (`streamlit run studio/app.py`).

## Build

```bash
docker compose build
```

Cold build: ~2-4 minutes.

## Run

```bash
docker compose up -d

# Eval runner CLI
docker compose exec app iwe-eval --help
docker compose exec app python -m tools.eval_runner list

# Studio (port 8501 exposed)
docker compose exec app streamlit run studio/app.py --server.address 0.0.0.0

# Tests
docker compose exec app pytest tests/ -v

docker compose down
```

## Verify

```bash
docker compose build                   # exit 0
docker compose up -d
docker compose exec app iwe-eval --help  # prints click usage
docker compose exec app pytest -q        # exit 0
```

## Notes

- Studio extras (`streamlit`, providers) install with the `studio` extra. To include them in the image, change `pip install -e ".[dev,llm]"` in `Dockerfile` to `".[dev,llm,studio]"`.
- Eval results persist on the host at `./results` and `./outputs` via bind mounts.
