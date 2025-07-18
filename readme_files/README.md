# Re-Style Project

## Handling Secret Credentials

- **Never commit real secret files** (API keys, credentials, etc.) to the repository.
- All secret files are listed in `.gitignore` and will not be committed.
- Use the provided template files (e.g., `local_settings_template.py`) to create your own secret files (e.g., `local_settings.py`, `local_settings_secrets.py`).
- Place your real credentials in these files locally.
- If you ever accidentally commit a secret, use [BFG Repo-Cleaner](https://rtyley.github.io/bfg-repo-cleaner/) to remove it from git history.
- For production, use environment variables or secret managers to inject secrets securely.
