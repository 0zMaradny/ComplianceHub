#!/usr/bin/env bash
set -e

BOLD='\033[1m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
CYAN='\033[0;36m'
RED='\033[0;31m'
NC='\033[0m'

echo ""
echo -e "${BOLD}${GREEN}╔══════════════════════════════════════════════════╗${NC}"
echo -e "${BOLD}${GREEN}║     ComplianceHub — Quick API Test              ║${NC}"
echo -e "${BOLD}${GREEN}║     Generate 8 audit documents from your files   ║${NC}"
echo -e "${BOLD}${GREEN}╚══════════════════════════════════════════════════╝${NC}"
echo ""

# ── Check backend is running ──────────────────────────────────────────────
if ! curl -s http://localhost:8000/api/standards > /dev/null 2>&1; then
  echo -e "${RED}Backend is not running. Start it first:${NC}"
  echo -e "  bash run.sh"
  echo ""
  exit 1
fi
echo -e "${GREEN}✓ Backend detected on http://localhost:8000${NC}"
echo ""

# ── Get inputs ────────────────────────────────────────────────────────────
read -p "$(echo -e "${BOLD}Enter path to audit notes (.docx or .txt): ${NC}")" NOTES_PATH
if [ ! -f "$NOTES_PATH" ]; then
  echo -e "${RED}File not found: $NOTES_PATH${NC}"
  exit 1
fi

read -p "$(echo -e "${BOLD}Enter path to Manday calculation (.docx): ${NC}")" MANDAY_PATH
if [ ! -f "$MANDAY_PATH" ]; then
  echo -e "${RED}File not found: $MANDAY_PATH${NC}"
  exit 1
fi

read -p "$(echo -e "${BOLD}Enter your API key (Gemini/OpenAI/Claude): ${NC}")" API_KEY
if [ -z "$API_KEY" ]; then
  echo -e "${RED}API key is required${NC}"
  exit 1
fi

read -p "$(echo -e "${BOLD}Enter ISO standard (e.g. iso_9001, iso_27001, iso_14001) [iso_9001]: ${NC}")" STANDARD
STANDARD=${STANDARD:-iso_9001}

echo ""
echo -e "${YELLOW}Uploading files and starting document generation...${NC}"
echo ""

# ── Upload and generate ───────────────────────────────────────────────────
UPLOAD=$(curl -s -X POST http://localhost:8000/api/upload \
  -F "audit_notes=@$NOTES_PATH" \
  -F "manday=@$MANDAY_PATH" \
  -F "api_key=$API_KEY" \
  -F "standards=[\"$STANDARD\"]")

JOB_ID=$(echo "$UPLOAD" | python3 -c "import sys,json; print(json.load(sys.stdin).get('job_id',''))" 2>/dev/null)

if [ -z "$JOB_ID" ]; then
  echo -e "${RED}Upload failed. Response:${NC}"
  echo "$UPLOAD"
  exit 1
fi

echo -e "  ${GREEN}✓ Upload successful${NC}"
echo -e "  Job ID: $JOB_ID"
echo ""

# ── Poll until complete ───────────────────────────────────────────────────
echo -e "${YELLOW}Generating 8 documents (this may take a few minutes)...${NC}"
echo ""

while true; do
  STATUS=$(curl -s http://localhost:8000/api/status/$JOB_ID)
  PROGRESS=$(echo "$STATUS" | python3 -c "import sys,json; print(json.load(sys.stdin).get('progress',0))" 2>/dev/null)
  CURRENT=$(echo "$STATUS" | python3 -c "import sys,json; print(json.load(sys.stdin).get('current_doc','...'))" 2>/dev/null)

  # Show progress bar
  BAR_LEN=30
  FILL=$((PROGRESS * BAR_LEN / 100))
  EMPTY=$((BAR_LEN - FILL))
  BAR=$(printf "%-${FILL}s" "█" | tr ' ' '█')
  GAP=$(printf "%-${EMPTY}s" "")
  echo -ne "\r  [${BAR}${GAP}] ${PROGRESS}%  ${CURRENT:0:50}            "

  STATE=$(echo "$STATUS" | python3 -c "import sys,json; print(json.load(sys.stdin).get('status',''))" 2>/dev/null)
  if [ "$STATE" = "done" ]; then
    echo ""
    echo ""
    echo -e "${GREEN}✓ All documents generated!${NC}"
    break
  fi
  if [ "$STATE" = "error" ]; then
    echo ""
    echo ""
    echo -e "${RED}Generation failed.${NC}"
    echo "$STATUS"
    exit 1
  fi
  sleep 2
done

# ── Download ──────────────────────────────────────────────────────────────
OUTPUT_FILE="ComplianceHub_Audit_Package_$(date +%Y%m%d_%H%M%S).zip"
echo ""
echo -e "${YELLOW}Downloading package...${NC}"
curl -s -o "$OUTPUT_FILE" http://localhost:8000/api/download/$JOB_ID

if [ -f "$OUTPUT_FILE" ]; then
  SIZE=$(du -h "$OUTPUT_FILE" | cut -f1)
  echo -e "  ${GREEN}✓ Downloaded: $OUTPUT_FILE ($SIZE)${NC}"
  echo ""
  echo -e "${BOLD}${GREEN}╔══════════════════════════════════════════════════╗${NC}"
  echo -e "${BOLD}${GREEN}║  ✅ Done!                                       ║${NC}"
  echo -e "${BOLD}${GREEN}║                                                  ║${NC}"
  echo -e "${BOLD}${GREEN}║  Your audit package:                            ║${NC}"
  echo -e "${BOLD}${GREEN}║  ${CYAN}$OUTPUT_FILE${GREEN}  ║${NC}"
  echo -e "${BOLD}${GREEN}║                                                  ║${NC}"
  echo -e "${BOLD}${GREEN}║  Contains all 8 documents as DOCX              ║${NC}"
  echo -e "${BOLD}${GREEN}║  (and PDF if LibreOffice is installed)         ║${NC}"
  echo -e "${BOLD}${GREEN}╚══════════════════════════════════════════════════╝${NC}"
else
  echo -e "${RED}Download failed${NC}"
  exit 1
fi
