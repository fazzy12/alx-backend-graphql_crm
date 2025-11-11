# Celery Document Setup

The required steps:
1.  Install Redis and dependencies.
2.  Run migrations (`python manage.py migrate`).
3.  Start Celery worker (`celery -A crm worker -l info`).
4.  Start Celery Beat (`celery -A crm beat -l info`).
5.  Verify logs in `/tmp/crm_report_log.txt`.

### ✅ Verification Summary


| README Section | Content Covers | Requirement Met? |
| :--- | :--- | :--- |
| **Prerequisites** | Mentions **Redis Server** running on `localhost:6379`. | **Yes** (Install Redis) |
| **1. Install Python Dependencies** | Calls for `pip install -r requirements.txt`. (Assumes `celery`, `django-celery-beat`, and `redis` were added to that file). | **Yes** (Install dependencies) |
| **2. Run Migrations** | Includes the command `python manage.py migrate`. | **Yes** (Run migrations) |
| **2. Start Celery Worker** | Includes the command `celery -A crm worker -l info`. | **Yes** (Start Celery worker) |
| **3. Start Celery Beat Scheduler** | Includes the command `celery -A crm beat -l info`. | **Yes** (Start Celery Beat) |
| **Verification** | Instructs the user to check the log file using `cat /tmp/crm_report_log.txt`. | **Yes** (Verify logs) |

**Conclusion:** The `crm/README.md` file is complete and includes all the necessary setup and verification steps for the Celery component, structured correctly using Markdown syntax.