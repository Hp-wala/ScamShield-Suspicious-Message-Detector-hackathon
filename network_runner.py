# ==========================================================
# JARVIS AI
# NETWORK / SYSTEM COMMAND RUNNER
# Python 3.12
# ==========================================================
#
# Actually EXECUTES a shell command on the machine Jarvis is
# running on and returns real output. Used only for read-only
# diagnostic commands (SAFE_TASKS in code_engine.py) — nothing
# here deletes, kills, or installs anything.
# ==========================================================

import subprocess
import platform
import re


# ==========================================================
# DETECT CURRENT PLATFORM (so Jarvis runs the RIGHT command
# for whatever machine it's actually on, not a guess)
# ==========================================================

def get_current_platform():
    system = platform.system().lower()

    if system == "windows":
        return "windows_cmd"

    if system == "darwin":
        return "mac"

    return "linux"


# ==========================================================
# EXTRACT A HOST / DOMAIN / IP FROM THE USER'S SENTENCE
# ==========================================================
# e.g. "ping google.com" -> "google.com"
#      "run traceroute to 8.8.8.8" -> "8.8.8.8"
# Falls back to a safe default if nothing is found.

def extract_host(command, default="google.com"):
    ip_match = re.search(r"\b\d{1,3}(?:\.\d{1,3}){3}\b", command)

    if ip_match:
        return ip_match.group(0)

    domain_match = re.search(r"\b[a-zA-Z0-9-]+\.[a-zA-Z]{2,}\b", command)

    if domain_match:
        return domain_match.group(0)

    return default


# ==========================================================
# RUN A SHELL COMMAND AND RETURN ITS OUTPUT
# ==========================================================

def run_shell_command(command_str, timeout=15):
    try:
        result = subprocess.run(
            command_str,
            shell=True,
            capture_output=True,
            text=True,
            timeout=timeout,
        )

        output = (result.stdout or "").strip()
        error = (result.stderr or "").strip()

        if result.returncode != 0 and not output:
            return f"Command did not succeed:\n{error or 'No error message returned.'}"

        return output if output else "Command ran with no output."

    except subprocess.TimeoutExpired:
        return "Command timed out."

    except FileNotFoundError:
        return "That command or tool isn't available on this system."

    except Exception as error:
        return f"Error running command: {error}"