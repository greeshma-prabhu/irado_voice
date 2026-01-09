#!/usr/bin/env bash
set -euo pipefail

# Export Azure App Service application settings to a local .env file (NOT for git).
#
# Usage:
#   ./scripts/azure-appsettings-export.sh --name irado-chatbot-app --rg irado-rg --out .env.prod.local
#

NAME=""
RG=""
OUT=""

while [[ $# -gt 0 ]]; do
  case "$1" in
    --name) NAME="$2"; shift 2;;
    --rg) RG="$2"; shift 2;;
    --out) OUT="$2"; shift 2;;
    *) echo "Unknown arg: $1" >&2; exit 2;;
  esac
done

if [[ -z "${NAME}" || -z "${RG}" || -z "${OUT}" ]]; then
  echo "Usage: $0 --name <webapp> --rg <resource-group> --out <file>" >&2
  exit 2
fi

if ! az account show >/dev/null 2>&1; then
  echo "Azure CLI not logged in. Run: az login" >&2
  exit 1
fi

tmp="$(mktemp)"
trap 'rm -f "$tmp"' EXIT

az webapp config appsettings list \
  --name "$NAME" \
  --resource-group "$RG" \
  --query "[].{name:name,value:value}" \
  -o tsv > "$tmp"

{
  echo "# Exported from Azure App Settings"
  echo "# webapp: ${NAME}"
  echo "# resource_group: ${RG}"
  echo "# exported_at: $(date -u '+%Y-%m-%dT%H:%M:%SZ')"
  echo ""
  while IFS=$'\t' read -r key val; do
    [[ -z "$key" ]] && continue
    # Write as KEY="VALUE" with basic escaping.
    esc="${val//\\/\\\\}"
    esc="${esc//\"/\\\"}"
    echo "${key}=\"${esc}\""
  done < "$tmp"
} > "$OUT"

echo "Wrote: $OUT"

