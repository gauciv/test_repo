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
MAGENTA = '\033[95m'

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

def fetch_and_pull(repo):
    print(f"\n{MAGENTA}###### Fetching Remote Changes ######{RESET}")
    try:
        origin = repo.remote('origin')
        origin.fetch()
        print(f"{GREEN}[OK]{RESET} Fetched latest changes from remote.")

        # Check if there are changes on the remote
        remote_diff = repo.git.log('HEAD..origin/main', '--oneline')
        if remote_diff:
            print(f"{CYAN}[Info]{RESET} Changes detected on the remote repository.")
            
            # Check if the working tree is clean
            if repo.is_dirty(untracked_files=True):
                print(f"{YELLOW}[Warning]{RESET} Local changes detected. Stashing changes before pulling.")
                repo.git.stash('save', '--include-untracked')
                
                # Pull changes from the remote
                repo.git.pull('origin', 'main')
                print(f"{GREEN}[OK]{RESET} Pulled latest changes into 'main'.")

                # Pop the stash if it was created
                if repo.git.stash('list'):
                    print(f"{CYAN}[Info]{RESET} Restoring stashed changes.")
                    repo.git.stash('pop')
        else:
            # Check if the working tree is clean
            if not repo.is_dirty(untracked_files=True):
                print(f"{YELLOW}[Notice]{RESET} No changes on the remote and the working tree is clean.")
                print(f"{CYAN}[Info]{RESET} Please make some changes before running the script again.")
                sys.exit(0)
            else:
                print(f"{CYAN}[Info]{RESET} No changes detected on the remote. Proceeding with the script.")
    except GitCommandError as e:
        print(f"{RED}[Error]{RESET} Fetch/Pull failed: {e}")
        sys.exit(1)

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

    # Fetch and pull changes
    fetch_and_pull(repo)
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
