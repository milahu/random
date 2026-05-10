#!/usr/bin/env python3

# https://stackoverflow.com/questions/12523586/python-format-size-application-converting-b-to-kb-mb-gb-tb

# binary-prefixed decimal units: B, KiB, MiB, GiB, ...
format_size = lambda n:(
    (lambda L:(f'{n/1024**L:.2f}{(" KMGTPEZYRQ"[L]+"i")*(L>0)}'
    ).rstrip('0').rstrip('.')if L else str(n))(
    (len(bin(int(n)))-1)//10
    )
)+"B"

# decimal units: B, KB, MB, GB, ...
format_size_decimal = lambda n:(
    (lambda L:(f'{n/1000**L:.2f}{" KMGTPEZYRQ"[L]*(L>0)}'
    ).rstrip('0').rstrip('.')if L else str(n))(
    (len(str(int(n)))-1)//3)
)+"B"

# long version
r'''
def format_size(n):
    s = str(n)
    l = len(s)
    L = int((l-1)/3)
    sufs = "1KMGTPEZYRQ"
    suf = sufs[L] if L > 0 else ""
    r = s[:(l - L*3)] + suf
    # print(f"n={n} l={l} L={L} suf={suf} r={r}")
    return r
'''



if __name__ == "__main__":
    # test
    ns = [
        1,
        12,
        123,
        1234,
        1024,
        12345,
        123456,
        1234567,
        1048576,
        12345678,
        123456789,
    ]
    for n in ns:
        r = format_size(n)
        print(f"{r:9s} = {n}")
