# ==========================================================
# JARVIS AI
# CODE ENGINE
# Python 3.12
# ==========================================================
#
# Detects, from a plain-English sentence:
#   1. WHAT the user wants (concept)      -> e.g. "for loop"
#   2. WHERE / in what (language/platform) -> e.g. "python"
#
# Then looks the pair up in code_kb.py and returns the
# matching snippet. No LLM, no API, no training needed —
# this is pure keyword lookup, same idea as triggers.py.
#
# TO ADD MORE MATCHING PHRASES: edit the keyword lists below.
# TO ADD MORE CODE: edit code_kb.py instead.
# ==========================================================

from code_kb import CODE_KB, PLATFORM_CMDS


# ==========================================================
# LANGUAGE KEYWORDS
# ==========================================================

LANGUAGE_KEYWORDS = {
    "python": ["python", "py"],
    "java": ["java"],
    "cpp": ["c++", "cpp", "c plus plus"],
    "javascript": ["javascript", "js", "node", "nodejs"],
    "bash": ["bash", "shell script", "linux script", "sh script"],
    "powershell": ["powershell", "ps1"],
    "sql": ["sql", "mysql", "postgresql", "database query"],
}


# ==========================================================
# PLATFORM KEYWORDS (for OS / networking commands)
# ==========================================================

PLATFORM_KEYWORDS = {
    "android_adb": ["android", "adb"],
    "mac": ["mac", "macos", "apple os", "osx"],
    "powershell": ["powershell", "ps1"],
    "windows_cmd": ["cmd", "command prompt", "windows"],
    "linux": ["linux", "ubuntu", "debian", "fedora"],
}


# ==========================================================
# CONCEPT KEYWORDS -> CODE_KB key
# ==========================================================

CONCEPT_KEYWORDS = {
    "print_hello": ["print hello", "hello world"],
    "variable_declaration": ["declare a variable", "variable declaration", "create a variable"],
    "for_loop": ["for loop"],
    "while_loop": ["while loop"],
    "if_else": ["if else", "if condition", "conditional statement"],
    "function_definition": ["define a function", "write a function", "function definition"],
    "list_array": ["a list", "an array", "array of", "list in python", "list in java"],
    "read_file": ["read a file", "read file"],
    "write_file": ["write a file", "write to file", "write file"],
    "try_catch": ["try catch", "exception handling", "error handling"],
    "class_definition": ["define a class", "class definition", "write a class"],
    "select_query": ["select query", "fetch data", "get data from table"],
    "insert_query": ["insert query", "insert data", "add data to table"],
}


# ==========================================================
# PLATFORM-COMMAND KEYWORDS -> PLATFORM_CMDS key
# ==========================================================

PLATFORM_TASK_KEYWORDS = {
    "list_files": ["list files", "show files"],
    "current_directory": ["current directory", "where am i", "current folder"],
    "change_directory": ["change directory", "go to folder"],
    "create_directory": ["create a folder", "create directory", "make folder"],
    "copy_file": ["copy a file", "copy file"],
    "move_rename_file": ["rename a file", "move a file", "rename file"],
    "delete_file": ["delete a file", "remove a file", "delete file"],
    "check_ip": ["check ip", "my ip address", "show ip"],
    "ping_host": ["ping"],
    "check_port": ["check port", "is port open"],
    "process_list": ["list processes", "running processes", "show processes"],
    "kill_process": ["kill process", "stop process", "end process"],
    "disk_usage": ["disk usage", "disk space", "storage space"],
    "environment_variables": ["environment variables", "env variables"],
    "list_installed_packages": ["installed packages", "installed software"],
    "wifi_networks": ["wifi networks", "available wifi", "scan wifi"],
    "install_package": ["install package", "install software"],
    "list_android_devices": ["connected android devices", "list android devices"],
    "install_apk": ["install apk", "install app on android"],
    "android_screenshot": ["android screenshot", "screenshot android device"],
    "dns_lookup": ["dns lookup", "resolve domain", "nslookup"],
    "traceroute": ["traceroute", "trace route", "trace the route"],
    "hostname": ["my hostname", "computer name", "show hostname"],
    "mac_address": ["mac address"],
    "active_connections": ["active connections", "show connections", "netstat"],
    "default_gateway": ["default gateway", "gateway ip", "my gateway"],
    "dns_flush": ["flush dns", "clear dns cache"],
    "arp_table": ["arp table", "show arp"],
    "firewall_status": ["firewall status", "is firewall on", "check firewall"],
    "whois_lookup": ["whois", "who owns this domain", "domain info"],
    "public_ip": ["public ip", "my public ip", "external ip"],
    "network_interfaces_detailed": ["network interfaces", "show network adapters", "list interfaces"],
}


# ==========================================================
# TASKS SAFE TO ACTUALLY RUN AUTOMATICALLY
# (read-only / diagnostic — nothing here deletes, kills,
# installs, or changes state)
# ==========================================================

SAFE_TASKS = {
    "list_files", "current_directory", "check_ip", "ping_host",
    "check_port", "process_list", "disk_usage", "environment_variables",
    "list_installed_packages", "wifi_networks", "list_android_devices",
    "dns_lookup", "traceroute", "hostname", "mac_address",
    "active_connections", "default_gateway", "dns_flush", "arp_table",
    "firewall_status", "whois_lookup", "public_ip",
    "network_interfaces_detailed",
}

# Tasks whose command template needs a {host} filled in
HOST_TASKS = {"ping_host", "dns_lookup", "traceroute", "whois_lookup"}

# Words that signal the user wants it ACTUALLY RUN, not just shown
RUN_INTENT_WORDS = [
    "run ", "execute ", "actually run", "do it now", "run it",
    "run this", "check now", "run the command",
]


# ==========================================================
# HELPER — find first keyword match in a dict
# ==========================================================

def _match_keywords(command, keyword_map):
    for key, phrases in keyword_map.items():
        for phrase in phrases:
            if phrase in command:
                return key
    return None


# ==========================================================
# DOES THE USER WANT IT ACTUALLY RUN (not just shown)?
# ==========================================================

def wants_execution(command):
    return any(word in command for word in RUN_INTENT_WORDS)


# ==========================================================
# ACTUALLY EXECUTE A SAFE DIAGNOSTIC COMMAND
# ==========================================================
# Returns real command output if this is a run-intent request
# for a SAFE task, otherwise returns None so brain.py can fall
# through to the text-snippet response instead.

def try_execute(command):
    command = command.lower().strip()

    if not wants_execution(command):
        return None

    task = _match_keywords(command, PLATFORM_TASK_KEYWORDS)

    if task is None or task not in SAFE_TASKS:
        return None

    platform_key = _match_keywords(command, PLATFORM_KEYWORDS)

    import network_runner

    if platform_key is None:
        platform_key = network_runner.get_current_platform()

    template = PLATFORM_CMDS.get(task, {}).get(platform_key)

    if template is None:
        return (
            f"I don't have a runnable command for {task.replace('_', ' ')} "
            f"on {platform_key} yet."
        )

    if task in HOST_TASKS:
        host = network_runner.extract_host(command)
        cmd_str = template.format(host=host)
    else:
        cmd_str = template

    output = network_runner.run_shell_command(cmd_str)

    return f"Ran: {cmd_str}\n\n{output}"


# ==========================================================
# MAIN ENTRY POINT — call this from brain.py
# ==========================================================
# Returns a formatted code snippet string, or None if nothing
# matched (so brain.py can fall through to its other checks).

def get_code_response(command):
    command = command.lower().strip()

    # ------------------------------------------------------
    # Try OS / networking command first (more specific phrases)
    # ------------------------------------------------------
    task = _match_keywords(command, PLATFORM_TASK_KEYWORDS)

    if task is not None:
        platform = _match_keywords(command, PLATFORM_KEYWORDS)

        if platform is None:
            platform = "linux"  # default platform if not mentioned

        snippet = PLATFORM_CMDS.get(task, {}).get(platform)

        if snippet is not None:
            return f"Here's how to {task.replace('_', ' ')} on {platform}:\n\n{snippet}"

        available = ", ".join(PLATFORM_CMDS.get(task, {}).keys())
        return (
            f"I don't have a command for {task.replace('_', ' ')} on {platform} yet. "
            f"Available platforms for this: {available}."
        )

    # ------------------------------------------------------
    # Try programming-language concept next
    # ------------------------------------------------------
    concept = _match_keywords(command, CONCEPT_KEYWORDS)

    if concept is not None:
        language = _match_keywords(command, LANGUAGE_KEYWORDS)

        if language is None:
            language = "python"  # default language if not mentioned

        snippet = CODE_KB.get(concept, {}).get(language)

        if snippet is not None:
            return f"Here's {concept.replace('_', ' ')} in {language}:\n\n{snippet}"

        available = ", ".join(CODE_KB.get(concept, {}).keys())
        return (
            f"I don't have {concept.replace('_', ' ')} in {language} yet. "
            f"Available languages for this: {available}."
        )

    return None