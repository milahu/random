#!/usr/bin/env python3

# run "git push"
# but push only one commit at a time

# use case:
# push a large repo with large files
# where each file was added in a separate commit

import argparse
import subprocess
import sys
from typing import List, Optional
import shlex


def run_git(args: List[str], check: bool = True) -> str:
    args = ["git", *args]
    print("+", shlex.join(args))
    result = subprocess.run(
        args,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
    )
    if check and result.returncode != 0:
        print(result.stdout, file=sys.stderr)
        sys.exit(result.returncode)
    return result.stdout.strip()


def git_rev_parse(rev: str) -> str:
    return run_git(["rev-parse", rev])


def git_rev_list(range_expr: str) -> List[str]:
    out = run_git(["rev-list", "--reverse", range_expr])
    return [line.strip() for line in out.splitlines() if line.strip()]


def remote_branch_commit(remote: str, branch: str) -> Optional[str]:
    """
    Return the remote branch HEAD commit hash, or None if branch does not exist.
    """
    out = run_git(
        ["ls-remote", "--heads", remote, branch],
        check=False,
    )

    if not out:
        return None

    return out.split()[0]


def local_branch_exists(branch: str) -> bool:
    result = subprocess.run(
        ["git", "show-ref", "--verify", f"refs/heads/{branch}"],
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )
    return result.returncode == 0


def find_merge_base(a: str, b: str) -> str:
    return run_git(["merge-base", a, b])


def push_commit(
    remote: str,
    commit: str,
    remote_branch: str,
    force: bool,
) -> None:
    refspec = f"{commit}:refs/heads/{remote_branch}"

    cmd = ["git", "push"]

    if force:
        cmd.append("--force")

    cmd.extend([remote, refspec])

    print("+", " ".join(cmd))
    subprocess.run(cmd, check=True)


def parse_ref(ref: str):
    """
    Parse git push style refspec.

    Supported:
      main
      HEAD
      HEAD:main
      mybranch:main
    """

    if ":" in ref:
        local_ref, remote_ref = ref.split(":", 1)
    else:
        local_ref = ref
        remote_ref = ref

    return local_ref, remote_ref


r'''
def main():
    local_ref, remote_branch = parse_ref(args.ref)

    local_commit = git_rev_parse(local_ref)

    remote_commit = remote_branch_commit(args.remote, remote_branch)

    print(f"Local  : {local_commit}")
    print(f"Remote : {remote_commit or '(branch does not exist)'}")

'''


def main():
    parser = argparse.ArgumentParser(
        description="Incrementally push one commit at a time."
    )

    parser.add_argument(
        "--force",
        action="store_true",
        help="Force push incrementally from merge-base.",
    )

    parser.add_argument(
        "remote",
        nargs="?",
        help="Remote name (defaults to git's configured push remote)",
    )

    parser.add_argument(
        "ref",
        nargs="?",
        help="Refspec to push (defaults to current branch)",
    )

    args = parser.parse_args()

    if args.ref:
        local_ref, remote_branch = parse_ref(args.ref)
    else:
        current_branch = run_git(
            ["symbolic-ref", "--quiet", "--short", "HEAD"],
            check=False,
        )
        detached_head = not bool(current_branch)
        if detached_head:
            local_ref = "HEAD"
            remote_branch = "HEAD"
        else:
            local_ref = current_branch
            remote_branch = current_branch

    local_commit = git_rev_parse(local_ref)

    #
    # Determine remote
    #

    if args.remote:
        remote = args.remote
    else:
        # Match git push default remote selection behavior reasonably closely.
        #
        # Priority:
        #   branch.<name>.pushRemote
        #   remote.pushDefault
        #   branch.<name>.remote
        #   origin
        #

        remote = None

        if not detached_head:
            remote = run_git(
                ["config", "--get", f"branch.{current_branch}.pushRemote"],
                check=False,
            )

        if not remote:
            remote = run_git(
                ["config", "--get", "remote.pushDefault"],
                check=False,
            )

        if not remote and not detached_head:
            remote = run_git(
                ["config", "--get", f"branch.{current_branch}.remote"],
                check=False,
            )

        if not remote:
            remote = "origin"

    print(f"Remote name : {remote}")
    print(f"Local ref   : {local_ref}")
    print(f"Remote ref  : {remote_branch}")

    remote_commit = remote_branch_commit(remote, remote_branch)

    if remote_commit:
        if args.force:
            start_commit = find_merge_base(local_commit, remote_commit)

            print(f"Merge-base: {start_commit}")

            if start_commit == local_commit:
                print("Nothing to push.")
                return

            commits = git_rev_list(f"{start_commit}..{local_commit}")

        else:
            if remote_commit == local_commit:
                print("Nothing to push.")
                return

            commits = git_rev_list(f"{remote_commit}..{local_commit}")

    else:
        # Remote branch does not exist.
        # Start from root commit.
        commits = git_rev_list(local_commit)

    if not commits:
        print("Nothing to push.")
        return

    print(f"Pushing {len(commits)} commits incrementally...")

    for commit_idx, commit in enumerate(commits):
        print()
        print(f"Pushing commit {commit_idx + 1} of {len(commits)}")
        push_commit(
            remote=args.remote,
            commit=commit,
            remote_branch=remote_branch,
            force=args.force,
        )

    print("Done.")


if __name__ == "__main__":
    main()
