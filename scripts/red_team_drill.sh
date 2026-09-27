#!/usr/bin/env bash
# red_team_drill.sh — Run all red-team probes and show pass/fail
set -e
API=${1:-http://localhost:8000}

echo "🔴 Red-Team Drill — AI Intake Cop"
echo "========================================"
echo ""

# Get probe list
PROBES=$(curl -s "$API/guardrails/red-team-probes" | python3 -c "import sys,json; [print(p) for p in json.load(sys.stdin)['probes']]")

while IFS= read -r probe; do
    echo "Probe: ${probe:0:60}..."
    RESULT=$(curl -s -X POST "$API/guardrails/regex-check" \
        -H "Content-Type: application/json" \
        -d "{\"text\": $(python3 -c "import json,sys; print(json.dumps(sys.argv[1]))" "$probe")}")
    SAFE=$(echo "$RESULT" | python3 -c "import sys,json; d=json.load(sys.stdin); print('SAFE' if d.get('safe') else 'BLOCKED')")
    if [ "$SAFE" = "BLOCKED" ]; then
        echo "  ✅ BLOCKED by regex"
    else
        echo "  ⚠️  PASSED regex (escalate to semantic check!)"
    fi
    echo ""
done <<< "$PROBES"

echo "Run /guardrails/red-team-run for JSON summary."
