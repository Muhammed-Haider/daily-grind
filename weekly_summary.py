import json
import os
import smtplib
from datetime import date, timedelta
from email.mime.text import MIMEText

DATA_DIR = os.path.join(os.path.dirname(__file__), "data")
HISTORY_FILE = os.path.join(DATA_DIR, "history.json")
REPLIES_FILE = os.path.join(DATA_DIR, "replies.json")


def load_json(path, default):
    if os.path.exists(path):
        with open(path) as f:
            return json.load(f)
    return default


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
    history = load_json(HISTORY_FILE, [])
    cutoff = date.today() - timedelta(days=7)
    week = [h for h in history if date.fromisoformat(h["date"]) > cutoff]

    if not week:
        body = "No entries logged this week — check the daily workflow is running."
    else:
        problems_solved = len(week)
        total_pages = sum(h["ddia_end"] - h["ddia_start"] + 1 for h in week)
        page_start = week[0]["ddia_start"]
        page_end = week[-1]["ddia_end"]

        lines = [
            f"This week: {problems_solved}/7 days sent, {total_pages} DDIA pages covered (p{page_start}-p{page_end}).\n",
            "Codeforces problems this week:",
        ]
        for h in week:
            lines.append(f"  - {h['problem_name']} (rating {h['problem_rating']}) - {h['problem_link']}")

        body = "\n".join(lines)

    replies = load_json(REPLIES_FILE, [])
    week_replies = [r for r in replies if date.fromisoformat(r["date"]) > cutoff]

    if week_replies:
        body += "\n\nYour replies this week:\n"
        for r in week_replies:
            body += f"  [{r['date']}] {r['text'][:200]}\n"
    else:
        body += "\n\nNo replies logged this week."

    send_email("Weekly recap: CF + DDIA", body)
    print("Weekly summary sent")


if __name__ == "__main__":
    main()
