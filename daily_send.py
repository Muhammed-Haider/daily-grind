import json
import os
import random
import smtplib
import urllib.request
from datetime import date
from email.mime.text import MIMEText

DATA_DIR = os.path.join(os.path.dirname(__file__), "data")
USED_FILE = os.path.join(DATA_DIR, "used_problems.json")
DDIA_FILE = os.path.join(DATA_DIR, "ddia_progress.json")
HISTORY_FILE = os.path.join(DATA_DIR, "history.json")

MIN_RATING = 800
MAX_RATING = 1200
PAGES_PER_DAY = 10          # change this number to speed up / slow down DDIA
DDIA_TOTAL_PAGES = 616      # adjust if your edition has a different page count


def load_json(path, default):
    if os.path.exists(path):
        with open(path) as f:
            return json.load(f)
    return default


def save_json(path, data):
    with open(path, "w") as f:
        json.dump(data, f)


def get_codeforces_problem(used_ids):
    url = "https://codeforces.com/api/problemset.problems"
    with urllib.request.urlopen(url) as resp:
        data = json.load(resp)

    problems = data["result"]["problems"]
    candidates = [
        p for p in problems
        if p.get("rating") and MIN_RATING <= p["rating"] <= MAX_RATING
        and f"{p['contestId']}{p['index']}" not in used_ids
    ]

    if not candidates:
        # ran out of fresh problems in range -> reset the used list
        candidates = [
            p for p in problems
            if p.get("rating") and MIN_RATING <= p["rating"] <= MAX_RATING
        ]
        used_ids = []

    problem = random.choice(candidates)
    pid = f"{problem['contestId']}{problem['index']}"
    used_ids.append(pid)

    link = f"https://codeforces.com/problemset/problem/{problem['contestId']}/{problem['index']}"
    return problem, link, used_ids


def get_ddia_range():
    progress = load_json(DDIA_FILE, {"current_page": 1})
    start = progress["current_page"]
    end = min(start + PAGES_PER_DAY - 1, DDIA_TOTAL_PAGES)
    progress["current_page"] = end + 1 if end < DDIA_TOTAL_PAGES else 1  # loop back if finished
    save_json(DDIA_FILE, progress)
    return start, end


def send_email(subject, body):
    smtp_user = os.environ["SMTP_USER"]
    smtp_pass = os.environ["SMTP_PASS"]
    to_email = os.environ["TO_EMAIL"]

    msg = MIMEText(body)
    msg["Subject"] = subject
    msg["From"] = smtp_user
    msg["To"] = to_email

    with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
        server.login(smtp_user, smtp_pass)
        server.sendmail(smtp_user, [to_email], msg.as_string())


def main():
    used_ids = load_json(USED_FILE, [])
    problem, link, used_ids = get_codeforces_problem(used_ids)
    save_json(USED_FILE, used_ids)

    start_page, end_page = get_ddia_range()

    subject = "Today's grind: 1 Codeforces problem + DDIA pages"
    body = (
        f"Good morning.\n\n"
        f"CODEFORCES ({MIN_RATING}-{MAX_RATING}):\n"
        f"{problem['name']} (rating {problem['rating']})\n"
        f"{link}\n\n"
        f"DDIA:\n"
        f"Read pages {start_page}-{end_page} today.\n"
        f"(explain-back after: could you rebuild it from scratch?)\n"
    )

    send_email(subject, body)

    history = load_json(HISTORY_FILE, [])
    history.append({
        "date": str(date.today()),
        "problem_name": problem["name"],
        "problem_rating": problem["rating"],
        "problem_link": link,
        "ddia_start": start_page,
        "ddia_end": end_page,
    })
    save_json(HISTORY_FILE, history)

    print("Sent:", subject)


if __name__ == "__main__":
    main()
