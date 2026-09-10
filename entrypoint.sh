#!/bin/sh
set -e

PORT="${PORT:-8000}"
case "$PORT" in
    (*[!0-9]*|"") PORT=8000 ;;
esac

echo "==> DO'KON POS: Ishga tushirilmoqda (PORT: ${PORT})..."
exec python /app/gunicorn_run.py --bind 0.0.0.0:${PORT} --workers ${WEB_CONCURRENCY:-3} --timeout 120 "$@"

