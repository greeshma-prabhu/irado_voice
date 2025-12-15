#!/usr/bin/env bash
set -euo pipefail

# Mainfact Azure backup script
# Creates PostgreSQL dumps and packages critical seed files for safe storage.

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

# Configurable settings (override via environment variables)
RESOURCE_GROUP="${RESOURCE_GROUP:-irado-rg}"
LOCATION="${LOCATION:-westeurope}"
POSTGRES_SERVER="${POSTGRES_SERVER:-irado-chat-db}"
POSTGRES_ADMIN_USER="${POSTGRES_ADMIN_USER:-irado_admin}"
POSTGRES_ADMIN_PASSWORD="${POSTGRES_ADMIN_PASSWORD:-lqBp6OF31+wCNXzyTMvasFrspdtL+IWPGVtooy2zjS4=}"
CHAT_DB_NAME="${CHAT_DB_NAME:-irado_chat}"
CHAT_DB_FQDN="${CHAT_DB_FQDN:-${POSTGRES_SERVER}.postgres.database.azure.com}"
BACKUP_DIR="${BACKUP_DIR:-${ROOT_DIR}/backups}"
TIMESTAMP="$(date +%Y%m%d-%H%M%S)"
PLAIN_DUMP_FILE="${BACKUP_DIR}/${CHAT_DB_NAME}-${TIMESTAMP}.sql"
CUSTOM_DUMP_FILE="${BACKUP_DIR}/${CHAT_DB_NAME}-${TIMESTAMP}.dump"
BACKUP_ARCHIVE="${BACKUP_DIR}/irado-backup-${TIMESTAMP}.tar.gz"
STORAGE_ACCOUNT="${STORAGE_ACCOUNT:-}"
STORAGE_CONTAINER="${STORAGE_CONTAINER:-backups}"
APP_TIMEZONE="${APP_TIMEZONE:-Europe/Amsterdam}"

REQUIRED_COMMANDS=("az" "pg_dump" "psql" "tar" "curl")
FIREWALL_RULE_NAME=""

cleanup() {
  if [[ -n "$FIREWALL_RULE_NAME" ]]; then
    log "Removing temporary firewall rule ${FIREWALL_RULE_NAME}"
    az postgres flexible-server firewall-rule delete \
      --resource-group "$RESOURCE_GROUP" \
      --name "$POSTGRES_SERVER" \
      --rule-name "$FIREWALL_RULE_NAME" >/dev/null 2>&1 || warn "Could not delete firewall rule ${FIREWALL_RULE_NAME}"
    FIREWALL_RULE_NAME=""
  fi
}
trap cleanup EXIT

require_commands() {
  for cmd in "${REQUIRED_COMMANDS[@]}"; do
    if ! command -v "$cmd" >/dev/null 2>&1; then
      error "Command '${cmd}' is required but not installed."
      exit 1
    fi
  done
  success "All required commands available"
}

check_azure_login() {
  if ! az account show >/dev/null 2>&1; then
    error "Azure CLI not logged in. Run 'az login' before executing this script."
    exit 1
  fi
  success "Azure CLI login detected"
}

verify_postgres_server() {
  if ! az postgres flexible-server show --resource-group "$RESOURCE_GROUP" --name "$POSTGRES_SERVER" >/dev/null 2>&1; then
    error "PostgreSQL server ${POSTGRES_SERVER} not found in resource group ${RESOURCE_GROUP}"
    exit 1
  fi
  success "PostgreSQL server ${POSTGRES_SERVER} exists"
}

allow_current_ip() {
  local ip
  ip="$(curl -s https://ifconfig.me || true)"
  if [[ -z "$ip" || ! "$ip" =~ ^[0-9]+\.[0-9]+\.[0-9]+\.[0-9]+$ ]]; then
    warn "Unable to detect public IP address. Ensure your IP already has database access."
    return
  fi

  FIREWALL_RULE_NAME="mainfact-backup-${TIMESTAMP}"
  if az postgres flexible-server firewall-rule create \
      --resource-group "$RESOURCE_GROUP" \
      --name "$POSTGRES_SERVER" \
      --rule-name "$FIREWALL_RULE_NAME" \
      --start-ip-address "$ip" \
      --end-ip-address "$ip" >/dev/null 2>&1; then
    success "Temporary firewall rule ${FIREWALL_RULE_NAME} added for ${ip}"
  else
    warn "Failed to create firewall rule for ${ip}. Continuing without temporary rule."
    FIREWALL_RULE_NAME=""
  fi
}

test_database_connection() {
  log "Testing PostgreSQL connection to ${CHAT_DB_FQDN}"
  PGPASSWORD="$POSTGRES_ADMIN_PASSWORD" PGSSLMODE=require \
    psql --host "$CHAT_DB_FQDN" --port 5432 --username "$POSTGRES_ADMIN_USER" --dbname "$CHAT_DB_NAME" \
      -v ON_ERROR_STOP=1 -c "SELECT NOW() AT TIME ZONE '${APP_TIMEZONE}' AS backup_time;" >/dev/null
  success "Database connection successful"
}

dump_database() {
  log "Creating PostgreSQL dumps in ${BACKUP_DIR}"
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

create_archive() {
  log "Packaging backup archive ${BACKUP_ARCHIVE}"
  [[ -f "$BACKUP_ARCHIVE" ]] && rm -f "$BACKUP_ARCHIVE"

  local -a tar_args=()

  if [[ -f "$ROOT_DIR/VERSION.txt" ]]; then
    tar_args+=("-C" "$ROOT_DIR" "VERSION.txt")
  else
    warn "VERSION.txt not found; skipping"
  fi

  if [[ -f "$ROOT_DIR/chatbot/prompts/system_prompt.txt" ]]; then
    tar_args+=("-C" "$ROOT_DIR" "chatbot/prompts/system_prompt.txt")
  else
    warn "System prompt file not found; skipping"
  fi

  if [[ -f "$ROOT_DIR/chatbot/koad.csv" ]]; then
    tar_args+=("-C" "$ROOT_DIR" "chatbot/koad.csv")
  else
    warn "KOAD CSV not found; skipping"
  fi

  if [[ -d "$ROOT_DIR/data" ]]; then
    tar_args+=("-C" "$ROOT_DIR" "data")
  else
    warn "Data directory not found; skipping"
  fi

  if [[ -f "$PLAIN_DUMP_FILE" ]]; then
    tar_args+=("-C" "$BACKUP_DIR" "$(basename "$PLAIN_DUMP_FILE")")
  fi
  if [[ -f "$CUSTOM_DUMP_FILE" ]]; then
    tar_args+=("-C" "$BACKUP_DIR" "$(basename "$CUSTOM_DUMP_FILE")")
  fi

  if [[ ${#tar_args[@]} -eq 0 ]]; then
    warn "No files to include in archive; skipping tar creation"
    BACKUP_ARCHIVE=""
    return
  fi

  if tar -czf "$BACKUP_ARCHIVE" "${tar_args[@]}" >/dev/null 2>&1; then
    success "Backup archive created at ${BACKUP_ARCHIVE}"
  else
    warn "Failed to create backup archive at ${BACKUP_ARCHIVE}"
    BACKUP_ARCHIVE=""
  fi
}

upload_backup() {
  if [[ -z "$STORAGE_ACCOUNT" || -z "$BACKUP_ARCHIVE" ]]; then
    warn "Skipping blob upload (storage account not configured)"
    return
  fi

  log "Uploading backup archive to Azure Storage (${STORAGE_ACCOUNT}/${STORAGE_CONTAINER})"
  local account_key
  account_key="$(az storage account keys list \
    --resource-group "$RESOURCE_GROUP" \
    --account-name "$STORAGE_ACCOUNT" \
    --query "[0].value" -o tsv 2>/dev/null || true)"

  if [[ -z "$account_key" ]]; then
    warn "Unable to retrieve storage account key for ${STORAGE_ACCOUNT}. Upload skipped."
    return
  fi

  az storage container create \
    --account-name "$STORAGE_ACCOUNT" \
    --account-key "$account_key" \
    --name "$STORAGE_CONTAINER" \
    --public-access off >/dev/null 2>&1 || true

  if az storage blob upload \
      --account-name "$STORAGE_ACCOUNT" \
      --account-key "$account_key" \
      --container-name "$STORAGE_CONTAINER" \
      --name "$(basename "$BACKUP_ARCHIVE")" \
      --file "$BACKUP_ARCHIVE" \
      --overwrite true >/dev/null; then
    success "Backup uploaded to https://${STORAGE_ACCOUNT}.blob.core.windows.net/${STORAGE_CONTAINER}/$(basename "$BACKUP_ARCHIVE")"
  else
    warn "Failed to upload ${BACKUP_ARCHIVE} to Azure Storage"
  fi
}

summarize() {
  echo ""
  success "Backup completed"
  echo ""
  echo "Artifacts:"
  [[ -f "$PLAIN_DUMP_FILE" ]] && echo "  - Plain dump : $PLAIN_DUMP_FILE"
  [[ -f "$CUSTOM_DUMP_FILE" ]] && echo "  - Custom dump: $CUSTOM_DUMP_FILE"
  [[ -n "$BACKUP_ARCHIVE" && -f "$BACKUP_ARCHIVE" ]] && echo "  - Archive    : $BACKUP_ARCHIVE"
  echo ""
  echo "Next steps:"
  echo "  1. Store the files in your secure archive (if not already uploaded)."
  echo "  2. Delete the temporary firewall rule if it was not removed automatically."
  echo "  3. Proceed to decommission Azure resources once backups are verified."
}

main() {
  log "Starting Azure backup for database ${CHAT_DB_NAME}"
  require_commands
  check_azure_login
  verify_postgres_server
  allow_current_ip
  test_database_connection
  dump_database
  create_archive
  upload_backup
  summarize
}

main "$@"
