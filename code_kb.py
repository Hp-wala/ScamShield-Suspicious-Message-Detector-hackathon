# ==========================================================
# JARVIS AI
# CODE KNOWLEDGE BASE
# Python 3.12
# ==========================================================
#
# HOW THIS WORKS
# --------------
# Two dictionaries:
#
# 1. CODE_KB       -> programming concepts (loops, functions,
#                      variables etc.) with the same concept
#                      written in different languages.
#
# 2. PLATFORM_CMDS -> OS / networking commands (list files,
#                      check ip, ping etc.) with the same task
#                      written for different platforms.
#
# TO ADD MORE: just add a new key with a dict of
# {language_or_platform: snippet}. You don't need every
# language for every concept — only add what you know.
#
# Example:
#
#   "reverse_string": {
#       "python": "text[::-1]",
#       "java": "new StringBuilder(text).reverse().toString();",
#   },
#
# ==========================================================


# ==========================================================
# PROGRAMMING LANGUAGE FUNDAMENTALS
# ==========================================================

CODE_KB = {

    "print_hello": {
        "python": 'print("Hello, World!")',
        "java": (
            "public class Main {\n"
            "    public static void main(String[] args) {\n"
            '        System.out.println("Hello, World!");\n'
            "    }\n"
            "}"
        ),
        "cpp": (
            "#include <iostream>\n"
            "int main() {\n"
            '    std::cout << "Hello, World!";\n'
            "    return 0;\n"
            "}"
        ),
        "javascript": 'console.log("Hello, World!");',
        "bash": 'echo "Hello, World!"',
        "powershell": 'Write-Host "Hello, World!"',
        "sql": "SELECT 'Hello, World!';",
    },

    "variable_declaration": {
        "python": 'name = "Ritul"\nage = 21',
        "java": 'String name = "Ritul";\nint age = 21;',
        "cpp": 'std::string name = "Ritul";\nint age = 21;',
        "javascript": 'let name = "Ritul";\nlet age = 21;',
        "bash": 'name="Ritul"\nage=21',
        "powershell": '$name = "Ritul"\n$age = 21',
    },

    "for_loop": {
        "python": "for i in range(10):\n    print(i)",
        "java": "for (int i = 0; i < 10; i++) {\n    System.out.println(i);\n}",
        "cpp": "for (int i = 0; i < 10; i++) {\n    std::cout << i << std::endl;\n}",
        "javascript": "for (let i = 0; i < 10; i++) {\n    console.log(i);\n}",
        "bash": 'for i in {1..10}; do\n    echo "$i"\ndone',
        "powershell": "for ($i = 0; $i -lt 10; $i++) {\n    Write-Host $i\n}",
    },

    "while_loop": {
        "python": "i = 0\nwhile i < 10:\n    print(i)\n    i += 1",
        "java": "int i = 0;\nwhile (i < 10) {\n    System.out.println(i);\n    i++;\n}",
        "cpp": "int i = 0;\nwhile (i < 10) {\n    std::cout << i;\n    i++;\n}",
        "javascript": "let i = 0;\nwhile (i < 10) {\n    console.log(i);\n    i++;\n}",
        "bash": 'i=0\nwhile [ $i -lt 10 ]; do\n    echo "$i"\n    i=$((i+1))\ndone',
        "powershell": "$i = 0\nwhile ($i -lt 10) {\n    Write-Host $i\n    $i++\n}",
    },

    "if_else": {
        "python": 'if age >= 18:\n    print("Adult")\nelse:\n    print("Minor")',
        "java": 'if (age >= 18) {\n    System.out.println("Adult");\n} else {\n    System.out.println("Minor");\n}',
        "cpp": 'if (age >= 18) {\n    std::cout << "Adult";\n} else {\n    std::cout << "Minor";\n}',
        "javascript": 'if (age >= 18) {\n    console.log("Adult");\n} else {\n    console.log("Minor");\n}',
        "bash": 'if [ $age -ge 18 ]; then\n    echo "Adult"\nelse\n    echo "Minor"\nfi',
        "powershell": 'if ($age -ge 18) {\n    Write-Host "Adult"\n} else {\n    Write-Host "Minor"\n}',
    },

    "function_definition": {
        "python": "def add(a, b):\n    return a + b",
        "java": "public static int add(int a, int b) {\n    return a + b;\n}",
        "cpp": "int add(int a, int b) {\n    return a + b;\n}",
        "javascript": "function add(a, b) {\n    return a + b;\n}",
        "bash": "add() {\n    echo $(( $1 + $2 ))\n}",
        "powershell": "function Add($a, $b) {\n    return $a + $b\n}",
    },

    "list_array": {
        "python": 'items = ["apple", "banana", "mango"]\nitems.append("grape")',
        "java": 'List<String> items = new ArrayList<>(Arrays.asList("apple", "banana", "mango"));\nitems.add("grape");',
        "cpp": 'std::vector<std::string> items = {"apple", "banana", "mango"};\nitems.push_back("grape");',
        "javascript": 'let items = ["apple", "banana", "mango"];\nitems.push("grape");',
        "bash": 'items=("apple" "banana" "mango")\nitems+=("grape")',
        "powershell": '$items = @("apple", "banana", "mango")\n$items += "grape"',
    },

    "read_file": {
        "python": 'with open("file.txt", "r") as f:\n    content = f.read()',
        "java": "String content = new String(Files.readAllBytes(Paths.get(\"file.txt\")));",
        "cpp": '#include <fstream>\nstd::ifstream file("file.txt");\nstd::string line;\nwhile (std::getline(file, line)) { }',
        "javascript": 'const fs = require("fs");\nconst content = fs.readFileSync("file.txt", "utf8");',
        "bash": 'content=$(cat file.txt)',
        "powershell": '$content = Get-Content "file.txt"',
    },

    "write_file": {
        "python": 'with open("file.txt", "w") as f:\n    f.write("Hello")',
        "java": 'Files.write(Paths.get("file.txt"), "Hello".getBytes());',
        "cpp": '#include <fstream>\nstd::ofstream file("file.txt");\nfile << "Hello";',
        "javascript": 'const fs = require("fs");\nfs.writeFileSync("file.txt", "Hello");',
        "bash": 'echo "Hello" > file.txt',
        "powershell": 'Set-Content "file.txt" -Value "Hello"',
    },

    "try_catch": {
        "python": 'try:\n    risky()\nexcept Exception as e:\n    print(e)',
        "java": "try {\n    risky();\n} catch (Exception e) {\n    System.out.println(e);\n}",
        "cpp": "try {\n    risky();\n} catch (const std::exception& e) {\n    std::cout << e.what();\n}",
        "javascript": "try {\n    risky();\n} catch (e) {\n    console.log(e);\n}",
        "bash": 'risky() || echo "Error occurred"',
        "powershell": "try {\n    Risky\n} catch {\n    Write-Host $_.Exception.Message\n}",
    },

    "class_definition": {
        "python": 'class Person:\n    def __init__(self, name):\n        self.name = name',
        "java": "class Person {\n    String name;\n    Person(String name) {\n        this.name = name;\n    }\n}",
        "cpp": "class Person {\npublic:\n    std::string name;\n    Person(std::string n) : name(n) {}\n};",
        "javascript": "class Person {\n    constructor(name) {\n        this.name = name;\n    }\n}",
    },

    "select_query": {
        "sql": "SELECT column1, column2 FROM table_name WHERE condition;",
    },

    "insert_query": {
        "sql": "INSERT INTO table_name (col1, col2) VALUES (val1, val2);",
    },
}


# ==========================================================
# OS / NETWORKING COMMANDS
# ==========================================================

PLATFORM_CMDS = {

    "list_files": {
        "linux": "ls -la",
        "mac": "ls -la",
        "windows_cmd": "dir",
        "powershell": "Get-ChildItem",
        "android_adb": "adb shell ls",
    },

    "current_directory": {
        "linux": "pwd",
        "mac": "pwd",
        "windows_cmd": "cd",
        "powershell": "Get-Location",
        "android_adb": "adb shell pwd",
    },

    "change_directory": {
        "linux": "cd /path/to/folder",
        "mac": "cd /path/to/folder",
        "windows_cmd": "cd C:\\path\\to\\folder",
        "powershell": "Set-Location C:\\path\\to\\folder",
    },

    "create_directory": {
        "linux": "mkdir new_folder",
        "mac": "mkdir new_folder",
        "windows_cmd": "mkdir new_folder",
        "powershell": "New-Item -ItemType Directory -Name new_folder",
    },

    "copy_file": {
        "linux": "cp source.txt destination.txt",
        "mac": "cp source.txt destination.txt",
        "windows_cmd": "copy source.txt destination.txt",
        "powershell": "Copy-Item source.txt destination.txt",
    },

    "move_rename_file": {
        "linux": "mv old_name.txt new_name.txt",
        "mac": "mv old_name.txt new_name.txt",
        "windows_cmd": "move old_name.txt new_name.txt",
        "powershell": "Move-Item old_name.txt new_name.txt",
    },

    "delete_file": {
        "linux": "rm file.txt",
        "mac": "rm file.txt",
        "windows_cmd": "del file.txt",
        "powershell": "Remove-Item file.txt",
    },

    "check_ip": {
        "linux": "ip addr show",
        "mac": "ifconfig",
        "windows_cmd": "ipconfig",
        "powershell": "Get-NetIPAddress",
        "android_adb": "adb shell ip addr show wlan0",
    },

    "ping_host": {
        "linux": "ping -c 4 {host}",
        "mac": "ping -c 4 {host}",
        "windows_cmd": "ping {host}",
        "powershell": "Test-Connection {host}",
    },

    "check_port": {
        "linux": "netstat -tuln | grep 8080",
        "mac": "lsof -i :8080",
        "windows_cmd": "netstat -ano | findstr 8080",
        "powershell": "Test-NetConnection -ComputerName localhost -Port 8080",
    },

    "dns_lookup": {
        "linux": "nslookup {host}",
        "mac": "nslookup {host}",
        "windows_cmd": "nslookup {host}",
        "powershell": "Resolve-DnsName {host}",
    },

    "traceroute": {
        "linux": "traceroute {host}",
        "mac": "traceroute {host}",
        "windows_cmd": "tracert {host}",
        "powershell": "Test-NetConnection {host} -TraceRoute",
    },

    "hostname": {
        "linux": "hostname",
        "mac": "hostname",
        "windows_cmd": "hostname",
        "powershell": "$env:COMPUTERNAME",
    },

    "mac_address": {
        "linux": "ip link show | grep ether",
        "mac": "ifconfig en0 | grep ether",
        "windows_cmd": "getmac",
        "powershell": "Get-NetAdapter | Select-Object Name,MacAddress",
    },

    "active_connections": {
        "linux": "netstat -tuln",
        "mac": "netstat -an",
        "windows_cmd": "netstat -an",
        "powershell": "Get-NetTCPConnection",
    },

    "default_gateway": {
        "linux": "ip route | grep default",
        "mac": "netstat -nr | grep default",
        "windows_cmd": "ipconfig | findstr Gateway",
        "powershell": "Get-NetRoute -DestinationPrefix 0.0.0.0/0",
    },

    "dns_flush": {
        "linux": "sudo systemd-resolve --flush-caches",
        "mac": "sudo dscacheutil -flushcache; sudo killall -HUP mDNSResponder",
        "windows_cmd": "ipconfig /flushdns",
        "powershell": "Clear-DnsClientCache",
    },

    "arp_table": {
        "linux": "arp -a",
        "mac": "arp -a",
        "windows_cmd": "arp -a",
        "powershell": "Get-NetNeighbor",
    },

    "firewall_status": {
        "linux": "sudo ufw status",
        "mac": "sudo /usr/libexec/ApplicationFirewall/socketfilterfw --getglobalstate",
        "windows_cmd": "netsh advfirewall show allprofiles",
        "powershell": "Get-NetFirewallProfile",
    },

    "whois_lookup": {
        "linux": "whois {host}",
        "mac": "whois {host}",
        "windows_cmd": "nslookup {host}",
        "powershell": "Resolve-DnsName {host}",
    },

    "public_ip": {
        "linux": "curl ifconfig.me",
        "mac": "curl ifconfig.me",
        "windows_cmd": "curl ifconfig.me",
        "powershell": "(Invoke-WebRequest -Uri 'ifconfig.me/ip').Content",
    },

    "network_interfaces_detailed": {
        "linux": "ip addr show",
        "mac": "ifconfig -a",
        "windows_cmd": "ipconfig /all",
        "powershell": "Get-NetIPConfiguration",
    },

    "process_list": {
        "linux": "ps aux",
        "mac": "ps aux",
        "windows_cmd": "tasklist",
        "powershell": "Get-Process",
        "android_adb": "adb shell ps",
    },

    "kill_process": {
        "linux": "kill -9 <pid>",
        "mac": "kill -9 <pid>",
        "windows_cmd": "taskkill /PID <pid> /F",
        "powershell": "Stop-Process -Id <pid> -Force",
    },

    "disk_usage": {
        "linux": "df -h",
        "mac": "df -h",
        "windows_cmd": "wmic logicaldisk get size,freespace,caption",
        "powershell": "Get-PSDrive -PSProvider FileSystem",
    },

    "environment_variables": {
        "linux": "printenv",
        "mac": "printenv",
        "windows_cmd": "set",
        "powershell": "Get-ChildItem Env:",
    },

    "list_installed_packages": {
        "linux": "dpkg -l   # Debian/Ubuntu\nrpm -qa   # RedHat/CentOS",
        "mac": "brew list",
        "windows_cmd": "wmic product get name",
        "powershell": "Get-Package",
    },

    "wifi_networks": {
        "linux": "nmcli device wifi list",
        "mac": "networksetup -listallhardwareports",
        "windows_cmd": "netsh wlan show networks",
        "powershell": "netsh wlan show networks",
    },

    "install_package": {
        "linux": "sudo apt install package_name   # Debian/Ubuntu\nsudo dnf install package_name  # Fedora",
        "mac": "brew install package_name",
        "windows_cmd": "winget install package_name",
        "powershell": "winget install package_name",
    },

    "list_android_devices": {
        "android_adb": "adb devices",
    },

    "install_apk": {
        "android_adb": "adb install app.apk",
    },

    "android_screenshot": {
        "android_adb": "adb shell screencap -p /sdcard/screen.png",
    },
}