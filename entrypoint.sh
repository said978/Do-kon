#!/bin/sh
set -e

echo "==> DO'KON POS: Statik fayllarni yig'ish (collectstatic)..."
python manage.py collectstatic --noinput

echo "==> DO'KON POS: Ma'lumotlar bazasi migratsiyalarini qo'llash (migrate)..."
python manage.py migrate --noinput

PORT=${PORT:-8000}
WORKERS=${WEB_CONCURRENCY:-3}

echo "==> DO'KON POS: Gunicorn veb-serverini 0.0.0.0:${PORT} portida ishga tushirish..."
exec gunicorn core.wsgi:application \
    --bind 0.0.0.0:${PORT} \
    --workers ${WORKERS} \
    --timeout 120 \
    --access-logfile - \
    --error-logfile -
