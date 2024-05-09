#!/usr/bin/env bash

# https://stackoverflow.com/questions/2199897
# How to convert a normal Git repository to a bare one?

# most solutions simply delete the main worktree
# but that also deletes untracked files
# here, we move untracked files to a separate directory

set -e
set -u
#set -x # debug

main_worktree_path="$1"

main_worktree_path="$(readlink -f "$main_worktree_path")"

workdir_path"$(readlink -f .)"

if [ "$main_worktree_path" = "$workdir_path" ]; then
  echo "error: main_worktree_path cannot be the current workdir, because it will be removed"
  exit 1
fi

cd "$main_worktree_path"

if ! [ -d .git ]; then
  echo "error: missing .git/"
  exit 1
fi

version=$(date --utc +%Y%m%dT%H%M%SZ).$(mktemp -u XXXXXXXX)

basename="${PWD##*/}"

# move .git to this path
git_path="../$basename.git"

# move untracked files to this directory
tmp_path="../$basename.untracked.$version"

if [ -e "$git_path" ]; then echo "error: path exists: ${git_path@Q}"; exit 1; fi
if [ -e "$tmp_path" ]; then echo "error: path exists: ${tmp_path@Q}"; exit 1; fi

# no. rsync does not move files
# remove-source-files means copy and delete files, which is slow/wasteful
if false; then
args=(
  rsync
    #--verbose # debug
    --archive
    --recursive # not implied by --archive when --files-from is used
    --remove-source-files # copy and delete files
    --from0
    .
    "$tmp_path"
)
"${args[@]}" \
    --files-from=<(
      git ls-files -dmoz --directory
    )
fi

echo "checking for untracked files"

# actually "move" untracked files
# git ls-files -dmoz | xargs -r -0 mv -v -t "$tmp_path" # wrong: mv does not preserve path
has_untracked=0
while IFS= read -r -d '' src; do
  if [ $has_untracked = 0 ]; then
    echo "moving untracked files to $tmp_path"
    mkdir -p "$tmp_path"
    has_untracked=1
  fi
  stack=("$src")
  dirstack=()
  while [ ${#stack[@]} != 0 ]; do
    echo "stack ${stack@Q}"
    src="${stack[0]}"; stack=("${stack[@]:1}") # shift src from stack
    #[ -z "$src" ] && continue
    echo "src ${src@Q}"
    isdir=0
    if [ "${src: -1}" = "/" ]; then # git shows directories with "/" suffix
      src="${src:0: -1}"
      isdir=1
    elif [ -d "$src" ]; then
      isdir=1
    fi
    srcdir="${src%/*}"
    dst="$tmp_path/$src"
    dstdir="${dst%/*}"
    #echo "dstdir ${dstdir@Q}"
    # mkdir -p "$(dirname "$dst")" # more generic
    if [ -e "$dstdir" ] && ! [ -d "$dstdir" ]; then
      dstdir2="$dstdir.$version"
      echo "note: file exists: ${dstdir@Q}. moving ${src@Q} to ${dstdir2@Q}"
      dstdir="$dstdir2"
      dst="$dstdir2/${src##*/}"
    fi
    if [ -e "$dst" ]; then # dst path exists
      if [ $isdir = 0 ]; then # src path is file
        if [ -d "$dst" ]; then # dst path is dir
          dst2="$dst.$version"
          echo "note: dir exists: ${dst@Q}. moving ${src@Q} to ${dst2@Q}"
          dst="$dst2"
        else # dst path is file
          # compare files: permissions, size, content
          if
            [ $(stat -c%a_%s "$src") = $(stat -c%a_%s "$dst") ] &&
            [ $(sha256sum "$src" | head -c64) = $(sha256sum "$dst" | head -c64) ]
          then
            echo "note: same file exists: ${dst@Q}. deleting ${src@Q}"
            rm "$src"
            continue
          else
            dst2="$dst.$version"
            echo "note: different file exists: ${dst@Q}. moving ${src@Q} to ${dst2@Q}"
            dst="$dst2"
          fi
        fi
      else # src path is dir
        if ! [ -d "$dst" ]; then # dst path is file
          dst2="$dst.$version"
          echo "note: file exists: ${dst@Q}. moving ${src@Q} to ${dst2@Q}"
          dst="$dst2"
        fi
        # dst path is dir
        echo "note: dir exists: ${dst@Q}. moving contents of ${src@Q}"
        # recurse: move contents of src dir
        while IFS= read -r -d '' src2; do
          if [ -d "$src2" ]; then
            stack+=("$src2/")
          else
            stack+=("$src2")
          fi
        done < <(
          find "$src" -mindepth 1 -maxdepth 1 -print0
        )
        #echo "dirstack+=(${src@Q})"
        dirstack+=("$src") # later: remove empty src dir
        #echo "dirstack ${dirstack@Q}"
        continue
      fi
      dstdir2="$dstdir.$version"
      echo "error: file exists: ${dstdir@Q}. moving to ${dstdir2@Q}"
      dstdir="$dstdir2"
      dst="$dstdir2/${src##*/}"
    fi
    mkdir -p "$dstdir"
    echo mv "${src@Q}" "${dst@Q}"
    mv "$src" "$dst"
    # no. still walking down here
    #rmdir --ignore-fail-on-non-empty "$srcdir" # remove srcdir if empty
  done
  # walk up
  # todo? try this more often to keep dirstack small
  while [ ${#dirstack[@]} != 0 ]; do
    #echo "dirstack ${dirstack@Q}"
    srcdir="${dirstack[-1]}"; dirstack=("${dirstack[@]:0:$((${#dirstack[@]} - 1))}") # pop srcdir from stack
    #echo "srcdir ${srcdir@Q}"
    rmdir --ignore-fail-on-non-empty "$srcdir" # remove srcdir if empty
  done
done < <(
  git ls-files -dmoz --directory
)

if [ $has_untracked = 0 ]; then
  echo "ok. found no untracked files"
else
  echo "ok. done moving untracked files"
fi



echo "moving .git/ to ${git_path@Q}"
mv .git "$git_path"

echo "setting git config core.bare=true in ${git_path@Q}"
git -C "$git_path" config --bool core.bare true

echo "removing main worktree ${main_worktree_path@Q}"
#cd "$workdir_path"
cd ..
rm -rf "$main_worktree_path"
