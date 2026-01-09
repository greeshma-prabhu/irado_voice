#!/usr/bin/env bash
set -euo pipefail

# Import a local .env file into Azure App Service application settings.
#
# Usage:
#   ./scripts/azure-appsettings-import.sh --name irado-chatbot-app --rg irado-rg --file .env.prod.local
#
# Notes:
# - This will overwrite settings with the values from the file.
# - Keep your .env.*.local files OUT of git.
#

NAME=""
RG=""
FILE=""

while [[ $# -gt 0 ]]; do
  case "$1" in
    --name) NAME="$2"; shift 2;;
    --rg) RG="$2"; shift 2;;
    --file) FILE="$2"; shift 2;;
    *) echo "Unknown arg: $1" >&2; exit 2;;
  esac
done

if [[ -z "${NAME}" || -z "${RG}" || -z "${FILE}" ]]; then
  echo "Usage: $0 --name <webapp> --rg <resource-group> --file <env-file>" >&2
  exit 2
fi

if [[ ! -f "$FILE" ]]; then
  echo "File not found: $FILE" >&2
  exit 1
fi

if ! az account show >/dev/null 2>&1; then
  echo "Azure CLI not logged in. Run: az login" >&2
  exit 1
fi

# Read KEY=VALUE lines (supports quoted values), ignore comments/empties.
settings=()
while IFS= read -r line || [[ -n "$line" ]]; do
  [[ -z "$line" ]] && continue
  [[ "$line" =~ ^[[:space:]]*# ]] && continue
  if [[ "$line" =~ ^([A-Za-z_][A-Za-z0-9_]*)=(.*)$ ]]; then
    key="${BASH_REMATCH[1]}"
    val="${BASH_REMATCH[2]}"
    # Strip optional surrounding quotes
    if [[ "$val" =~ ^\"(.*)\"$ ]]; then
      val="${BASH_REMATCH[1]}"
      val="${val//\\\"/\"}"
      val="${val//\\\\/\\}"
    fi
    settings+=("${key}=${val}")
  fi
done < "$FILE"

if [[ ${#settings[@]} -eq 0 ]]; then
  echo "No settings found in $FILE" >&2
  exit 1
fi

az webapp config appsettings set \
  --name "$NAME" \
  --resource-group "$RG" \
  --settings "${settings[@]}" \
  --output none

echo "Imported ${#settings[@]} settings into ${NAME} (${RG})"

