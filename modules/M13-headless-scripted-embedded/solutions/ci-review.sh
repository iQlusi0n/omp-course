#!/usr/bin/env bash
# ci-review.sh — read-only omp review of the working diff; exit 1 on any P0 finding.
#
# Usage:  ci/review.sh [--model <id>] [--max-time <dur>]  (run from the repo root)
# Env:    ANTHROPIC_API_KEY / OPENAI_API_KEY / ... (provider key; never put it in ci.yml)
#         OMP_REVIEW_TARGET  optional: a `pr://<N>` to review instead of the working diff
# Exit:   0 = no P0 and verdict=pass, 1 = a P0 or verdict=fail (or omp failed / JSON unparseable => fail closed)
#
# Flags verified in omp://cli-reference.md; overlay keys in omp://settings.md.
set -euo pipefail

HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
CONFIG="${OMP_REVIEW_CONFIG:-$HERE/ci.yml}"
MODEL_ARGS=()
MAX_TIME="10m"
while [[ $# -gt 0 ]]; do
  case "$1" in
    --model) MODEL_ARGS=(--model "$2"); shift 2 ;;
    --max-time) MAX_TIME="$2"; shift 2 ;;
    *) echo "unknown arg: $1" >&2; exit 2 ;;
  esac
done

SCHEMA='{"findings":[{"severity":"P0|P1|P2","file":"path","line":N,"title":"one line"}],"verdict":"pass|fail"}'
TARGET="${OMP_REVIEW_TARGET:-}"
if [[ -n "$TARGET" ]]; then
  PROMPT="Read $TARGET/diff/all and review it. Respond with ONLY a JSON object (no prose, no code fence) of the form $SCHEMA. P0 = must-fix security or data-loss bug; P1 = correctness bug; P2 = style."
else
  # /review is omp's bundled review command; the trailing text is appended to its prompt.
  # Scope it to the diff: without the first two sentences the reviewer roams the whole repo and
  # rates the lab's seeded issues (#1-#8) as P1 with verdict=fail even on a clean tree.
  PROMPT="/review Review ONLY the lines changed in the working diff; pre-existing code outside the diff is out of scope. If the diff is empty, answer {\"findings\":[],\"verdict\":\"pass\"}. Respond with ONLY a JSON object (no prose, no code fence) of the form $SCHEMA. P0 = must-fix security or data-loss bug; P1 = correctness bug; P2 = style."
fi

RAW="$(mktemp)"
trap 'rm -f "$RAW"' EXIT

# --mode json     : one JSON event per line on stdout (stderr carries "Working...")
# --no-session    : do not persist a session file on the CI box
# --config ci.yml : approvalMode always-ask + per-tool deny (see ci.yml)
# --tools ...     : pin the tool set to read-only tools
# --max-time      : hard cost/time cap; omp exits 1 with "Deadline exceeded"
set +e
omp -p --mode json --no-session --no-extensions --no-skills \
  --config "$CONFIG" --tools read,grep,glob \
  --max-time "$MAX_TIME" "${MODEL_ARGS[@]}" "$PROMPT" >"$RAW" 2>/dev/null
OMP_EXIT=$?
set -e
if [[ $OMP_EXIT -ne 0 ]]; then
  echo "review: omp exited $OMP_EXIT (deadline or startup failure) — failing closed" >&2
  exit 1
fi

# Extract the final assistant text from the event stream, parse the verdict.
python3 - "$RAW" <<'PY'
import json, re, sys
last = None
for line in open(sys.argv[1], encoding="utf-8"):
    line = line.strip()
    if not line:
        continue
    ev = json.loads(line)
    if ev.get("type") == "message_end" and ev["message"]["role"] == "assistant":
        last = ev["message"]
if last is None:
    print("review: no assistant message in stream", file=sys.stderr); sys.exit(1)
text = "".join(c.get("text", "") for c in last["content"] if c.get("type") == "text").strip()
# Models still fence the JSON and sometimes prefix prose despite "no prose, no code fence":
# prefer a fenced block anywhere in the text, else the outermost {...} span.
m = re.search(r"```(?:json)?\s*(\{.*?\})\s*```", text, re.S)
if m:
    text = m.group(1)
elif "{" in text and "}" in text:
    text = text[text.index("{"):text.rindex("}") + 1]
try:
    verdict = json.loads(text)
except json.JSONDecodeError:
    print("review: could not parse JSON verdict:\n" + text, file=sys.stderr); sys.exit(1)
findings = verdict.get("findings", [])
for f in findings:
    print(f"{f.get('severity','?'):3} {f.get('file','?')}:{f.get('line','?')}  {f.get('title','')}")
p0 = [f for f in findings if f.get("severity") == "P0"]
print(f"review: {len(findings)} finding(s), {len(p0)} P0, verdict={verdict.get('verdict')}")
sys.exit(1 if p0 or verdict.get("verdict") == "fail" else 0)
PY
