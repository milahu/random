#! /usr/bin/env python3

# https://codereview.stackexchange.com/questions/267787/python-3-arbitrary-base-converter-and-base36-encoder

# https://onlineasciitools.com/convert-ascii-to-arbitrary-base

import sys

#from string import ascii_lowercase
#from string import ascii_uppercase
#from string import digits
from typing import List, Iterable

# >>> string.printable
# '0123456789abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ!"#$%&\'()*+,-./:;<=>?@[\\]^_`{|}~ \t\n\r\x0b\x0c'

# 10 + 26 + 26 + 2 = 64
#GLYPHS = digits + ascii_lowercase + ascii_uppercase + "_+"
# only "_" and "'" are treated as "characters" by chrome browser.
# "characters" as in: double-click will select one word.
GLYPHS = "0123456789abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ_'"


def log2(n: int) -> int:
    return n.bit_length() - 1


def power_of_2(n: int) -> bool:
    return (n & (n-1) == 0) and n != 0


def sep_for_base(base: int) -> str:
    return {
        60: ':',
        256: '.',
    }.get(base, ',')


def parser(s: str, base: int) -> List[int]:
    # if 2 <= base <= 36:
    # >>> len(string.digits + string.ascii_letters + string.punctuation)
    # 94
    if 2 <= base <= 94:
        return [GLYPHS.index(i) for i in s]

    return s.split(sep_for_base(base))


def to_base(num: int, base: int) -> str:
    if not isinstance(base, int):
        raise ValueError()
    if base < 2:
        raise ValueError()
    if base > 256:
        raise ValueError()

    if power_of_2(base):
        l = log2(base)
        powers = range(num.bit_length() // l + (num.bit_length() % l != 0))
        places = [(num >> l * i) % base for i in powers]

    else:
        if num == 0:
            return '0'

        places = []
        while num:
            n, p = divmod(num, base)
            places.append(p)
            num = n

    #if base > 36:
    #    sep = sep_for_base(base)
    #    return sep.join(map(str, reversed(places)))

    # >>> len(string.digits + string.ascii_letters + string.punctuation)
    # 94
    if base > 94:
        GLYPHS = ''.join([chr(i) for i in range(256)])

    result = ''.join([GLYPHS[p] for p in reversed(places)])
    if base == 16 and len(result) % 2 == 1:
        result = "0" + result
    return result


def from_base(s: str, base: int) -> int:
    if base < 2 or not isinstance(base, int):
        raise ValueError()

    # if base <= 36:
    # >>> len(string.digits + string.ascii_letters + string.punctuation)
    # 94
    if base <= 94:
        for i in s:
            #print("checking char:", repr(i))
            if GLYPHS.index(i) >= base:
                raise ValueError()

    else:
        sep = sep_for_base(base)
        for i in s.split(sep):
            if int(i) >= base:
                raise ValueError()

    places = parser(s, base)

    if power_of_2(base):
        l = log2(base)
        return sum([int(n) << l * p for p, n in enumerate(reversed(places))])

    powers = reversed([base ** i for i in range(len(places))])
    return sum(int(a) * b for a, b in zip(places, powers))


def b36encode(s: str) -> str:
    msg = s.encode('utf8').hex()
    n = int(msg, 16)
    return to_base(n, 36)


def b36decode(m: str) -> str:
    n = from_base(m, 36)
    h = hex(n).removeprefix('0x')
    return bytes.fromhex(h).decode('utf8')


def b36_encode(s: str) -> str:
    msg = [ord(i) for i in s]
    return ''.join([to_base(n, 36).zfill(2) for n in msg])


def b36_digits(m: str) -> Iterable[int]:
    for i in range(0, len(m), 2):
        n = m[i:i+2]
        yield from_base(n, 36)


def b36_decode(m) -> str:
    s = b36_digits(m)
    return ''.join(chr(n) for n in s)


def base36_encode(s: str) -> str:
    msg = s.encode('utf8')
    return ''.join([to_base(n, 36) for n in msg])


def base36_decode(m: str) -> str:
    s = b36_digits(m)
    return bytearray(s).decode('utf8')


def assert_from_base(s: str, base: int, exp: int) -> None:
    assert int(s, base) == exp
    assert from_base(s, base) == exp


def round_trip(x: int, base: int, s: str) -> None:
    s_actual = to_base(x, base)
    assert s == s_actual
    assert_from_base(s, base, x)


def test() -> None:
    round_trip(2**24-1, 3, '1011120101000100')
    round_trip(2**32-1, 3, '102002022201221111210')
    round_trip(2**64-1, 36, '3w5e11264sgsf')

    assert to_base(46610, 16) == 'b612'

    assert to_base(54, 13) == '42'

    assert_from_base('zzz', 36, 46655)

    round_trip(993986429283, 36, 'computer')

    assert b36encode('whoami') == '1ajdznl1ex'
    assert b36decode('1ajdznl1ex') == 'whoami'

    assert '᠀᠀᠀' == '\u1800\u1800\u1800'
    assert b36encode('᠀᠀᠀') == 'oedjywcl6i78g0'
    assert b36decode('oedjywcl6i78g0') == '᠀᠀᠀'
    assert base36_encode('᠀᠀᠀') == '694g3k694g3k694g3k'
    assert base36_decode('694g3k694g3k694g3k') == '᠀᠀᠀'


if __name__ == '__main__':

    #test()
    from_base_n = int(sys.argv[1])
    to_base_n = int(sys.argv[2])
    #s = sys.stdin.read()
    bytes_ = sys.stdin.buffer.read()
    #msg = s.encode('utf8').hex()

    if from_base_n == 0:
      msg = bytes_.hex()
      input = int(msg, 16)
      result = to_base(input, to_base_n)
      print(result)
      sys.exit()

    # TODO remove all whitespace

    input_string = bytes_.decode('ascii').strip()
    #print("input string:", repr(input_string))

    input = from_base(input_string, from_base_n)
    result = to_base(input, to_base_n)
    print(result)
    sys.exit()
