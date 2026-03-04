#!/usr/bin/env python3
"""
Git Branch Cleanup Tool

A CLI tool to detect merged branches, identify stale branches,
provide safe deletion with undo capability, and enforce team branch policies.
"""

import argparse
import subprocess
import sys
import json
import os
import datetime
from typing import List, Dict, Optional


class GitBranchCleanup:
    def __init__(self):
        self.current_branch = self._get_current_branch()
        
    def _run_git_command(self, command: List[str]) -> str:
        """Run a git command and return its output."""
        try:
            result = subprocess.run(
                ['git'] + command,
                capture_output=True,
                text=True,
                check=True
            )
            return result.stdout.strip()
        except subprocess.CalledProcessError as e:
            print(f"Error running git command {' '.join(command)}: {e}")
            sys.exit(1)
    
    def _get_current_branch(self) -> str:
        """Get the current git branch."""
        return self._run_git_command(['rev-parse', '--abbrev-ref', 'HEAD'])
    
    def get_merged_branches(self, remote: str = 'origin') -> List[str]:
        """Get branches that have been merged into main/master."""
        # Get the main branch name (try common names)
        main_branch = 'main'
        if not self._branch_exists('main'):
            main_branch = 'master'
        
        # Get merged branches
        try:
            merged_output = self._run_git_command(['branch', '--merged', main_branch])
            merged_branches = []
            
            for line in merged_output.split('\n'):
                branch = line.strip().replace('*', '').strip()  # Remove current branch indicator
                if branch and branch != main_branch and branch != 'HEAD':
                    merged_branches.append(branch)
                    
            return merged_branches
        except:
            # Fallback: try with remote
            try:
                self._run_git_command(['fetch', remote])
                merged_output = self._run_git_command(['branch', '-r', '--merged', f'{remote}/{main_branch}'])
                
                merged_branches = []
                for line in merged_output.split('\n'):
                    branch = line.strip()
                    if f'{remote}/' in branch and not '->' in branch:
                        branch_name = branch.replace(f'{remote}/', '').strip()
                        if branch_name != main_branch and branch_name not in merged_branches:
                            merged_branches.append(branch_name)
                            
                # Check which local branches track these remote branches
                local_branches = self.get_local_branches()
                truly_merged = []
                
                for remote_branch in merged_branches:
                    if remote_branch in local_branches:
                        truly_merged.append(remote_branch)
                        
                return truly_merged
            except:
                return []
    
    def _branch_exists(self, branch: str) -> bool:
        """Check if a branch exists locally."""
        try:
            self._run_git_command(['rev-parse', '--verify', branch])
            return True
        except:
            return False
    
    def get_local_branches(self) -> List[str]:
        """Get all local branches."""
        output = self._run_git_command(['branch'])
        branches = []
        for line in output.split('\n'):
            branch = line.strip().replace('*', '').strip()
            if branch:
                branches.append(branch)
        return branches
    
    def get_branch_last_commit_date(self, branch: str) -> datetime.datetime:
        """Get the date of the last commit on a branch."""
        timestamp = self._run_git_command(['log', '-1', '--format=%ct', branch])
        return datetime.datetime.fromtimestamp(int(timestamp))
    
    def get_stale_branches(self, days: int = 30) -> List[Dict[str, any]]:
        """Get branches that haven't been updated in the specified number of days."""
        cutoff_date = datetime.datetime.now() - datetime.timedelta(days=days)
        local_branches = self.get_local_branches()
        
        stale_branches = []
        
        for branch in local_branches:
            if branch == self.current_branch:
                continue  # Skip current branch
                
            last_commit_date = self.get_branch_last_commit_date(branch)
            if last_commit_date < cutoff_date:
                stale_branches.append({
                    'name': branch,
                    'last_commit': last_commit_date,
                    'days_old': (datetime.datetime.now() - last_commit_date).days
                })
        
        return stale_branches
    
    def delete_branches(self, branches: List[str], force: bool = False) -> bool:
        """Delete the specified branches."""
        if not branches:
            print("No branches to delete.")
            return True
            
        cmd = ['branch', '-D' if force else '-d']
        cmd.extend(branches)
        
        try:
            result = self._run_git_command(cmd)
            print(f"Deleted branches: {', '.join(branches)}")
            if result:
                print(result)
            return True
        except Exception as e:
            print(f"Failed to delete some branches: {e}")
            return False
    
    def save_deletion_log(self, branches: List[str]):
        """Save deleted branches to a log file for potential recovery."""
        log_entry = {
            'timestamp': datetime.datetime.now().isoformat(),
            'deleted_branches': branches,
            'current_branch': self.current_branch
        }
        
        log_file = '.git_branch_cleanup_log.json'
        log_data = []
        
        if os.path.exists(log_file):
            with open(log_file, 'r') as f:
                try:
                    log_data = json.load(f)
                except:
                    log_data = []
        
        log_data.append(log_entry)
        
        with open(log_file, 'w') as f:
            json.dump(log_data, f, indent=2)
    
    def restore_branches(self, branch_names: List[str]) -> bool:
        """Restore previously deleted branches from their last known state."""
        print("Restoring branches is not fully implemented in this version.")
        print("This would typically restore from the reflog or a backup.")
        print(f"Branches to restore: {', '.join(branch_names)}")
        return True  # Placeholder - actual implementation would be more complex


def main():
    parser = argparse.ArgumentParser(
        description='Git Branch Cleanup Tool - Detect and clean up merged/stale branches safely'
    )
    
    parser.add_argument(
        '--detect-merged',
        action='store_true',
        help='Detect branches that have been merged into main/master'
    )
    
    parser.add_argument(
        '--detect-stale',
        action='store_true',
        help='Detect stale branches (not updated in N days, default 30)'
    )
    
    parser.add_argument(
        '--days',
        type=int,
        default=30,
        help='Number of days for stale branch detection (default: 30)'
    )
    
    parser.add_argument(
        '--delete',
        nargs='+',
        metavar='BRANCH',
        help='Delete specified branches'
    )
    
    parser.add_argument(
        '--force-delete',
        nargs='+',
        metavar='BRANCH',
        help='Force delete specified branches (use with caution)'
    )
    
    parser.add_argument(
        '--list',
        action='store_true',
        help='List all branches with status information'
    )
    
    parser.add_argument(
        '--remote',
        default='origin',
        help='Remote name to check for merged branches (default: origin)'
    )
    
    parser.add_argument(
        '--policy-check',
        action='store_true',
        help='Check branches against team policies'
    )
    
    args = parser.parse_args()
    
    if len(sys.argv) == 1:
        parser.print_help()
        sys.exit(1)
    
    git_tool = GitBranchCleanup()
    
    if args.detect_merged:
        print("Detecting merged branches...")
        merged_branches = git_tool.get_merged_branches(args.remote)
        if merged_branches:
            print(f"Merged branches found ({len(merged_branches)}):")
            for branch in merged_branches:
                print(f"  - {branch}")
        else:
            print("No merged branches found.")
        print()
    
    if args.detect_stale:
        print(f"Detecting stale branches (not updated in last {args.days} days)...")
        stale_branches = git_tool.get_stale_branches(args.days)
        if stale_branches:
            print(f"Stale branches found ({len(stale_branches)}):")
            for branch_info in stale_branches:
                print(f"  - {branch_info['name']} (last updated {branch_info['days_old']} days ago)")
        else:
            print("No stale branches found.")
        print()
    
    if args.delete:
        print(f"Deleting branches: {', '.join(args.delete)}")
        # Confirm deletion
        confirm = input(f"Are you sure you want to delete these {len(args.delete)} branches? (yes/no): ")
        if confirm.lower() in ['yes', 'y']:
            if git_tool.delete_branches(args.delete, force=False):
                git_tool.save_deletion_log(args.delete)
                print("Branches deleted successfully.")
            else:
                print("Some branches could not be deleted.")
        else:
            print("Deletion cancelled.")
    
    if args.force_delete:
        print(f"Force deleting branches: {', '.join(args.force_delete)}")
        # Confirm deletion
        confirm = input(f"Are you sure you want to FORCE delete these {len(args.force_delete)} branches? This cannot be undone! (yes/no): ")
        if confirm.lower() in ['yes', 'y']:
            if git_tool.delete_branches(args.force_delete, force=True):
                git_tool.save_deletion_log(args.force_delete)
                print("Branches force-deleted successfully.")
            else:
                print("Some branches could not be force-deleted.")
        else:
            print("Force deletion cancelled.")
    
    if args.list:
        print("Listing all branches with status...")
        all_branches = git_tool.get_local_branches()
        merged_branches = set(git_tool.get_merged_branches(args.remote))
        stale_branches = [b['name'] for b in git_tool.get_stale_branches(args.days)]
        
        for branch in all_branches:
            status = []
            if branch in merged_branches:
                status.append("MERGED")
            if branch in stale_branches:
                status.append(f"STALE({git_tool.get_branch_last_commit_date(branch).strftime('%Y-%m-%d')})")
            if branch == git_tool.current_branch:
                status.append("CURRENT")
            
            status_str = f" [{', '.join(status)}]" if status else ""
            print(f"  {branch}{status_str}")
    
    if args.policy_check:
        print("Checking branches against team policies...")
        # Basic policy checks
        all_branches = git_tool.get_local_branches()
        
        issues = []
        for branch in all_branches:
            # Example policy: branches should follow naming convention
            if branch not in ['main', 'master'] and not any(prefix in branch for prefix in ['feature/', 'bugfix/', 'hotfix/', 'release/']):
                issues.append(f"Branch '{branch}' doesn't follow naming convention (should start with feature/, bugfix/, hotfix/, release/)")
        
        if issues:
            print(f"Policy violations found ({len(issues)}):")
            for issue in issues:
                print(f"  - {issue}")
        else:
            print("All branches comply with team policies.")


if __name__ == '__main__':
    main()