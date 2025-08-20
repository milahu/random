#!/usr/bin/env python3
# move files to trash, the "smart" way. "smart" as in:
# try to avoid moving files across different filesystems (which is slow)
# FIXME mp_trash_path is readable by other users
import os, sys
trash_subpath = ".local/share/Trash/files"
default_trash_path = os.path.realpath(os.path.join(os.environ["HOME"], trash_subpath))
# default_trash_dev = os.stat(default_trash_path).st_dev; print("default_trash_dev", default_trash_dev)
def find_mount_point(path): # https://stackoverflow.com/a/4453715/10440128
    path = os.path.realpath(path)
    while not os.path.ismount(path):
        path = os.path.dirname(path)
    return path
def get_path2(path, trash_dir):
    os.makedirs(trash_dir, exist_ok=True)
    path2 = os.path.join(trash_dir, os.path.basename(path))
    return path2
for path in sys.argv[1:]:
    print("trashing", repr(path))
    # path_dev = os.stat(path).st_dev; print("path_dev", path_dev)
    mp_path = find_mount_point(path)
    print("  mp_path", repr(mp_path))
    mp_trash_path = os.path.realpath(os.path.join(mp_path, trash_subpath))
    done_move = False
    for trash_path in set([default_trash_path, mp_trash_path]):
        path2 = get_path2(path, trash_path)
        try:
            os.rename(path, path2) # this only works on the same filesystem
            print(f"  fast path: moved file to the same-filesystem trash {trash_path}")
            done_move = True
            break
        except OSError as exc: # [Errno 18] Invalid cross-device link
            pass # path and path2 are on different filesystems
    if done_move: continue
    trash_path = default_trash_path
    path2 = get_path2(path, trash_path)
    shutil.move(path, path2) # slow path: copy + unlink
    print(f"  slow path: moved file to the other-filesystem trash {trash_path}")
