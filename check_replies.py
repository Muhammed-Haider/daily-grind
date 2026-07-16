import email
import imaplib
import json
import os
from datetime import date
from email.header import decode_header

DATA_DIR = os.path.join(os.path.dirname(__file__), "data")
REPLIES_FILE = os.path.join(DATA_DIR, "replies.json")

IMAP_HOST = "imap.gmail.com"


def load_json(path, default):
    if os.path.exists(path):
        with open(path) as f:
            return json.load(f)
    return default


def save_json(path, data):
    with open(path, "w") as f:
        json.dump(data, f, indent=2)


def get_text_body(msg):
    if msg.is_multipart():
        for part in msg.walk():
            if part.get_content_type() == "text/plain" and not part.get(
                "Content-Disposition"
            ):
                charset = part.get_content_charset() or "utf-8"
                return part.get_payload(decode=True).decode(charset, errors="replace")
        return ""
    else:
        charset = msg.get_content_charset() or "utf-8"
        return msg.get_payload(decode=True).decode(charset, errors="replace")


def decode_subject(raw_subject):
    if not raw_subject:
        return ""
    parts = decode_header(raw_subject)
    decoded = ""
    for text, enc in parts:
        if isinstance(text, bytes):
            decoded += text.decode(enc or "utf-8", errors="replace")
        else:
            decoded += text
    return decoded


def main():
    smtp_user = os.environ["SMTP_USER"]
    smtp_pass = os.environ["SMTP_PASS"]
    # The alias you send your daily replies to, e.g. yourname+dailygrind@gmail.com
    reply_alias = os.environ.get("REPLY_ALIAS", smtp_user)

    mail = imaplib.IMAP4_SSL(IMAP_HOST)
    mail.login(smtp_user, smtp_pass)
    mail.select("inbox")

    # Only pulls messages addressed to the alias, and only ones not yet processed (UNSEEN).
    # This does NOT scan or touch anything else in the inbox.
    status, data = mail.search(None, f'(TO "{reply_alias}" UNSEEN)')

    if status != "OK" or not data[0]:
        print("No new replies.")
        mail.logout()
        return

    ids = data[0].split()
    replies = load_json(REPLIES_FILE, [])

    for msg_id in ids:
        # PEEK so we control exactly when it's marked as read (after successful logging)
        status, msg_data = mail.fetch(msg_id, "(BODY.PEEK[])")
        raw_email = msg_data[0][1]
        msg = email.message_from_bytes(raw_email)

        body = get_text_body(msg).strip()
        subject = decode_subject(msg.get("Subject"))

        replies.append({
            "date": str(date.today()),
            "subject": subject,
            "text": body[:2000],  # cap length, avoid huge quoted email chains
        })

        # mark as read now that it's safely logged
        mail.store(msg_id, "+FLAGS", "\\Seen")

    save_json(REPLIES_FILE, replies)
    mail.logout()
    print(f"Logged {len(ids)} new repl{'y' if len(ids) == 1 else 'ies'}.")


if __name__ == "__main__":
    main()
