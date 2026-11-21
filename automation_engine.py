# ==========================================================
# JARVIS AI
# AUTOMATION ENGINE
# Python 3.12
# Version 1.0 (basic — one small piece of everything)
# ==========================================================
#
# Optional dependencies (only needed for the features you use):
#   pip install keyboard --break-system-packages
#   pip install screen-brightness-control --break-system-packages
#
# Notes:
#   - Wi-Fi toggling uses `netsh` and usually needs the terminal
#     to be run as Administrator.
#   - Volume control sends the same key presses as your keyboard's
#     media keys (relative up/down/mute), not an exact percentage.
#   - Reminders are in-memory only — they reset if Jarvis restarts.
#
# ==========================================================

import datetime
import os
import re
import subprocess
import threading

try:
    import screen_brightness_control as sbc
    BRIGHTNESS_AVAILABLE = True
except ImportError:
    BRIGHTNESS_AVAILABLE = False

try:
    import keyboard
    KEYBOARD_AVAILABLE = True
except ImportError:
    KEYBOARD_AVAILABLE = False


# ==========================================================
# KNOWN APPLICATIONS
# ==========================================================
# Add more entries here as you need them — key is what the
# user says, value is the executable Windows can resolve.

KNOWN_APPS = {
    "notepad": "notepad.exe",
    "calculator": "calc.exe",
    "calc": "calc.exe",
    "chrome": "chrome.exe",
    "browser": "chrome.exe",
    "explorer": "explorer.exe",
    "file explorer": "explorer.exe",
    "vscode": "code",
    "vs code": "code",
    "cmd": "cmd.exe",
    "command prompt": "cmd.exe",
    "paint": "mspaint.exe",
    "wordpad": "write.exe",
}

# ==========================================================
# KNOWN PROCESS NAMES (for closing apps)
# ==========================================================
# taskkill needs the actual process name, which isn't always the
# same string as the launch executable above (e.g. modern Windows
# Calculator runs as CalculatorApp.exe, not calc.exe).

KNOWN_PROCESSES = {
    "notepad": "notepad.exe",
    "calculator": "CalculatorApp.exe",
    "calc": "CalculatorApp.exe",
    "chrome": "chrome.exe",
    "browser": "chrome.exe",
    "explorer": "explorer.exe",
    "file explorer": "explorer.exe",
    "vscode": "Code.exe",
    "vs code": "Code.exe",
    "cmd": "cmd.exe",
    "command prompt": "cmd.exe",
    "paint": "mspaint.exe",
    "wordpad": "wordpad.exe",
}


# ==========================================================
# APP LAUNCHING
# ==========================================================

def open_app(app_name):
    app_name = app_name.strip().lower()
    executable = KNOWN_APPS.get(app_name)

    if executable is None:
        return (
            f"I don't know how to open '{app_name}' yet. "
            f"Add it to KNOWN_APPS in automation_engine.py."
        )

    try:
        subprocess.Popen(executable, shell=True)
        return f"Opening {app_name}."
    except Exception as error:
        return f"Couldn't open {app_name}: {error}"


# ==========================================================
# GENERIC APP CLOSING
# ==========================================================
# Works for any app, not just the ones already open by name —
# if it's not in KNOWN_PROCESSES, we guess "<name>.exe" and let
# taskkill try it.

def close_app(app_name):
    app_name = app_name.strip().lower()
    process_name = KNOWN_PROCESSES.get(app_name)

    if process_name is None:
        process_name = app_name if app_name.endswith(".exe") else f"{app_name}.exe"

    try:
        result = subprocess.run(
            ["taskkill", "/IM", process_name, "/F"],
            capture_output=True,
            text=True,
            shell=True,
        )

        if result.returncode == 0:
            return f"Closed {app_name}."

        detail = result.stderr.strip() or result.stdout.strip() or "process not found."
        return f"I couldn't close {app_name}: {detail}"

    except Exception as error:
        return f"Couldn't close {app_name}: {error}"


# ==========================================================
# FILE / FOLDER OPERATIONS
# ==========================================================

def open_path(path):
    path = path.strip().strip('"')

    if not os.path.exists(path):
        return f"I couldn't find '{path}'."

    try:
        os.startfile(path)
        return f"Opening {path}."
    except Exception as error:
        return f"Couldn't open {path}: {error}"


def delete_path(path):
    # DESTRUCTIVE — brain.py must confirm with the user before
    # calling this. Only deletes empty folders (safer default).
    path = path.strip().strip('"')

    if not os.path.exists(path):
        return f"I couldn't find '{path}'."

    try:
        if os.path.isdir(path):
            os.rmdir(path)
        else:
            os.remove(path)
        return f"Deleted '{path}'."
    except Exception as error:
        return f"Couldn't delete '{path}': {error}"


# ==========================================================
# SYSTEM CONTROLS — VOLUME
# ==========================================================

def volume_up():
    if not KEYBOARD_AVAILABLE:
        return "The 'keyboard' package isn't installed. Run: pip install keyboard"
    keyboard.send("volume up")
    return "Volume increased."


def volume_down():
    if not KEYBOARD_AVAILABLE:
        return "The 'keyboard' package isn't installed. Run: pip install keyboard"
    keyboard.send("volume down")
    return "Volume decreased."


def volume_mute():
    if not KEYBOARD_AVAILABLE:
        return "The 'keyboard' package isn't installed. Run: pip install keyboard"
    keyboard.send("volume mute")
    return "Volume muted or unmuted."


# ==========================================================
# SYSTEM CONTROLS — BRIGHTNESS
# ==========================================================

def brightness_up(step=10):
    if not BRIGHTNESS_AVAILABLE:
        return (
            "The 'screen_brightness_control' package isn't installed. "
            "Run: pip install screen-brightness-control"
        )
    try:
        current = sbc.get_brightness(display=0)[0]
        new_value = min(current + step, 100)
        sbc.set_brightness(new_value)
        return f"Brightness increased to {new_value}%."
    except Exception as error:
        return f"Couldn't change brightness: {error}"


def brightness_down(step=10):
    if not BRIGHTNESS_AVAILABLE:
        return (
            "The 'screen_brightness_control' package isn't installed. "
            "Run: pip install screen-brightness-control"
        )
    try:
        current = sbc.get_brightness(display=0)[0]
        new_value = max(current - step, 0)
        sbc.set_brightness(new_value)
        return f"Brightness decreased to {new_value}%."
    except Exception as error:
        return f"Couldn't change brightness: {error}"


# ==========================================================
# SYSTEM CONTROLS — WI-FI
# ==========================================================

def wifi_toggle(turn_on):
    # RISKY — needs admin privileges and brain.py should confirm
    # with the user before calling this.
    action = "enable" if turn_on else "disable"

    try:
        subprocess.run(
            ["netsh", "interface", "set", "interface", "Wi-Fi", f"admin={action}"],
            check=True,
            shell=True,
        )
        return f"Wi-Fi {'enabled' if turn_on else 'disabled'}."
    except Exception as error:
        return (
            f"Couldn't change Wi-Fi state: {error}. "
            f"This usually needs Administrator privileges."
        )


def check_wifi_status():
    # Read-only — doesn't need admin privileges the way toggling does.
    try:
        result = subprocess.run(
            ["netsh", "interface", "show", "interface", "Wi-Fi"],
            capture_output=True,
            text=True,
            shell=True,
        )

        output = result.stdout.lower()

        if "connected" in output and "disconnected" not in output:
            return "Wi-Fi is on and connected."
        if "enabled" in output:
            return "Wi-Fi is enabled but not connected to a network."
        if "disabled" in output:
            return "Wi-Fi is currently turned off."

        return "I couldn't determine the Wi-Fi status."

    except Exception as error:
        return f"Couldn't check Wi-Fi status: {error}"


# ==========================================================
# LIST AUTOMATION SETTINGS / CAPABILITIES
# ==========================================================

def list_settings():
    lines = [
        "Automation capabilities I currently support:",
        "",
        "- Apps: open <" + ", ".join(sorted(KNOWN_APPS.keys())) + ">, close <any app>",
        "- Files: open <path>, delete file <path> (asks for confirmation first)",
        "- Volume: volume up / volume down / mute",
        "- Brightness: brightness up / brightness down",
        "- Wi-Fi: wifi on / wifi off (asks for confirmation), check wifi",
        "- Reminders: remind me to <task> in <N> minutes / at <time>, "
        "list reminders (plays a beep when a reminder fires)",
        "- Notifications (experimental, needs Chrome + Selenium, and you "
        "must already be logged in): check <whatsapp/youtube> for messages",
        "- Compound commands: separate multiple tasks with a comma or "
        "'and', e.g. 'open notepad, open calculator'",
    ]
    return "\n".join(lines)


# ==========================================================
# SCHEDULED TASKS / REMINDERS
# ==========================================================

_reminders = []


def _play_reminder_sound():
    # Windows-only beep. Fails silently on other platforms or if
    # winsound isn't available — the printed [REMINDER] line below
    # still shows either way.
    try:
        import winsound
        winsound.Beep(1000, 350)
        winsound.Beep(1300, 350)
    except Exception:
        pass


def reminder_callback(message):
    # Runs on a background thread when the reminder fires.
    # Chat mode will see this printed the next time it refreshes
    # the console; voice mode could be extended to also call speak().
    _play_reminder_sound()
    print(f"\n[REMINDER] {message}\n")


def schedule_reminder(message, delay_seconds, callback):
    timer = threading.Timer(delay_seconds, callback, args=[message])
    timer.daemon = True
    timer.start()

    fire_time = datetime.datetime.now() + datetime.timedelta(seconds=delay_seconds)

    _reminders.append({
        "message": message,
        "time": fire_time.strftime("%d-%m-%Y %H:%M:%S"),
    })

    return fire_time


def list_reminders():
    return _reminders


# ==========================================================
# TIME PARSING HELPERS (for reminders)
# ==========================================================

def parse_relative_delay_seconds(time_text):
    """
    Parses phrases like "in 10 minutes", "in 2 hours", "in 30 seconds".
    Returns delay in seconds, or None if it can't be parsed.
    """

    match = re.match(r"^in\s+(\d+)\s*(second|minute|hour)s?$", time_text.strip())

    if not match:
        return None

    amount = int(match.group(1))
    unit = match.group(2)

    if unit == "second":
        return amount
    if unit == "minute":
        return amount * 60
    if unit == "hour":
        return amount * 3600

    return None


def parse_absolute_delay_seconds(time_text):
    """
    Parses phrases like "5 pm", "5:30 pm", "17:30".
    Returns delay in seconds from now, or None if it can't be parsed.
    """

    time_text = time_text.strip().lower()
    now = datetime.datetime.now()

    formats = ["%I:%M %p", "%I %p", "%H:%M", "%H"]

    for fmt in formats:
        try:
            parsed = datetime.datetime.strptime(time_text, fmt)
        except ValueError:
            continue

        target = now.replace(
            hour=parsed.hour,
            minute=getattr(parsed, "minute", 0),
            second=0,
            microsecond=0,
        )

        if target <= now:
            target += datetime.timedelta(days=1)

        return (target - now).total_seconds()

    return None


# ==========================================================
# NOTIFICATION CHECKING (EXPERIMENTAL, BEST-EFFORT)
# ==========================================================
# There is no official API for reading your WhatsApp/YouTube
# notifications from a desktop script. The only way to approach it
# is to drive a real, visible Chrome window with Selenium and read
# the page's HTML — which means:
#
#   1. It needs:  pip install selenium --break-system-packages
#      (Selenium 4.6+ auto-downloads a matching chromedriver the
#      first time webdriver.Chrome() runs — no manual driver needed.)
#   2. The FIRST time you check WhatsApp, Chrome will show the
#      web.whatsapp.com QR code — you scan it once with your phone.
#      After that, the named profile below keeps you logged in.
#   3. The CSS/aria-label selectors below match WhatsApp Web's site
#      as of writing. If WhatsApp changes their site layout, this
#      selector will need updating — that's an inherent limitation
#      of scraping a website instead of using a real API.
#
# NOTIFICATION_SITES is intentionally a plain dict so you can keep
# adding services (youtube, gmail, etc.) the same way.

NOTIFICATION_SITES = {
    "whatsapp": "https://web.whatsapp.com",
    "youtube": "https://www.youtube.com",
}

# ==========================================================
# NAMED CHROME PROFILES
# ==========================================================
# Instead of one throwaway/anonymous profile, Jarvis remembers a
# profile NAME (you pick it once) and always reuses that same
# folder — so WhatsApp Web / YouTube stay logged in between runs,
# and you can keep separate named profiles (e.g. "work", "personal")
# if you ever want to switch.

CHROME_PROFILES_BASE_DIR = r"C:\AI\jarvis_chrome_profiles"
CHROME_PROFILE_CONFIG_FILE = os.path.join(CHROME_PROFILES_BASE_DIR, "active_profile.txt")

_driver = None


def _ensure_profiles_dir():
    os.makedirs(CHROME_PROFILES_BASE_DIR, exist_ok=True)


def list_chrome_profiles():
    _ensure_profiles_dir()
    return sorted(
        name for name in os.listdir(CHROME_PROFILES_BASE_DIR)
        if os.path.isdir(os.path.join(CHROME_PROFILES_BASE_DIR, name))
    )


def get_active_chrome_profile():
    _ensure_profiles_dir()

    if not os.path.exists(CHROME_PROFILE_CONFIG_FILE):
        return None

    try:
        with open(CHROME_PROFILE_CONFIG_FILE, "r") as file:
            name = file.read().strip()
            return name or None
    except Exception:
        return None


def set_active_chrome_profile(name):
    global _driver

    name = name.strip()

    if name == "":
        return "Please give the profile a name, e.g. 'jarvis' or 'personal'."

    _ensure_profiles_dir()
    profile_dir = os.path.join(CHROME_PROFILES_BASE_DIR, name)
    os.makedirs(profile_dir, exist_ok=True)

    with open(CHROME_PROFILE_CONFIG_FILE, "w") as file:
        file.write(name)

    # Force a fresh browser on the next check, using the new profile.
    if _driver is not None:
        try:
            _driver.quit()
        except Exception:
            pass
        _driver = None

    return (
        f"Chrome profile set to '{name}'. The next time I check "
        f"WhatsApp or YouTube, Chrome will open using this profile — "
        f"you'll need to log in once, then it stays logged in."
    )


def _ensure_chrome_profile_configured():
    """
    One-time interactive setup: if no profile has been chosen yet,
    ask for a name right here in the console before opening Chrome.
    Safe to call every time — it's a no-op once a profile exists.
    """
    existing = get_active_chrome_profile()

    if existing:
        return existing

    print()
    print("=" * 60)
    print("CHROME PROFILE SETUP (one-time)")
    print("=" * 60)
    print(
        "I haven't got a Chrome profile set up for browser checks yet.\n"
        "This keeps you logged into WhatsApp Web / YouTube between runs,\n"
        "instead of asking you to log in every single time."
    )

    try:
        name = input("Enter a name for this profile (e.g. 'jarvis'): ").strip()
    except Exception:
        name = ""

    if name == "":
        name = "default"

    set_active_chrome_profile(name)
    print(f"Using Chrome profile: {name}")
    print("=" * 60)

    return name


def _get_driver(force_new=False):
    global _driver

    if _driver is not None and not force_new:
        return _driver

    if _driver is not None and force_new:
        try:
            _driver.quit()
        except Exception:
            pass
        _driver = None

    profile_name = _ensure_chrome_profile_configured()
    profile_dir = os.path.join(CHROME_PROFILES_BASE_DIR, profile_name)

    from selenium import webdriver
    from selenium.webdriver.chrome.options import Options

    options = Options()
    options.add_argument(f"--user-data-dir={profile_dir}")

    _driver = webdriver.Chrome(options=options)
    return _driver


def check_notifications(service_name):
    """
    Best-effort notification check for a known service. Returns a
    plain-English string describing what was found (or why it couldn't
    check). Never raises — callers can treat the return value as the
    final spoken/printed response. Automatically recovers once if the
    browser window was closed or crashed since the last check.
    """
    service_name = service_name.strip().lower()
    url = NOTIFICATION_SITES.get(service_name)

    if url is None:
        return (
            f"I don't know how to check '{service_name}' yet. "
            f"Add it to NOTIFICATION_SITES in automation_engine.py."
        )

    import time
    from selenium.common.exceptions import WebDriverException

    for attempt in (1, 2):
        try:
            driver = _get_driver(force_new=(attempt == 2))
            driver.get(url)
            time.sleep(5)  # crude wait for the page/login state to settle

            if service_name == "whatsapp":
                unread_chats = driver.find_elements(
                    "xpath",
                    "//span[contains(@aria-label, 'unread message')]",
                )

                if not unread_chats:
                    return "No new WhatsApp messages."

                return (
                    f"You have unread WhatsApp messages in "
                    f"{len(unread_chats)} chat(s)."
                )

            # No specific selector written yet for this service — we
            # still opened the page, so say so rather than pretending
            # we checked.
            return (
                f"Opened {service_name}, but I don't have a notification "
                f"check written for it yet."
            )

        except WebDriverException as error:
            if attempt == 1:
                # Browser was likely closed/crashed since last time —
                # drop the dead driver and try once more with a fresh one.
                continue

            return (
                f"Couldn't check {service_name}: the browser window "
                f"wasn't available and restarting it didn't help "
                f"({getattr(error, 'msg', error)}). Make sure selenium "
                f"is installed and you've logged into {service_name} "
                f"at least once in this profile."
            )

        except Exception as error:
            return (
                f"Couldn't check {service_name}: {error}. "
                f"Make sure selenium is installed and you've logged "
                f"into {service_name} at least once in this profile."
            )