# https://stackoverflow.com/questions/1885181/how-to-un-escape-a-backslash-escaped-string/72564681#72564681

# shlex.quote [1] is optimized for performance,
# so the output is machine-readable, but less pretty for human eyes.
# producing a "pretty" string is slower
#
# when you wrap the string in double-quotes (for a shell),
# you also need to escape expressions like `$x` or `$(x)` or `!x`
#
# [1] https://github.com/python/cpython/blob/58277de8e651df287ceae053eeb321c0f8406a1b/Lib/shlex.py#L325

import re

_shell_quote_is_unsafe = re.compile(r'[^\w@%+=:,./-]', re.ASCII).search
# note: [^...] = negated char class -> safe chars are \w@%+=:,./-

_shell_quote_replace = re.compile(r'([\\$"!])', re.ASCII).sub

def shell_quote(s: str):
    """
    Return a shell-escaped version of the string *s*.
    Wrap string in double-quotes when necessary.
    Based on shlex.quote (wrap string in single-quotes)
    """
    if not s:
        return '""'
    if _shell_quote_is_unsafe(s) is None:
        return s
    return '"' + _shell_quote_replace(r"\\\1", s) + '"'

# test
assert shell_quote('a"b\\c$d$(e)!f\tg\nh\ri') == '"a\\"b\\\\c\\$d\\$(e)\\!f\tg\nh\ri"'
