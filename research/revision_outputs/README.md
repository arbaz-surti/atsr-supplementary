# Expanded-evaluation generation records

Production records for `ATSR-SREP-R2-v1.0` will be written beneath a directory named
after the protocol ID. The controlled runner creates:

- `queue-manifest.json`: the deterministic randomized queue and frozen-input hashes;
- `attempts.jsonl`: append-only request/response records for every attempt, including
  transport failures and invalid-JSON retries;
- `outputs.jsonl`: parsed terminal JSON outputs, including schema-invalid outputs;
- `run-summary.json`: resumable progress counts.

The runner is deliberately dry-run-only unless `--execute` and the exact protocol ID
confirmation are both supplied. Do not edit generated JSONL records by hand.

For production generation, place the credential in the project-root `.env` file as
`OPENROUTER_API_KEY=...`. The runner loads it locally and never writes it into request
records. `.env` is excluded by the project `.gitignore`.

Offline validation:

```bash
PYTHONDONTWRITEBYTECODE=1 python3 research/test_revision_generation.py
python3 research/run_revision_generation.py
```

The second command validates the frozen protocol, constructs the complete queue, and
checks a representative request payload without writing files or calling OpenRouter.
Production execution may use bounded `--workers` concurrency; this affects wall-clock
time only. Queue identities, payloads, retry limits, and append-only archival remain
unchanged.
