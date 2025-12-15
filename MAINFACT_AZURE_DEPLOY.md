# Mainfact Azure Deploy Guide

Comprehensive instructions for rebuilding the complete Irado environment on Azure with `mainfact-azure-deploy.sh`.

---

## 🧭 What the script does

When you run `./mainfact-azure-deploy.sh`, it will:

1. Validate local tooling (`az`, `docker`, `psql`, `python3`, `tar`) and install `psycopg2-binary` if missing.
2. Ensure foundational Azure resources exist (resource group, Azure Container Registry, optional storage account).
3. Provision or update Azure Database for PostgreSQL Flexible Server, including firewall rules for Azure services and your current IP.
4. Create/refresh the `irado_chat` database schema, import KOAD data from `chatbot/koad.csv`, and seed the system prompt from `chatbot/prompts/system_prompt.txt`.
5. Build fresh chatbot and dashboard Docker images, push them to ACR with timestamped tags, and deploy them to Linux Web Apps on a shared App Service plan.
6. Restart both Web Apps and package a local backup archive (with optional upload to Azure Storage).

The result is a fully bootstrapped environment with database content, container images, and application configuration ready to serve traffic.

---

## ✅ Prerequisites

Local machine:

- Docker daemon running and logged in (for building/pushing images).
- Azure CLI installed and authenticated: `az login` (and `az account set --subscription <id>` if needed).
- PostgreSQL client tools (`psql`, `pg_dump`; the script checks for both and prompts to install if absent).
- Python 3.11+ with `pip`.

Azure subscription:

- Permissions to create/update the following resources:
  - Resource group
  - Azure Container Registry (Basic SKU)
  - Azure Database for PostgreSQL Flexible Server (Burstable, B1ms)
  - App Service plan + Linux Web Apps
  - Storage account (optional, for backup uploads)

Make sure the subscription has been cleared of any of the old Irado resources you removed to avoid naming conflicts.

---

## ⚙️ Configurable parameters

The script ships with sane defaults matching the historic environment. Override them via environment variables before running if you need alternative names or secure credentials:

| Variable | Default | Purpose |
|----------|---------|---------|
| `RESOURCE_GROUP` | `irado-rg` | Azure resource group name |
| `LOCATION` | `westeurope` | Azure region for all resources |
| `ACR_NAME` | `irado` | Container registry name (global namespace) |
| `APP_SERVICE_PLAN` | `irado-app-service-plan` | Linux App Service plan |
| `CHATBOT_APP_NAME` | `irado-chatbot-app` | Chatbot Web App name |
| `DASHBOARD_APP_NAME` | `irado-dashboard-app` | Dashboard Web App name |
| `POSTGRES_SERVER` | `irado-chat-db` | Flexible Server hostname prefix |
| `POSTGRES_ADMIN_USER` | `irado_admin` | DB admin username |
| `POSTGRES_ADMIN_PASSWORD` | `lqBp6OF31+wCNXzyTMvasFrspdtL+IWPGVtooy2zjS4=` | DB admin password (replace in production!) |
| `CHAT_DB_NAME` | `irado_chat` | Database name |
| `STORAGE_ACCOUNT` | `iradostorage` | Storage account for backups (optional) |
| `STORAGE_CONTAINER` | `backups` | Blob container for archives |
| `AZURE_OPENAI_*` | legacy values | AI credentials injected into Web Apps |
| `CHAT_BASIC_AUTH_*` | `irado` / `20Irado25!` | HTTP basic auth for chatbot |
| `SYSTEM_PROMPT_VERSION` | `v${VERSION.txt}` | Version label stored in DB |

> 🛡️ **Security tip:** Update secrets such as `POSTGRES_ADMIN_PASSWORD`, `AZURE_OPENAI_API_KEY`, and `CHAT_BASIC_AUTH_PASSWORD` before the first run in a new environment.

---

## ▶️ Running the script

```bash
cd /opt/irado-azure
chmod +x mainfact-azure-deploy.sh         # already done once, but safe to repeat
export RESOURCE_GROUP=mainfact-irado-rg   # example override (optional)
./mainfact-azure-deploy.sh
```

The script emits progress logs with colored status indicators. It will exit on the first error. Re-run after resolving any reported issue; the steps are idempotent.

---

## 💾 Stand-alone backup (before teardown)

If you only need the latest database dumps and seed assets (for example before deleting Azure resources), run the dedicated backup script:

```bash
cd /opt/irado-azure
chmod +x mainfact-azure-backup.sh      # once
export STORAGE_ACCOUNT=<your-storage>  # optional; skips upload when unset
./mainfact-azure-backup.sh
```

It will:

- Open a temporary firewall rule for your public IP (if possible).
- Produce both plain-text and custom-format dumps of `irado_chat`.
- Package the dumps together with `VERSION.txt`, `chatbot/koad.csv`, `chatbot/prompts/system_prompt.txt`, and the `data/` directory.
- Upload the tarball to `https://<storage>.blob.core.windows.net/<container>/` when `STORAGE_ACCOUNT` is defined (defaults to container `backups`).

Artifacts are written to `backups/` in the repository root. Verify the `.sql`, `.dump`, and `.tar.gz` files before decommissioning Azure resources.

---

## 📦 Artifacts created

- **Docker images:** `chatbot-<timestamp>` and `dashboard-<timestamp>` in `irado.azurecr.io`.
- **PostgreSQL schema:** `chat_sessions`, `chat_messages`, `chat_memory`, `bedrijfsklanten`, `csv_uploads`, `dashboard_logs`, `system_prompts`, `system_prompt_state`.
- **Seed data:** KOAD records imported from `chatbot/koad.csv`, active system prompt from `chatbot/prompts/system_prompt.txt`.
- **Database dumps:** `backups/irado_chat-<timestamp>.sql` (plain text) and `.dump` (custom format) for point-in-time restores.
- **Backups:** `backups/irado-seed-<timestamp>.tar.gz` bundling the dumps, KOAD CSV, system prompt, and `data/`; optionally uploaded to Blob Storage `https://<storage>.blob.core.windows.net/<container>/`.

---

## 🔍 Verification checklist

1. **Health probes**
   - `curl https://<chatbot-app>.azurewebsites.net/health`
   - Visit `https://<dashboard-app>.azurewebsites.net`
2. **Database**
   - In Azure Portal > PostgreSQL > Query editor, run `SELECT COUNT(*) FROM bedrijfsklanten;`
   - Check `SELECT version, is_active FROM system_prompts;`
3. **Container logs**
   - `az webapp log tail --resource-group <rg> --name <app>`
4. **Backups**
   - Confirm the `.sql`, `.dump`, and tarball live under `backups/` (and, if configured, in Blob Storage).

---

## 🛠️ Troubleshooting

- **ACR name already taken:** choose a unique `ACR_NAME` (3–50 lowercase letters/numbers).
- **Storage account creation fails:** storage names must be globally unique, lowercase, 3–24 chars; script will continue without blob uploads.
- **Firewall blocks local DB bootstrap:** ensure your current IP was added, or temporarily disable the bootstrap block and run `psql` from a host inside Azure.
- **Docker push authentication errors:** rerun `az acr login --name <acr>` and verify Docker is logged in.
- **`psycopg2` build issues:** install system prerequisites (`sudo apt-get install libpq-dev gcc`) before rerunning the script.

---

## 🔁 Iterating after deployment

- Re-run the script whenever the codebase changes or you need to reprovision infrastructure; it will rebuild images and redeploy while preserving data already in PostgreSQL (it truncates the KOAD table intentionally).
- Use `SYSTEM_PROMPT_VERSION` to tag new prompt releases (e.g., `export SYSTEM_PROMPT_VERSION=v2.3.0`).
- Clean up old backup archives locally if disk space becomes an issue.

---

## 📚 Related resources

- Script source: `mainfact-azure-deploy.sh`
- Legacy deployment scripts for reference:
  - `deploy-to-azure.sh` (chatbot only)
  - `deploy-dashboard-to-azure.sh`
  - `azure/deploy.sh`
- Additional documentation in `AZURE_DEPLOYMENT_GUIDE.md` and `MIGRATION_README.md`

---

Ready to roll! 🚀 Run the script, verify the endpoints, and the Irado stack is back online. If you need to tailor the deployment for other environments, duplicate the script with updated defaults and secrets.***
