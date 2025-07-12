# CRM Celery Report Setup

## Installation and Setup

1. Install Redis:
   - On Ubuntu: `sudo apt install redis-server`
   - Start Redis service: `sudo service redis-server start`

2. Install dependencies:
   ```bash
   pip install -r requirements.txt
3. Run Django migrations for celery beat:
    - python manage.py migrate

4. Start Celery worker:
    - celery -A crm worker -l info

5. Start Celery beat scheduler:
    - celery -A crm beat -l info

6. Verify logs:
    - Check the CRM report log file at /tmp/crm_report_log.txt


---

### Summary

- Added Celery and Beat setup to `settings.py`
- Created `crm/celery.py` for Celery app initialization
- Added `tasks.py` with a shared task that queries GraphQL and writes logs
- Registered celery app in `__init__.py`
- Added documentation for setup and usage in README

---

If you want, I can help generate any of these files fully for you! Would you like that?
