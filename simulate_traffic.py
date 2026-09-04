"""
Simulates visitor traffic against the ABC Tutoring site by sending events
directly to PostHog's capture API. Use this to populate PostHog with
realistic data before demoing the analytics to Dana.

Usage:
    pip install requests
    python simulate_traffic.py

If your PostHog project is not on the US cloud, change API_HOST below
(EU cloud is https://eu.i.posthog.com).
"""

import random
import time
import uuid
from datetime import datetime, timedelta

import requests

API_KEY = "phc_scigRnBaEhFJtzqksc8tD3kKXQYGXeXxvG8QA9SA7kVj"
API_HOST = "https://us.i.posthog.com"
CAPTURE_URL = f"{API_HOST}/capture/"

TUTORS = [
    {"name": "Maria Chen", "subjects": ["Elementary Math", "Algebra II"], "rate": 35},
    {"name": "James Whitfield", "subjects": ["Science"], "rate": 40},
    {"name": "Priya Anand", "subjects": ["Elementary Reading"], "rate": 30},
    {"name": "Sam Okafor", "subjects": ["Algebra II", "Elementary Math"], "rate": 38},
    {"name": "Laura Bennett", "subjects": ["Science", "Elementary Reading"], "rate": 32},
    {"name": "David Kim", "subjects": ["Elementary Math", "Science"], "rate": 34},
]

# Weighted so some tutors/subjects are clearly more popular than others,
# which gives Dana something meaningful to see in the dashboard.
TUTOR_WEIGHTS = [5, 2, 3, 4, 1, 2]
SUBJECT_FILTERS = ["All", "Elementary Math", "Algebra II", "Science", "Elementary Reading"]
SUBJECT_WEIGHTS = [3, 5, 2, 3, 4]

GRADES = ["K", "1", "2", "3", "4", "5", "6", "7", "8", "9", "10", "11", "12"]


def send_event(distinct_id, event, properties=None, timestamp=None):
    payload = {
        "api_key": API_KEY,
        "event": event,
        "properties": {"distinct_id": distinct_id, **(properties or {})},
    }
    if timestamp:
        payload["timestamp"] = timestamp.isoformat()
    try:
        requests.post(CAPTURE_URL, json=payload, timeout=5)
    except requests.RequestException as e:
        print(f"  (warning: failed to send {event}: {e})")


def simulate_session(session_num, base_time):
    distinct_id = str(uuid.uuid4())
    t = base_time + timedelta(minutes=random.randint(0, 60 * 24 * 5))  # spread over ~5 days

    # 1. Land on homepage
    send_event(distinct_id, "$pageview", {"$current_url": "https://example.github.io/"}, t)

    # Most visitors click through to browse tutors
    if random.random() < 0.85:
        t += timedelta(seconds=random.randint(5, 40))
        send_event(distinct_id, "browse_tutors_clicked", {"source": "home_hero"}, t)
        t += timedelta(seconds=2)
        send_event(distinct_id, "$pageview", {"$current_url": "https://example.github.io/tutors.html"}, t)
    else:
        return  # bounced from homepage

    # Some visitors filter by subject
    if random.random() < 0.6:
        subject = random.choices(SUBJECT_FILTERS, weights=SUBJECT_WEIGHTS)[0]
        t += timedelta(seconds=random.randint(3, 15))
        send_event(distinct_id, "subject_filtered", {"subject": subject}, t)

    # Visitor views 1-3 tutor profiles
    num_views = random.randint(1, 3)
    viewed_tutors = random.choices(TUTORS, weights=TUTOR_WEIGHTS, k=num_views)
    booked = False
    for tutor in viewed_tutors:
        t += timedelta(seconds=random.randint(5, 30))
        send_event(distinct_id, "tutor_profile_viewed", {
            "tutor_name": tutor["name"],
            "subjects": tutor["subjects"],
            "rate": tutor["rate"],
        }, t)
        t += timedelta(seconds=2)
        send_event(distinct_id, "$pageview", {"$current_url": f"https://example.github.io/booking.html?tutor={tutor['name']}"}, t)

        # Some visitors who view a profile go on to start a booking
        if not booked and random.random() < 0.45:
            subject = random.choice(tutor["subjects"])
            t += timedelta(seconds=random.randint(10, 60))
            send_event(distinct_id, "booking_started", {
                "tutor_name": tutor["name"],
                "slot": "Sample slot",
            }, t)

            # Most who start a booking complete it; some abandon (the drop-off Dana cares about)
            if random.random() < 0.7:
                t += timedelta(seconds=random.randint(20, 90))
                send_event(distinct_id, "booking_completed", {
                    "tutor_name": tutor["name"],
                    "subject": subject,
                    "student_grade": random.choice(GRADES),
                    "slot": "Sample slot",
                }, t)
                booked = True


def main():
    num_sessions = 120
    base_time = datetime.utcnow() - timedelta(days=6)
    print(f"Simulating {num_sessions} visitor sessions...")
    for i in range(num_sessions):
        simulate_session(i, base_time)
        if (i + 1) % 20 == 0:
            print(f"  {i + 1}/{num_sessions} sessions sent")
        time.sleep(0.02)  # light throttle
    print("Done. Give PostHog a minute to ingest, then check your dashboard.")


if __name__ == "__main__":
    main()
