# cli/menus.py
from colorama import Fore, Style
from cli import tasks, notes, expenses

def tasks_menu():
    """Menu for tasks CRUD operations"""
    while True:
        print(Fore.CYAN + "\n=== Tasks Menu ===")
        print("1. View Tasks")
        print("2. Add Task")
        print("3. Edit Task")
        print("4. Delete Task")
        print("5. Back to Main Menu")

        choice = input(Fore.YELLOW + "Select an option: ").strip()

        if choice == "1":
            tasks.view_tasks()
        elif choice == "2":
            tasks.add_task()
        elif choice == "3":
            tasks.edit_task()
        elif choice == "4":
            tasks.delete_task()
        elif choice == "5":
            break
        else:
            print(Fore.RED + "❌ Invalid choice!")

def notes_menu():
    """Menu for notes CRUD operations"""
    while True:
        print(Fore.CYAN + "\n=== Notes Menu ===")
        print("1. View Notes")
        print("2. Add Note")
        print("3. Edit Note")
        print("4. Delete Note")
        print("5. Back to Main Menu")

        choice = input(Fore.YELLOW + "Select an option: ").strip()

        if choice == "1":
            notes.view_notes()
        elif choice == "2":
            notes.add_note()
        elif choice == "3":
            notes.edit_note()
        elif choice == "4":
            notes.delete_note()
        elif choice == "5":
            break
        else:
            print(Fore.RED + "❌ Invalid choice!")

def expenses_menu():
    """Menu for expenses CRUD operations"""
    while True:
        print(Fore.CYAN + "\n=== Expenses Menu ===")
        print("1. View Expenses")
        print("2. Add Expense")
        print("3. Edit Expense")
        print("4. Delete Expense")
        print("5. Back to Main Menu")

        choice = input(Fore.YELLOW + "Select an option: ").strip()

        if choice == "1":
            expenses.view_expenses()
        elif choice == "2":
            expenses.add_expense()
        elif choice == "3":
            expenses.edit_expense()
        elif choice == "4":
            expenses.delete_expense()
        elif choice == "5":
            break
        else:
            print(Fore.RED + "❌ Invalid choice!")
