import uuid
from colorama import init, Fore, Style

def generate_uuid():
    return str(uuid.uuid4())

init(autoreset=True)

def print_success(msg):
    print(Fore.GREEN + msg)

def print_info(msg):
    print(Fore.CYAN + msg)

def print_warning(msg):
    print(Fore.YELLOW + msg)

def print_error(msg):
    print(Fore.RED + msg)
