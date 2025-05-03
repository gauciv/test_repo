# .github/scripts/gitflow.py
#!/usr/bin/env python3
import os
import re
import platform
import sys
import argparse
from git import Repo, GitCommandError

# ANSI color codes
GREEN = '\033[92m'
YELLOW = '\033[93m'
RED = '\033[91m'
CYAN = '\033[96m'
RESET = '\033[0m'

# ----------------------------------------
# Validators & Prompts
# ----------------------------------------
def valid_branch(name: str) -> bool:
    return bool(re.match(r'^(?!/|.*([~^:\?\*\[\\])).+(?<!/)$', name))

def prompt_branch(repo, arg_branch=None):
    print(f"\n{CYAN}###### Branch Setup ######{RESET}")
    if arg_branch:
        if not valid_branch(arg_branch):
            print(f"{RED}[Error]{RESET} Invalid branch name: {arg_branch}")
            sys.exit(1)
        return arg_branch
    while True:
        name = input(f"{CYAN}+ Enter branch name:{RESET} ").strip()
        if not valid_branch(name):
            print(f"{YELLOW}[Warning]{RESET} Illegal branch name. Avoid spaces or ~ ^ : ? * [ \\ and no leading/trailing '/'.")
            continue
        return name

def prompt_commit_msg(arg_msg=None):
    print(f"\n{CYAN}###### Commit Setup ######{RESET}")
    if arg_msg:
        return arg_msg
    while True:
        msg = input(f"{CYAN}+ Enter commit message:{RESET} ").strip()
        if not msg:
            print(f"{YELLOW}[Warning]{RESET} Commit message cannot be empty.")
            continue
        confirm = input(f"{CYAN}? Confirm message [y/N]:{RESET} ").lower()
        if confirm.startswith('y'):
            return msg
        
def clear_screen():
    if platform.system() == "Windows":
        os.system("cls")  # Command for clearing the screen on Windows
    else:
        os.system("clear")  # Command for clearing the screen on Linux/macOS

# ----------------------------------------
# Main Workflow
# ----------------------------------------
def main():
    clear_screen()
    parser = argparse.ArgumentParser(
        description=f"{CYAN}=== Gitflow Automation ==={RESET}",
        formatter_class=argparse.RawTextHelpFormatter
    )
    parser.add_argument("--branch", "-b", help="Branch name to create/use")
    parser.add_argument("--message", "-m", help="Commit message to use")
    args = parser.parse_args()

    # Open repo
    try:
        repo = Repo('.', search_parent_directories=True)
    except Exception:
        print(f"{RED}[Error]{RESET} Not a git repository.")
        sys.exit(1)

    # Banner
    print(f"\n{CYAN}{'='*10} Starting Gitflow {'='*10}{RESET}\n")

    # 1. Branch Creation & Checkout
    branch = prompt_branch(repo, args.branch)
    try:
        repo.git.checkout('-b', branch)
        print(f"{GREEN}[OK]{RESET} Switched to branch: {branch}")
    except GitCommandError:
        try:
            repo.git.checkout(branch)
            print(f"{GREEN}[OK]{RESET} Checked out existing branch: {branch}")
        except GitCommandError as e:
            print(f"{RED}[Error]{RESET} Could not checkout branch: {e}")
            sys.exit(1)

    # 2. Stage Changes
    try:
        repo.git.add('--all')
        print(f"{GREEN}[OK]{RESET} Staged all changes")
    except GitCommandError as e:
        print(f"{RED}[Error]{RESET} Staging failed: {e}")
        sys.exit(1)

    # 3. Commit
    msg = prompt_commit_msg(args.message)
    try:
        repo.git.commit('-m', msg)
        print(f"{GREEN}[OK]{RESET} Committed: '{msg}'")
    except GitCommandError as e:
        print(f"{RED}[Error]{RESET} Commit failed: {e}")
        sys.exit(1)

    # 5. Push Feature Branch
    try:
        origin = repo.remote('origin')
        origin.push(branch)
        print(f"{GREEN}[OK]{RESET} Pushed '{branch}' to origin")
    except GitCommandError as e:
        print(f"{RED}[Error]{RESET} Push failed: {e}")
        sys.exit(1)

    # Done
    print(f"\n{CYAN}{'='*10} Gitflow Complete {'='*10}{RESET}\n")

if __name__ == "__main__":
    main()
