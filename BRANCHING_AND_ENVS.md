## Branches & Environments (dev/prod)

### Goal
We run **two isolated environments** in the **same Azure subscription**:

- **prod**: the existing live stack (current Resource Group)
- **dev**: a full clone for testing changes safely

### Naming convention
- **Resource Group**
  - prod: `irado-rg`
  - dev: `irado-dev-rg`

- **Web Apps**
  - prod: `irado-chatbot-app`, `irado-dashboard-app`
  - dev: `irado-dev-chatbot-app`, `irado-dev-dashboard-app`

- **Postgres**
  - prod server/db: `irado-chat-db` / `irado_chat`
  - dev server/db: `irado-dev-chat-db` / `irado_dev_chat` (empty DB)

### Git workflow (simple & professional)
- **main**: stable (maps to prod)
- **dev**: integration/testing (maps to dev)

Typical flow:
1. Work on feature branch → merge into `dev`
2. Deploy `dev` to Azure dev RG and test
3. Merge `dev` → `main`
4. Deploy `main` to Azure prod RG

### Secrets / env values
Secrets are **not stored in git**.

- Source of truth: **Azure App Settings** (recommended)
- Local export (do NOT commit):

```bash
./scripts/azure-appsettings-export.sh --name irado-chatbot-app --rg irado-rg --out .env.prod.local
./scripts/azure-appsettings-export.sh --name irado-dashboard-app --rg irado-rg --out .env.dashboard.prod.local
```

### Dev DB password (server-only)
On this server we keep the dev database password locally in:

- `/opt/irado-azure/.env.dev.local`  *(gitignored)*

The dev deploy scripts (`--env dev`) will auto-load this file if present so fresh deploys do not miss `POSTGRES_PASSWORD`.

### Next step (implementation)
We will update deployment scripts to accept `--env dev|prod` (or `ENV=dev|prod`)
and automatically pick the correct Resource Group + app names.

