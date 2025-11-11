# **Celery and Periodic Task Setup**

This guide details the steps required to install prerequisites, run migrations, and start the Celery worker and Celery Beat scheduler for automated CRM reports.

## **Prerequisites**

You must have **Redis Server** installed and running on localhost:6379, as it is configured as the message broker for Celery.

## **Installation and Setup**

1. Install Python Dependencies:  
   Ensure you install celery, django-celery-beat, and redis.  
   pip install \-r requirements.txt

2. Run Migrations:  
   The django-celery-beat application requires database tables to store periodic task schedules.  
   python manage.py migrate

## **Running Celery Components**

You must run the Django server, the Celery Worker, and Celery Beat concurrently.

### **1\. Start Django Server (Web App)**

python manage.py runserver

### **2\. Start Celery Worker**

The worker executes tasks (like generate\_crm\_report) placed in the message queue.

celery \-A crm worker \-l info

### **3\. Start Celery Beat Scheduler**

Celery Beat monitors the CELERY\_BEAT\_SCHEDULE in settings.py and periodically sends tasks to the queue according to the schedule (e.g., every Monday at 06:00 AM for the report).

celery \-A crm beat \-l info

## **Verification**

Once Celery Beat runs (or once you trigger the task manually), the report will be logged.

* **Verify Logs:** Check the contents of the log file:  
  cat /tmp/crm\_report\_log.txt

  The output should show a line similar to:  
  YYYY-MM-DD HH:MM:SS \- Report: X customers, Y orders, $Z revenue