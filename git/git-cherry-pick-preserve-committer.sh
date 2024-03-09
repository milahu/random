#!/usr/bin/env bash

# git-cherry-pick-preserve-committer.sh

# bash script to modify committer after git cherry-pick

# either to preserve the original committer
# or to use author as committer
# similar to git rebase --committer-date-is-author-date

#     #echo 'format = "%an\n%ae\n%at\n%ad"' # committer is author
#     echo 'format = "%cn\n%ce\n%ct\n%cd"' # preserve committer

set -e

# preserve committer in "git cherry-pick"

function git_cherry_pick_preserve_committer() {

  # only modify commits of the "git cherry-pick"
  local head_before_cherry_pick=$(git rev-parse HEAD)

  # -x: append "(cherry picked from commit ...)" to the original commit message
  local args=(git cherry-pick -x "$@")
  echo -n "running:"; printf " %q" "${args[@]}"; echo
  "${args[@]}"

  # run "git filter-repo" to postprocess the "git cherry-pick"

  # Python code body for processing commit objects
  commit_callback=$(
    #echo 'print("locals", locals())'

    echo 'message_lines = commit.message.split(b"\n")'
    #echo 'print("message_lines", repr(message_lines))'
    echo 'try:'
    echo '  picked_from = message_lines[-2].decode("ascii")'
    echo 'except IndexError:'
    echo '  return'
    echo 'if not picked_from.startswith("(cherry picked from commit "):'
    echo '  return'

    # print newline after "Parsed 123 commits"
    #echo 'print()'

    #echo 'print("message_lines", repr(message_lines))'
    echo 'assert len(picked_from) == 68, f"unexpected picked_from: {repr(picked_from)}"'
    echo 'picked_from = picked_from[27:-1]'

    #echo 'for a in ["author_date", "author_email", "author_name", "message", "branch", "id", "old_id", "original_id", "parents", "type"]:'
    #echo '  print(f"commit.{a}", repr(getattr(commit, a)))'

    #echo 'print("picked_from", repr(picked_from))'

    # _do_not_use_this_var is passed via callback_metadata
    # lets use it! :P
    # we only need repo_filter._repo_working_dir
    # 'commit_rename_func': <bound method RepoFilter._translate_commit_hash of <git_filter_repo.RepoFilter object at ...>>
    echo 'repo_filter = _do_not_use_this_var["commit_rename_func"].__self__'
    #echo 'print("repo_filter", repo_filter)'

    #echo 'format = "%an\n%ae\n%at\n%ad"' # committer is author
    echo 'format = "%cn\n%ce\n%ct\n%cd"' # preserve committer

    echo 'args = ["git", "show", "-s", f"--format=format:{format}", picked_from]'
    #echo 'print("args", repr(args))'
    echo 'proc = subproc.Popen(args, stdout=subprocess.PIPE, cwd=repo_filter._repo_working_dir)'
    echo 'lines = proc.stdout.read().splitlines()'
    echo 'if len(lines) != 4:'
    echo '  print("lines", repr(lines))'
    echo '  raise Exception(f"not found picked_from commit {picked_from}")'
    echo 'commit.committer_name = lines[0]'
    echo 'commit.committer_email = lines[1]'
    echo 'commit.committer_date = lines[2] + lines[3][-6:]' # timestamp + timezone

    echo 'message_lines = message_lines[:-2]' # remove "cherry picked from" line
    echo 'commit.message = b"\n".join(message_lines)'
    #echo 'print("commit.message", repr(commit.message))'
  )

  # preserve-commit-hashes
  # fix: fatal: bad object xxx
  # git-filter-repo patches hashes in commit.message

  git filter-repo \
    --force \
    --preserve-commit-hashes \
    --commit-callback "$commit_callback" \
    --refs "$head_before_cherry_pick..HEAD"

}

git_cherry_pick_preserve_committer "$@"
