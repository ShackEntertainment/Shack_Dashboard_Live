"""
SHACK ENTERTAINMENT — shack_scheduler.py
Fixed scheduler for chief_of_staff.py.

Usage in chief_of_staff.py — delete the old scheduler/add_job block and add:
    from shack_scheduler import init_scheduler
    init_scheduler(send_fn=print)          # today: console only, zero risk
Swap print for your Telegram send function later, with approval.
"""
from apscheduler.schedulers.background import BackgroundScheduler

_scheduler = None

DEFAULT_JOBS = [
    {"id": "shack_hourly_checkin", "minutes": 60,
     "message": "Shack hourly check-in: all agents nominal."},
]

def _deliver(message: str, send_fn) -> None:
    send_fn(message)

def init_scheduler(send_fn, jobs=None):
    global _scheduler
    if _scheduler is not None and _scheduler.running:
        return _scheduler
    _scheduler = BackgroundScheduler(daemon=True)
    for job in (jobs or DEFAULT_JOBS):
        _scheduler.add_job(
            _deliver,
            trigger="interval",
            minutes=job["minutes"],
            args=[job["message"], send_fn],   # THE FIX: message always supplied
            id=job["id"],
            replace_existing=True,
        )
    _scheduler.start()
    return _scheduler

def shutdown_scheduler():
    global _scheduler
    if _scheduler is not None and _scheduler.running:
        _scheduler.shutdown(wait=False)
        _scheduler = None