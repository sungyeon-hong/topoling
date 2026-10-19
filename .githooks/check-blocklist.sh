#!/bin/sh
# Shared by pre-commit and commit-msg: refuse text that matches the private
# blocklist. Venue names, dates and publication plans stay out of this public
# repository; see "Gotchas" in CLAUDE.md.
LIST=$(git config --get topoling.blocklist)
if [ ! -f "$LIST" ]; then
    echo "warning: $LIST not found; venue check skipped." >&2
    exit 0
fi
PATTERNS=$(grep -v '^#' "$LIST" | grep -v '^[[:space:]]*$')
HITS=$(grep -n -i -E -f /dev/stdin "$1" <<EOP
$PATTERNS
EOP
)
if [ -n "$HITS" ]; then
    echo "Refused: this $2 mentions material kept out of the public repository:" >&2
    echo "$HITS" | sed 's/^/  /' >&2
    echo "Reword it (e.g. 'the target venue'), or keep it outside the repository." >&2
    exit 1
fi
