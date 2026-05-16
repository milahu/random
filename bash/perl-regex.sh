#!/usr/bin/env bash

# https://superuser.com/questions/416419/perl-for-matching-with-regular-expressions-in-terminal

# https://stackoverflow.com/questions/4361004/perl-regex-to-act-on-a-file-from-the-command-line

# replace "</span>\n<span" with "</span><span"
# replacing text across newlines is hard with sed, but trivial with perl

perl -i.bak$(date +%s) -0777 -pe 's/<\/span>\n<span/<\/span><span/sg' test.html
