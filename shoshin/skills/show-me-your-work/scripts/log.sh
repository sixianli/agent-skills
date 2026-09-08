#!/usr/bin/env bash
# Adapted from PStack, Copyright (c) 2026 Lauren Tan, MIT.
# One task owns one log; callers must not write to it concurrently.
set -euo pipefail
if [ "$#" -ne 6 ]; then
    printf 'usage: log.sh <logfile> <phase> <decision> <why> <evidence> <result>\n' >&2
    exit 1
fi
logfile="$1"
shift
header=$'ts\tphase\tdecision\twhy\tevidence\tresult'
if [ -e "$logfile" ] && [ ! -f "$logfile" ]; then
    printf 'log target is not a regular file\n' >&2
    exit 1
fi
if [ -s "$logfile" ]; then
    IFS= read -r existing < "$logfile" || true
    if [ "$existing" != "$header" ]; then
        printf 'existing log has an invalid header; unchanged\n' >&2
        exit 1
    fi
fi
clean() {
    local value trimmed
    value=$(printf '%s' "$1" | tr '\t\n\r' '   ')
    trimmed="${value#"${value%%[![:space:]]*}"}"
    case "$trimmed" in
        =*|+*|-*|@*) value="'$value" ;;
    esac
    case "$value" in
        *\"*) value="${value//\"/\"\"}"; printf '"%s"' "$value" ;;
        *) printf '%s' "$value" ;;
    esac
}
# Prepare the full row before opening the output, so conversion errors are visible.
ts="$(date -u +%Y-%m-%dT%H:%M:%SZ)"
phase="$(clean "$1")"
decision="$(clean "$2")"
why="$(clean "$3")"
evidence="$(clean "$4")"
result="$(clean "$5")"
mkdir -p -- "$(dirname -- "$logfile")"
{
    if [ ! -s "$logfile" ]; then printf '%s\n' "$header"; fi
    if [ -s "$logfile" ] && [ -n "$(tail -c 1 -- "$logfile")" ]; then printf '\n'; fi
    printf '%s\t%s\t%s\t%s\t%s\t%s\n' "$ts" "$phase" "$decision" "$why" "$evidence" "$result"
} >> "$logfile"
