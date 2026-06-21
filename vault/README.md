# HashiCorp Vault Secrets Storage - Project Polaris

HashiCorp Vault is run in dev mode (`-dev`) for local testing.

## Credentials

* **Vault Address:** `http://localhost:8200`
* **Root Token:** `polaris-root-token`

## Secrets Configuration

Secrets are stored inside the KV-v2 engine (mounted at `secret/`) at path `polaris`.

### Secrets Schema

The Flask application reads the following secrets from `secret/data/polaris`:

1. `secret_key`: Used for Flask session cryptographical signing (e.g. `polaris_vault_secret_key`).
2. `db_path`: Defines the relative database path (e.g. `database/polaris.db`).

## Dynamic Fetching

During startup, the Flask application attempts to connect to Vault, write the default values if they are missing, and retrieve them to initialize the app.
If Vault is down or unreachable, the application falls back gracefully to hardcoded defaults in the code.
