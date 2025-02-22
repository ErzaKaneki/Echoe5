# Create renew_cert.bat in project root
@echo off
call dev\Scripts\activate
python manage.py renew_cert --notify