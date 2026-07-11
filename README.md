# Daily CF + DDIA Grind

Sends you one email every morning with:
- A fresh Codeforces problem (rating 800-1200, never repeats until you've done them all)
- Your next 10 pages of DDIA to read, tracked automatically

Runs for free on GitHub Actions — no server, no phone app needed.

## Setup (10 minutes, one-time)

### 1. Create a Gmail App Password (so the script can send email as you)
- Go to https://myaccount.google.com/apppasswords
- Generate a new App Password (name it "daily-grind")
- Copy the 16-character password — you'll need it in step 3

If you'd rather receive the email at a different address than the one sending it, that's fine — just set `TO_EMAIL` differently in step 3.

### 2. Create a new GitHub repo
- Go to github.com -> New repository -> name it `daily-grind` -> Create
- Upload all the files from this folder (drag and drop works, or use `git push`)

### 3. Add your secrets
In your new repo: **Settings -> Secrets and variables -> Actions -> New repository secret**

Add three secrets:
| Name | Value |
|---|---|
| `SMTP_USER` | your Gmail address |
| `SMTP_PASS` | the App Password from step 1 |
| `TO_EMAIL` | the email you want the daily message sent to |

### 4. Test it
Go to the **Actions** tab -> "Daily CF + DDIA email" -> **Run workflow** (this is the `workflow_dispatch` trigger). Check your email within a minute or two.

### 5. Done
It'll now run automatically every day at 6:30 AM PKT. To change the time, edit the `cron` line in `.github/workflows/daily.yml` (cron times are in UTC — PKT is UTC+5).

## Adjusting settings
Open `daily_send.py`:
- `MIN_RATING` / `MAX_RATING` — change problem difficulty as you improve
- `PAGES_PER_DAY` — change DDIA pace (default 10/day, finishes in ~2 months)
- `DDIA_TOTAL_PAGES` — adjust if your edition's page count differs from 616

## Note on "alarm"
This sends an email, not a literal phone alarm — a script can't ring your phone directly. To make it feel more like an alarm: turn on loud notification sound for this specific sender in your email app's settings, so it wakes you up like a message alert would.
