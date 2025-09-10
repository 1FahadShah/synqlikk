# cli/main.py
import sys
from colorama import init, Fore
from cli import menus, tasks, notes, expenses, sync, utils
from cli.auth import login, register, is_authenticated, clear_session

init(autoreset=True)

def main_menu():
    """Display main menu after login."""
    while True:
        print(Fore.CYAN + "\n=== SynQlikk Main Menu ===")
        print("1. Tasks")
        print("2. Notes")
        print("3. Expenses")
        print("4. Sync with Server")
        print("5. Logout / Exit")

        choice = input(Fore.YELLOW + "Select an option: ").strip()

        if choice == "1":
            menus.tasks_menu()
        elif choice == "2":
            menus.notes_menu()
        elif choice == "3":
            menus.expenses_menu()
        elif choice == "4":
            print(Fore.GREEN + "🔄 Syncing with server...")
            sync.sync_all()
        elif choice == "5":
            if is_authenticated():
                print(Fore.GREEN + "🔄 Syncing final changes before logout...")
                sync.sync_all()
            print(Fore.RED + "🚪 Logging out...")
            clear_session()
            sys.exit(0)
        else:
            print(Fore.RED + "❌ Invalid choice, try again!")

def auth_menu():
    """Display login/register menu."""
    while True:
        print(Fore.MAGENTA + "\n=== SynQlikk Authentication ===")
        print("1. Login")
        print("2. Register")
        print("3. Exit")

        choice = input(Fore.YELLOW + "Select an option: ").strip()

        if choice == "1":
            username = input("Username: ").strip()
            password = input("Password: ").strip()
            try:
                login(username, password)  # Full sync handled inside login
                break
            except Exception as e:
                print(Fore.RED + f"❌ {e}")
        elif choice == "2":
            username = input("Username: ").strip()
            password = input("Password: ").strip()
            try:
                register(username, password)  # Full sync handled inside register
                break
            except Exception as e:
                print(Fore.RED + f"❌ {e}")
        elif choice == "3":
            print(Fore.RED + "Exiting CLI...")
            sys.exit(0)
        else:
            print(Fore.RED + "❌ Invalid choice!")

if __name__ == "__main__":
    # --- NEW UPDATE ---
    # Initialize the local DB once at the start
    utils.initialize_local_db()

    try:
        if is_authenticated():
            print(Fore.CYAN + "🔄 Syncing all server records to local DB...")
            sync.sync_all(force_full=True)  # Full sync even if session exists
            main_menu()
        else:
            auth_menu()
            main_menu()
    except KeyboardInterrupt:
        # Handle Ctrl+C exit
        print(Fore.YELLOW + "\n\n⚡ Exit detected (Ctrl+C).")
        if is_authenticated():
            print(Fore.GREEN + "🔄 Syncing final changes before exit...")
            sync.sync_all()
        print(Fore.CYAN + "Goodbye!")
        sys.exit(0)
    except Exception as e:
        print(Fore.RED + f"\nAn unexpected error occurred: {e}")
        sys.exit(1)
