#! /nix/store/bdzvgpz8y5qd4iy4p59zl74l2qk5gcgy-bash-5.2-p21/bin/bash -e
export WINELOADER='/nix/store/fa1fn9p561cy7nlzvdgmkgzpy20fxcm5-wine-9.0/bin/.wine'
GST_PLUGIN_SYSTEM_PATH_1_0=${GST_PLUGIN_SYSTEM_PATH_1_0:+':'$GST_PLUGIN_SYSTEM_PATH_1_0':'}
GST_PLUGIN_SYSTEM_PATH_1_0=${GST_PLUGIN_SYSTEM_PATH_1_0/':''/nix/store/bx31vqni82ywaq03s6di41d0gs4vnqgg-gst-plugins-bad-1.22.8/lib/gstreamer-1.0'':'/':'}
GST_PLUGIN_SYSTEM_PATH_1_0='/nix/store/bx31vqni82ywaq03s6di41d0gs4vnqgg-gst-plugins-bad-1.22.8/lib/gstreamer-1.0'$GST_PLUGIN_SYSTEM_PATH_1_0
GST_PLUGIN_SYSTEM_PATH_1_0=${GST_PLUGIN_SYSTEM_PATH_1_0#':'}
GST_PLUGIN_SYSTEM_PATH_1_0=${GST_PLUGIN_SYSTEM_PATH_1_0%':'}
export GST_PLUGIN_SYSTEM_PATH_1_0
GST_PLUGIN_SYSTEM_PATH_1_0=${GST_PLUGIN_SYSTEM_PATH_1_0:+':'$GST_PLUGIN_SYSTEM_PATH_1_0':'}
GST_PLUGIN_SYSTEM_PATH_1_0=${GST_PLUGIN_SYSTEM_PATH_1_0/':''/nix/store/1363ws11bg33i9cnwdxv7f19d5gxif56-gst-libav-1.22.8/lib/gstreamer-1.0'':'/':'}
GST_PLUGIN_SYSTEM_PATH_1_0='/nix/store/1363ws11bg33i9cnwdxv7f19d5gxif56-gst-libav-1.22.8/lib/gstreamer-1.0'$GST_PLUGIN_SYSTEM_PATH_1_0
GST_PLUGIN_SYSTEM_PATH_1_0=${GST_PLUGIN_SYSTEM_PATH_1_0#':'}
GST_PLUGIN_SYSTEM_PATH_1_0=${GST_PLUGIN_SYSTEM_PATH_1_0%':'}
export GST_PLUGIN_SYSTEM_PATH_1_0
GST_PLUGIN_SYSTEM_PATH_1_0=${GST_PLUGIN_SYSTEM_PATH_1_0:+':'$GST_PLUGIN_SYSTEM_PATH_1_0':'}
GST_PLUGIN_SYSTEM_PATH_1_0=${GST_PLUGIN_SYSTEM_PATH_1_0/':''/nix/store/ff4fq6v90qfz7syavk52m8b6s54lc98x-gst-plugins-ugly-1.22.8/lib/gstreamer-1.0'':'/':'}
GST_PLUGIN_SYSTEM_PATH_1_0='/nix/store/ff4fq6v90qfz7syavk52m8b6s54lc98x-gst-plugins-ugly-1.22.8/lib/gstreamer-1.0'$GST_PLUGIN_SYSTEM_PATH_1_0
GST_PLUGIN_SYSTEM_PATH_1_0=${GST_PLUGIN_SYSTEM_PATH_1_0#':'}
GST_PLUGIN_SYSTEM_PATH_1_0=${GST_PLUGIN_SYSTEM_PATH_1_0%':'}
export GST_PLUGIN_SYSTEM_PATH_1_0
GST_PLUGIN_SYSTEM_PATH_1_0=${GST_PLUGIN_SYSTEM_PATH_1_0:+':'$GST_PLUGIN_SYSTEM_PATH_1_0':'}
GST_PLUGIN_SYSTEM_PATH_1_0=${GST_PLUGIN_SYSTEM_PATH_1_0/':''/nix/store/9hslf8dmpy4cf4wb6fzfq0hflp15azg6-gst-plugins-good-1.22.8/lib/gstreamer-1.0'':'/':'}
GST_PLUGIN_SYSTEM_PATH_1_0='/nix/store/9hslf8dmpy4cf4wb6fzfq0hflp15azg6-gst-plugins-good-1.22.8/lib/gstreamer-1.0'$GST_PLUGIN_SYSTEM_PATH_1_0
GST_PLUGIN_SYSTEM_PATH_1_0=${GST_PLUGIN_SYSTEM_PATH_1_0#':'}
GST_PLUGIN_SYSTEM_PATH_1_0=${GST_PLUGIN_SYSTEM_PATH_1_0%':'}
export GST_PLUGIN_SYSTEM_PATH_1_0
GST_PLUGIN_SYSTEM_PATH_1_0=${GST_PLUGIN_SYSTEM_PATH_1_0:+':'$GST_PLUGIN_SYSTEM_PATH_1_0':'}
GST_PLUGIN_SYSTEM_PATH_1_0=${GST_PLUGIN_SYSTEM_PATH_1_0/':''/nix/store/923drmgjivczhx9svbyy7gh48ql5m3z8-gst-plugins-base-1.22.8/lib/gstreamer-1.0'':'/':'}
GST_PLUGIN_SYSTEM_PATH_1_0='/nix/store/923drmgjivczhx9svbyy7gh48ql5m3z8-gst-plugins-base-1.22.8/lib/gstreamer-1.0'$GST_PLUGIN_SYSTEM_PATH_1_0
GST_PLUGIN_SYSTEM_PATH_1_0=${GST_PLUGIN_SYSTEM_PATH_1_0#':'}
GST_PLUGIN_SYSTEM_PATH_1_0=${GST_PLUGIN_SYSTEM_PATH_1_0%':'}
export GST_PLUGIN_SYSTEM_PATH_1_0
GST_PLUGIN_SYSTEM_PATH_1_0=${GST_PLUGIN_SYSTEM_PATH_1_0:+':'$GST_PLUGIN_SYSTEM_PATH_1_0':'}
GST_PLUGIN_SYSTEM_PATH_1_0=${GST_PLUGIN_SYSTEM_PATH_1_0/':''/nix/store/pcdr6h5kgw5rcbdldnx47s1749gvj0nr-gstreamer-1.22.8/lib/gstreamer-1.0'':'/':'}
GST_PLUGIN_SYSTEM_PATH_1_0='/nix/store/pcdr6h5kgw5rcbdldnx47s1749gvj0nr-gstreamer-1.22.8/lib/gstreamer-1.0'$GST_PLUGIN_SYSTEM_PATH_1_0
GST_PLUGIN_SYSTEM_PATH_1_0=${GST_PLUGIN_SYSTEM_PATH_1_0#':'}
GST_PLUGIN_SYSTEM_PATH_1_0=${GST_PLUGIN_SYSTEM_PATH_1_0%':'}
export GST_PLUGIN_SYSTEM_PATH_1_0



args=(
gdb

--batch

-ex "set trace-commands on"
#-ex "set logging file gdb.out" -ex "set logging on"

-ex "set follow-exec-mode new"
-ex "set breakpoint pending on"
#-ex "set detach-on-fork off"
-ex "set follow-fork-mode child"
#-ex "set disassemble-next-line on"
-ex "break execv"
-ex "break execvp"
#-ex "break __kernel_vsyscall" # too many breaks
-ex "break exit"
-ex "break syscall"
-ex "break fatal_error"
-ex "break getuid"
-ex "break getenv"
-ex "break syscall"

-ex "run" # run to getenv
-ex "info threads"
-ex 'printf "%s\n", $eax' # WINEDLLPATH
-ex "info threads"
-ex "catch syscall exit_group"

-ex "c"
-ex "info threads"
-ex "catch syscall exit_group"
-ex 'printf "%s\n", $eax' # HOME

-ex 'c' # continue to getenv
-ex "info threads"
-ex 'printf "%s\n", $eax' # USER

-ex 'c' # continue to getenv
-ex "info threads"
-ex 'printf "%s\n", $eax' # WINEPREFIX

-ex 'c' # continue to getenv
-ex "info threads"
-ex 'printf "%s\n", $eax' # WINELOADERNOEXEC

-ex 'c' # continue to execv
-ex 'printf "%s\n", $eax' # wine-preloader
-ex "info threads"
-ex "catch syscall group:process"

-ex 'c'
#-ex 'printf "eax = %s\n", $eax'
-ex 'printf "ebx = %s\n", $ebx'
#-ex 'printf "ecx = %s\n", $ecx'
#-ex 'printf "edx = %s\n", $edx'
-ex "info threads"
-ex "info inferiors"
-ex "catch syscall group:process"
# Catchpoint 11 (call to syscall execve), 0xf7fc7589 in __kernel_vsyscall ()
# ebx = /nix/store/fa1fn9p561cy7nlzvdgmkgzpy20fxcm5-wine-9.0/bin/wine-preloader

-ex 'printf "FIXME no breaks before exit\n"'

-ex 'c'

--args
"/nix/store/fa1fn9p561cy7nlzvdgmkgzpy20fxcm5-wine-9.0/bin/.wine"  "$@"
)
exec "${args[@]}"

FIXME
process 2757624 is executing new program: /nix/store/fa1fn9p561cy7nlzvdgmkgzpy20fxcm5-wine-9.0/bin/wine-preloader
[New inferior 2]
[New process 2757624]
wine: '/var/empty' is not owned by you
[Inferior 2 (process 2757624) exited with code 01]
