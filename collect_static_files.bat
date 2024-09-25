@echo off
echo Collecting static files....
python manage.py collectstatic --noinput
pause
