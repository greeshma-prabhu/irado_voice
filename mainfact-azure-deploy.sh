#!/usr/bin/env bash
set -euo pipefail

# Mainfact Azure deployment script for full Irado stack rebuild

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$ROOT_DIR"

RED='\033[0;31m'
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m'

log() { echo -e "${BLUE}[$(date '+%Y-%m-%d %H:%M:%S')]${NC} $*"; }
success() { echo -e "${GREEN}✅${NC} $*"; }
warn() { echo -e "${YELLOW}⚠️ ${NC} $*"; }
error() { echo -e "${RED}❌${NC} $*"; }

RESOURCE_GROUP="${RESOURCE_GROUP:-irado-rg}"
LOCATION="${LOCATION:-westeurope}"
ACR_NAME="${ACR_NAME:-irado}"
ACR_SKU="${ACR_SKU:-Basic}"
APP_SERVICE_PLAN="${APP_SERVICE_PLAN:-irado-app-service-plan}"
POSTGRES_SERVER="${POSTGRES_SERVER:-irado-chat-db}"
POSTGRES_ADMIN_USER="${POSTGRES_ADMIN_USER:-irado_admin}"
POSTGRES_ADMIN_PASSWORD="${POSTGRES_ADMIN_PASSWORD:-lqBp6OF31+wCNXzyTMvasFrspdtL+IWPGVtooy2zjS4=}"
POSTGRES_SKU="${POSTGRES_SKU:-Standard_B1ms}"
POSTGRES_TIER="${POSTGRES_TIER:-Burstable}"
POSTGRES_STORAGE_MB="${POSTGRES_STORAGE_MB:-32768}"
POSTGRES_VERSION="${POSTGRES_VERSION:-16}"
CHAT_DB_NAME="${CHAT_DB_NAME:-irado_chat}"
CHAT_DB_FQDN="${POSTGRES_SERVER}.postgres.database.azure.com"
CHATBOT_APP_NAME="${CHATBOT_APP_NAME:-irado-chatbot-app}"
DASHBOARD_APP_NAME="${DASHBOARD_APP_NAME:-irado-dashboard-app}"
STORAGE_ACCOUNT="${STORAGE_ACCOUNT:-iradostorage}"
STORAGE_CONTAINER="${STORAGE_CONTAINER:-backups}"
PROJECT_VERSION="$(tr -d '\r\n' < "${ROOT_DIR}/VERSION.txt")"
SYSTEM_PROMPT_VERSION="${SYSTEM_PROMPT_VERSION:-v${PROJECT_VERSION}}"
IMAGE_SUFFIX="$(date +%Y%m%d-%H%M%S)"
ACR_LOGIN_SERVER="${ACR_NAME}.azurecr.io"
CHATBOT_IMAGE_NAME="chatbot-${IMAGE_SUFFIX}"
DASHBOARD_IMAGE_NAME="dashboard-${IMAGE_SUFFIX}"
BACKUP_DIR="${ROOT_DIR}/backups"
BACKUP_ARCHIVE="${BACKUP_DIR}/irado-seed-${IMAGE_SUFFIX}.tar.gz"
PLAIN_DUMP_FILE="${BACKUP_DIR}/${CHAT_DB_NAME}-${IMAGE_SUFFIX}.sql"
CUSTOM_DUMP_FILE="${BACKUP_DIR}/${CHAT_DB_NAME}-${IMAGE_SUFFIX}.dump"

CHATBOT_PORT="${CHATBOT_PORT:-80}"
DASHBOARD_PORT="${DASHBOARD_PORT:-8000}"

AZURE_OPENAI_API_KEY="${AZURE_OPENAI_API_KEY:-BXFgQF9udVZRqyhvapyyKmaO5MxXH5CUZb2Xf992rD99al4C4zyKJQQJ99BJACfhMk5XJ3w3AAAAACOGL8rA}"
AZURE_OPENAI_ENDPOINT="${AZURE_OPENAI_ENDPOINT:-https://info-mgal213r-swedencentral.cognitiveservices.azure.com}"
AZURE_OPENAI_DEPLOYMENT="${AZURE_OPENAI_DEPLOYMENT:-gpt-4o}"
AZURE_OPENAI_API_VERSION="${AZURE_OPENAI_API_VERSION:-2025-01-01-preview}"
CHAT_BASIC_AUTH_USER="${CHAT_BASIC_AUTH_USER:-irado}"
CHAT_BASIC_AUTH_PASSWORD="${CHAT_BASIC_AUTH_PASSWORD:-20Irado25!}"
APP_TIMEZONE="${APP_TIMEZONE:-Europe/Amsterdam}"

REQUIRED_COMMANDS=("az" "docker" "psql" "pg_dump" "python3" "tar")

require_commands() {
  for cmd in "${REQUIRED_COMMANDS[@]}"; do
    if ! command -v "$cmd" >/dev/null 2>&1; then
      error "Command '${cmd}' is required but not installed."
      exit 1
    fi
  done
  success "All required commands available"
}

ensure_python_modules() {
  if python3 -c "import psycopg2" >/dev/null 2>&1; then
    return
  fi
  log "Installing psycopg2-binary for local database bootstrap"
  if python3 -m pip install --user psycopg2-binary >/dev/null 2>&1; then
    success "psycopg2-binary installed"
  else
    warn "Failed to install psycopg2-binary automatically. Ensure the module is available before rerunning."
  fi
}

check_azure_login() {
  if ! az account show >/dev/null 2>&1; then
    error "Azure CLI not logged in. Run 'az login' before executing this script."
    exit 1
  fi
  success "Azure CLI login detected"
}

ensure_resource_group() {
  log "Ensuring resource group ${RESOURCE_GROUP} in ${LOCATION}"
  az group create --name "$RESOURCE_GROUP" --location "$LOCATION" --tags "project=irado" >/dev/null
  success "Resource group ready"
}

ensure_acr() {
  log "Ensuring Azure Container Registry ${ACR_NAME}"
  if az acr show --name "$ACR_NAME" --resource-group "$RESOURCE_GROUP" >/dev/null 2>&1; then
    success "ACR ${ACR_NAME} already exists"
  else
    az acr create \
      --resource-group "$RESOURCE_GROUP" \
      --name "$ACR_NAME" \
      --sku "$ACR_SKU" \
      --location "$LOCATION" \
      --admin-enabled true >/dev/null
    success "ACR ${ACR_NAME} created"
  fi
}

ensure_storage_account() {
  log "Ensuring storage account ${STORAGE_ACCOUNT}"
  if ! [[ "$STORAGE_ACCOUNT" =~ ^[a-z0-9]{3,24}$ ]]; then
    warn "Storage account name '${STORAGE_ACCOUNT}' is invalid. Set STORAGE_ACCOUNT env var (3-24 lowercase alnum). Skipping storage setup."
    return
  fi

  if az storage account show --name "$STORAGE_ACCOUNT" --resource-group "$RESOURCE_GROUP" >/dev/null 2>&1; then
    success "Storage account ${STORAGE_ACCOUNT} already exists"
  else
    if az storage account create \
      --name "$STORAGE_ACCOUNT" \
      --resource-group "$RESOURCE_GROUP" \
      --location "$LOCATION" \
      --sku Standard_LRS \
      --kind StorageV2 >/dev/null; then
      success "Storage account ${STORAGE_ACCOUNT} created"
    else
      warn "Unable to create storage account ${STORAGE_ACCOUNT} (name may be taken). Backups to Blob Storage will be skipped."
      return
    fi
  fi

  local account_key
  account_key="$(az storage account keys list --resource-group "$RESOURCE_GROUP" --account-name "$STORAGE_ACCOUNT" --query "[0].value" -o tsv)"

  if ! az storage container show --account-name "$STORAGE_ACCOUNT" --name "$STORAGE_CONTAINER" --account-key "$account_key" >/dev/null 2>&1; then
    az storage container create \
      --account-name "$STORAGE_ACCOUNT" \
      --name "$STORAGE_CONTAINER" \
      --public-access off \
      --account-key "$account_key" >/dev/null
    success "Storage container ${STORAGE_CONTAINER} ready"
  else
    success "Storage container ${STORAGE_CONTAINER} already exists"
  fi

  STORAGE_ACCOUNT_KEY="$account_key"
}

ensure_postgres() {
  log "Ensuring Azure Database for PostgreSQL Flexible Server ${POSTGRES_SERVER}"
  if az postgres flexible-server show --resource-group "$RESOURCE_GROUP" --name "$POSTGRES_SERVER" >/dev/null 2>&1; then
    success "PostgreSQL server ${POSTGRES_SERVER} already exists"
  else
    az postgres flexible-server create \
      --resource-group "$RESOURCE_GROUP" \
      --name "$POSTGRES_SERVER" \
      --location "$LOCATION" \
      --admin-user "$POSTGRES_ADMIN_USER" \
      --admin-password "$POSTGRES_ADMIN_PASSWORD" \
      --tier "$POSTGRES_TIER" \
      --sku-name "$POSTGRES_SKU" \
      --storage-size "$POSTGRES_STORAGE_MB" \
      --version "$POSTGRES_VERSION" \
      --public-access all >/dev/null
    success "PostgreSQL server ${POSTGRES_SERVER} created"
  fi

  if ! az postgres flexible-server firewall-rule show \
    --resource-group "$RESOURCE_GROUP" \
    --name "$POSTGRES_SERVER" \
    --rule-name allow-azure >/dev/null 2>&1; then
    az postgres flexible-server firewall-rule create \
      --resource-group "$RESOURCE_GROUP" \
      --name "$POSTGRES_SERVER" \
      --rule-name allow-azure \
      --start-ip-address 0.0.0.0 \
      --end-ip-address 0.0.0.0 >/dev/null
    success "Firewall rule allow-azure enabled"
  fi

  local my_ip
  my_ip="$(curl -s https://ifconfig.me || true)"
  if [[ -n "$my_ip" && "$my_ip" =~ ^[0-9]+\.[0-9]+\.[0-9]+\.[0-9]+$ ]]; then
    if ! az postgres flexible-server firewall-rule show \
      --resource-group "$RESOURCE_GROUP" \
      --name "$POSTGRES_SERVER" \
      --rule-name allow-client-ip >/dev/null 2>&1; then
      az postgres flexible-server firewall-rule create \
        --resource-group "$RESOURCE_GROUP" \
        --name "$POSTGRES_SERVER" \
        --rule-name allow-client-ip \
        --start-ip-address "$my_ip" \
        --end-ip-address "$my_ip" >/dev/null
      success "Firewall rule for current IP (${my_ip}) created"
    fi
  else
    warn "Could not determine public IP for firewall rule. Ensure your IP can reach ${CHAT_DB_FQDN}."
  fi

  az postgres flexible-server db create \
    --resource-group "$RESOURCE_GROUP" \
    --server-name "$POSTGRES_SERVER" \
    --database-name "$CHAT_DB_NAME" >/dev/null 2>&1 || true
  success "Database ${CHAT_DB_NAME} ensured"
}

wait_for_postgres() {
  log "Waiting for PostgreSQL ${CHAT_DB_FQDN} to accept connections"
  export PGHOST="$CHAT_DB_FQDN"
  export PGUSER="$POSTGRES_ADMIN_USER"
  export PGPORT=5432
  export PGDATABASE="$CHAT_DB_NAME"
  export PGPASSWORD="$POSTGRES_ADMIN_PASSWORD"
  export PGSSLMODE=require

  local attempts=0
  local max_attempts=18
  until psql -c "SELECT 1;" >/dev/null 2>&1; do
    ((attempts++))
    if (( attempts >= max_attempts )); then
      error "Unable to connect to PostgreSQL after multiple attempts."
      exit 1
    fi
    sleep 10
  done
  success "PostgreSQL connection succeeded"
}

bootstrap_database() {
  log "Creating core database schema"
  psql -v ON_ERROR_STOP=1 <<'SQL'
CREATE TABLE IF NOT EXISTS chat_sessions (
  id SERIAL PRIMARY KEY,
  session_id VARCHAR(255) UNIQUE NOT NULL,
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  last_activity TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS chat_messages (
  id SERIAL PRIMARY KEY,
  session_id VARCHAR(255) NOT NULL,
  message_type VARCHAR(20) NOT NULL,
  content TEXT NOT NULL,
  timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  metadata JSONB
);

CREATE INDEX IF NOT EXISTS idx_chat_messages_session_id ON chat_messages(session_id);
CREATE INDEX IF NOT EXISTS idx_chat_sessions_session_id ON chat_sessions(session_id);

CREATE TABLE IF NOT EXISTS chat_memory (
  id SERIAL PRIMARY KEY,
  session_id VARCHAR(255) NOT NULL,
  memory_type VARCHAR(50) NOT NULL,
  content TEXT NOT NULL,
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_chat_memory_session_id ON chat_memory(session_id);

CREATE TABLE IF NOT EXISTS "bedrijfsklanten" (
  "KOAD-nummer" VARCHAR(255),
  "KOAD-str" VARCHAR(255),
  "KOAD-pc" VARCHAR(10),
  "KOAD-huisaand" VARCHAR(50),
  "KOAD-huisnr" VARCHAR(20),
  "KOAD-etage" VARCHAR(50),
  "KOAD-naam" VARCHAR(255),
  "KOAD-actief" VARCHAR(1) DEFAULT '1',
  "KOAD-inwoner" VARCHAR(1) DEFAULT '1'
);

CREATE INDEX IF NOT EXISTS idx_bedrijfsklanten_lookup
  ON bedrijfsklanten ("KOAD-pc", "KOAD-huisnr");

CREATE TABLE IF NOT EXISTS csv_uploads (
  id SERIAL PRIMARY KEY,
  filename VARCHAR(255) NOT NULL,
  upload_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  records_imported INTEGER DEFAULT 0,
  records_updated INTEGER DEFAULT 0,
  records_deleted INTEGER DEFAULT 0,
  status VARCHAR(50) DEFAULT 'completed',
  error_message TEXT
);

CREATE TABLE IF NOT EXISTS dashboard_logs (
  id SERIAL PRIMARY KEY,
  timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  log_type VARCHAR(50),
  action VARCHAR(100),
  message TEXT,
  details JSONB,
  level VARCHAR(20) DEFAULT 'info',
  user_ip VARCHAR(50),
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_dashboard_logs_timestamp
  ON dashboard_logs(timestamp DESC);
CREATE INDEX IF NOT EXISTS idx_dashboard_logs_type
  ON dashboard_logs(log_type);

CREATE TABLE IF NOT EXISTS system_prompts (
  id SERIAL PRIMARY KEY,
  version VARCHAR(50) NOT NULL UNIQUE,
  content TEXT NOT NULL,
  is_active BOOLEAN DEFAULT FALSE,
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  created_by VARCHAR(255) DEFAULT 'admin',
  notes TEXT
);

CREATE UNIQUE INDEX IF NOT EXISTS idx_system_prompts_active
  ON system_prompts(is_active) WHERE is_active = TRUE;

CREATE INDEX IF NOT EXISTS idx_system_prompts_version
  ON system_prompts(version);

CREATE TABLE IF NOT EXISTS system_prompt_state (
  key TEXT PRIMARY KEY,
  prompt_id INTEGER REFERENCES system_prompts(id) ON DELETE SET NULL,
  updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

INSERT INTO system_prompt_state (key, prompt_id)
VALUES ('active_prompt_id', NULL)
ON CONFLICT (key) DO NOTHING;
SQL
  success "Database schema ensured"

  log "Importing KOAD dataset"
  psql -v ON_ERROR_STOP=1 -c 'TRUNCATE TABLE bedrijfsklanten;'
  psql -v ON_ERROR_STOP=1 -c "\copy bedrijfsklanten (\"KOAD-nummer\",\"KOAD-str\",\"KOAD-pc\",\"KOAD-huisaand\",\"KOAD-huisnr\",\"KOAD-etage\",\"KOAD-naam\",\"KOAD-actief\",\"KOAD-inwoner\") FROM '${ROOT_DIR}/chatbot/koad.csv' WITH CSV HEADER;"
  local count
  count="$(psql -t -c 'SELECT COUNT(*) FROM bedrijfsklanten;' | tr -d '[:space:]')"
  success "KOAD import complete (${count} rows)"

  log "Seeding system prompt version ${SYSTEM_PROMPT_VERSION}"
  SYSTEM_PROMPT_VERSION="$SYSTEM_PROMPT_VERSION" \
  python3 <<'PY'
import os
import psycopg2
from pathlib import Path

host = os.environ["PGHOST"]
port = int(os.environ["PGPORT"])
dbname = os.environ["PGDATABASE"]
user = os.environ["PGUSER"]
password = os.environ["PGPASSWORD"]
sslmode = os.environ.get("PGSSLMODE", "require")
version = os.environ["SYSTEM_PROMPT_VERSION"]

prompt_path = Path(os.environ["ROOT_DIR"]) / "chatbot" / "prompts" / "system_prompt.txt"
content = prompt_path.read_text(encoding="utf-8").strip()

conn = psycopg2.connect(host=host, port=port, dbname=dbname, user=user, password=password, sslmode=sslmode)
cur = conn.cursor()
cur.execute("""
    INSERT INTO system_prompts (version, content, is_active, created_by, notes)
    VALUES (%s, %s, TRUE, %s, %s)
    ON CONFLICT (version) DO UPDATE
      SET content = EXCLUDED.content,
          is_active = TRUE,
          updated_at = CURRENT_TIMESTAMP,
          notes = EXCLUDED.notes
""", (version, content, "mainfact-deploy", "Seeded by mainfact-azure-deploy.sh"))
cur.execute("""
    INSERT INTO system_prompt_state (key, prompt_id, updated_at)
    SELECT 'active_prompt_id', id, CURRENT_TIMESTAMP
    FROM system_prompts
    WHERE version = %s
    ON CONFLICT (key) DO UPDATE
      SET prompt_id = EXCLUDED.prompt_id,
          updated_at = EXCLUDED.updated_at
""", (version,))
conn.commit()
cur.close()
conn.close()
print(f"Seeded system prompt version {version}")
PY
  success "System prompt seeded"
}

dump_database() {
  log "Creating PostgreSQL dumps"
  mkdir -p "$BACKUP_DIR"

  if PGPASSWORD="$POSTGRES_ADMIN_PASSWORD" PGSSLMODE=require pg_dump \
      --no-owner \
      --no-password \
      --format=p \
      --host="$CHAT_DB_FQDN" \
      --port=5432 \
      --username="$POSTGRES_ADMIN_USER" \
      --dbname="$CHAT_DB_NAME" \
      --file="$PLAIN_DUMP_FILE" >/dev/null 2>&1; then
    success "Plain SQL dump created at ${PLAIN_DUMP_FILE}"
  else
    warn "Failed to create plain SQL dump at ${PLAIN_DUMP_FILE}"
    rm -f "$PLAIN_DUMP_FILE" >/dev/null 2>&1 || true
  fi

  if PGPASSWORD="$POSTGRES_ADMIN_PASSWORD" PGSSLMODE=require pg_dump \
      --no-owner \
      --no-password \
      --format=c \
      --host="$CHAT_DB_FQDN" \
      --port=5432 \
      --username="$POSTGRES_ADMIN_USER" \
      --dbname="$CHAT_DB_NAME" \
      --file="$CUSTOM_DUMP_FILE" >/dev/null 2>&1; then
    success "Custom-format dump created at ${CUSTOM_DUMP_FILE}"
  else
    warn "Failed to create custom dump at ${CUSTOM_DUMP_FILE}"
    rm -f "$CUSTOM_DUMP_FILE" >/dev/null 2>&1 || true
  fi
}

build_and_push_images() {
  log "Building chatbot image ${CHATBOT_IMAGE_NAME}"
  docker build \
    --pull \
    --no-cache \
    -f "${ROOT_DIR}/Dockerfile.chatbot" \
    -t "${ACR_LOGIN_SERVER}/${CHATBOT_IMAGE_NAME}:latest" \
    "$ROOT_DIR"

  log "Building dashboard image ${DASHBOARD_IMAGE_NAME}"
  docker build \
    --pull \
    --no-cache \
    -f "${ROOT_DIR}/chatbot/Dockerfile.dashboard" \
    -t "${ACR_LOGIN_SERVER}/${DASHBOARD_IMAGE_NAME}:latest" \
    "${ROOT_DIR}/chatbot"

  log "Logging in to ACR ${ACR_NAME}"
  az acr login --name "$ACR_NAME" >/dev/null

  docker tag "${ACR_LOGIN_SERVER}/${CHATBOT_IMAGE_NAME}:latest" "${ACR_LOGIN_SERVER}/${CHATBOT_IMAGE_NAME}:${IMAGE_SUFFIX}"
  docker tag "${ACR_LOGIN_SERVER}/${DASHBOARD_IMAGE_NAME}:latest" "${ACR_LOGIN_SERVER}/${DASHBOARD_IMAGE_NAME}:${IMAGE_SUFFIX}"

  log "Pushing chatbot images to ACR"
  docker push "${ACR_LOGIN_SERVER}/${CHATBOT_IMAGE_NAME}:${IMAGE_SUFFIX}"
  docker push "${ACR_LOGIN_SERVER}/${CHATBOT_IMAGE_NAME}:latest"

  log "Pushing dashboard images to ACR"
  docker push "${ACR_LOGIN_SERVER}/${DASHBOARD_IMAGE_NAME}:${IMAGE_SUFFIX}"
  docker push "${ACR_LOGIN_SERVER}/${DASHBOARD_IMAGE_NAME}:latest"

  success "Images pushed to ACR"
}

ensure_app_service_plan() {
  log "Ensuring App Service plan ${APP_SERVICE_PLAN}"
  if az appservice plan show --name "$APP_SERVICE_PLAN" --resource-group "$RESOURCE_GROUP" >/dev/null 2>&1; then
    success "App Service plan already exists"
  else
    az appservice plan create \
      --name "$APP_SERVICE_PLAN" \
      --resource-group "$RESOURCE_GROUP" \
      --location "$LOCATION" \
      --is-linux \
      --sku B1 >/dev/null
    success "App Service plan created"
  fi
}

acr_credentials() {
  ACR_USERNAME="$(az acr credential show --name "$ACR_NAME" --query username -o tsv)"
  ACR_PASSWORD="$(az acr credential show --name "$ACR_NAME" --query passwords[0].value -o tsv)"
}

deploy_webapp() {
  local app_name="$1"
  local image_name="$2"
  local port="$3"

  log "Deploying Web App ${app_name}"
  if az webapp show --name "$app_name" --resource-group "$RESOURCE_GROUP" >/dev/null 2>&1; then
    az webapp config container set \
      --name "$app_name" \
      --resource-group "$RESOURCE_GROUP" \
      --container-image-name "${ACR_LOGIN_SERVER}/${image_name}:${IMAGE_SUFFIX}" \
      --container-registry-url "https://${ACR_LOGIN_SERVER}" \
      --container-registry-user "$ACR_USERNAME" \
      --container-registry-password "$ACR_PASSWORD" >/dev/null
    success "Updated container image for ${app_name}"
  else
    az webapp create \
      --name "$app_name" \
      --resource-group "$RESOURCE_GROUP" \
      --plan "$APP_SERVICE_PLAN" \
      --deployment-container-image-name "${ACR_LOGIN_SERVER}/${image_name}:${IMAGE_SUFFIX}" >/dev/null
    az webapp config container set \
      --name "$app_name" \
      --resource-group "$RESOURCE_GROUP" \
      --container-registry-url "https://${ACR_LOGIN_SERVER}" \
      --container-registry-user "$ACR_USERNAME" \
      --container-registry-password "$ACR_PASSWORD" >/dev/null
    success "Created Web App ${app_name}"
  fi

  az webapp config appsettings set \
    --name "$app_name" \
    --resource-group "$RESOURCE_GROUP" \
    --settings \
      POSTGRES_HOST="$CHAT_DB_FQDN" \
      POSTGRES_PORT="5432" \
      POSTGRES_DB="$CHAT_DB_NAME" \
      POSTGRES_USER="$POSTGRES_ADMIN_USER" \
      POSTGRES_PASSWORD="$POSTGRES_ADMIN_PASSWORD" \
      POSTGRES_SSLMODE="require" \
      APP_TIMEZONE="$APP_TIMEZONE" \
      TZ="$APP_TIMEZONE" \
      AZURE_OPENAI_API_KEY="$AZURE_OPENAI_API_KEY" \
      AZURE_OPENAI_ENDPOINT="$AZURE_OPENAI_ENDPOINT" \
      AZURE_OPENAI_DEPLOYMENT="$AZURE_OPENAI_DEPLOYMENT" \
      AZURE_OPENAI_API_VERSION="$AZURE_OPENAI_API_VERSION" \
      CHAT_BASIC_AUTH_USER="$CHAT_BASIC_AUTH_USER" \
      CHAT_BASIC_AUTH_PASSWORD="$CHAT_BASIC_AUTH_PASSWORD" \
      BEDRIJFSKLANTEN_DB_HOST="$CHAT_DB_FQDN" \
      BEDRIJFSKLANTEN_DB_PORT="5432" \
      BEDRIJFSKLANTEN_DB_NAME="$CHAT_DB_NAME" \
      BEDRIJFSKLANTEN_DB_USER="$POSTGRES_ADMIN_USER" \
      BEDRIJFSKLANTEN_DB_PASSWORD="$POSTGRES_ADMIN_PASSWORD" \
      WEBSITES_PORT="$port" \
      SCM_DO_BUILD_DURING_DEPLOYMENT="false" \
      WEBSITES_ENABLE_APP_SERVICE_STORAGE="false" >/dev/null
  success "App settings applied to ${app_name}"
}

restart_webapp() {
  local app_name="$1"
  log "Restarting Web App ${app_name}"
  az webapp restart --name "$app_name" --resource-group "$RESOURCE_GROUP" >/dev/null
  success "${app_name} restarted"
}

create_backup_archive() {
  log "Creating seed backup archive"
  mkdir -p "$BACKUP_DIR"
  [[ -f "$BACKUP_ARCHIVE" ]] && rm -f "$BACKUP_ARCHIVE"

  local -a tar_args=(
    "-C" "$ROOT_DIR"
    "VERSION.txt"
    "chatbot/prompts/system_prompt.txt"
    "chatbot/koad.csv"
    "data"
  )

  if [[ -f "$PLAIN_DUMP_FILE" ]]; then
    tar_args+=("-C" "$BACKUP_DIR" "$(basename "$PLAIN_DUMP_FILE")")
  fi
  if [[ -f "$CUSTOM_DUMP_FILE" ]]; then
    tar_args+=("-C" "$BACKUP_DIR" "$(basename "$CUSTOM_DUMP_FILE")")
  fi

  if tar -czf "$BACKUP_ARCHIVE" "${tar_args[@]}" >/dev/null 2>&1; then
    success "Backup archive created at ${BACKUP_ARCHIVE}"
  else
    warn "Failed to create backup archive at ${BACKUP_ARCHIVE}"
    return
  fi

  if [[ -n "${STORAGE_ACCOUNT_KEY:-}" ]]; then
    log "Uploading backup to Azure Storage"
    az storage blob upload \
      --account-name "$STORAGE_ACCOUNT" \
      --account-key "$STORAGE_ACCOUNT_KEY" \
      --container-name "$STORAGE_CONTAINER" \
      --name "$(basename "$BACKUP_ARCHIVE")" \
      --file "$BACKUP_ARCHIVE" \
      --overwrite true >/dev/null
    success "Backup uploaded to https://${STORAGE_ACCOUNT}.blob.core.windows.net/${STORAGE_CONTAINER}/$(basename "$BACKUP_ARCHIVE")"
  else
    warn "Skipping blob upload (storage account not configured)"
  fi
}

main() {
  log "Starting full Azure deployment for Irado (version ${PROJECT_VERSION})"
  require_commands
  ensure_python_modules
  check_azure_login
  ensure_resource_group
  ensure_acr
  ensure_storage_account
  ensure_postgres
  wait_for_postgres
  bootstrap_database
  dump_database
  build_and_push_images
  ensure_app_service_plan
  acr_credentials
  deploy_webapp "$CHATBOT_APP_NAME" "$CHATBOT_IMAGE_NAME" "$CHATBOT_PORT"
  deploy_webapp "$DASHBOARD_APP_NAME" "$DASHBOARD_IMAGE_NAME" "$DASHBOARD_PORT"
  restart_webapp "$CHATBOT_APP_NAME"
  restart_webapp "$DASHBOARD_APP_NAME"
  create_backup_archive

  success "Azure deployment completed"
  cat <<EOF

Next steps:
1. Verify chatbot: curl https://${CHATBOT_APP_NAME}.azurewebsites.net/health
2. Verify dashboard: open https://${DASHBOARD_APP_NAME}.azurewebsites.net
3. Update DNS records if custom domains are used
4. Review Azure portal for resource status in resource group ${RESOURCE_GROUP}

EOF
}

export ROOT_DIR
main "$@"
