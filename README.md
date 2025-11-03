# RemindMeSoon

RemindMeSoon is a lightweight email reminder service that lets users schedule messages for later delivery. It was built to explore asynchronous task scheduling and background processing in Python, supporting two modes: a local Celery and Redis queue and a production-ready QStash webhook system for zero-polling task execution.

🧭 Try it live at [remindmesoon.xyz](https://remindmesoon.xyz)

Create a reminder and receive an email when it triggers! 

*Note: reminder times limited to 1, 3, and 5 minutes for demo purposes*

## Learning Outcomes
- Implemented async scheduling via Celery and Redis, then migrated to webhook-driven scheduling with QStash to eliminate worker polling costs.
- Designed an ORM model with SQLAlchemy to track reminder task lifecycle states.
- Containerized full stack with Docker and deployed to Fly.io using Postgres and Mailgun integrations.

## Tech Stack
- **Flask** – REST API
- **SQLAlchemy** – ORM and persistence
- **PostgreSQL / SQLite** – relational database
- **Celery + Redis** – async queue (local)
- **QStash Webhooks** – async scheduling (production)
- **Mailgun** – transactional email delivery
- **Docker + Fly.io** – containerized deployment
