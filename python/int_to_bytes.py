#!/usr/bin/env python3

def int_to_bytes(n: int) -> bytes:
    # https://stackoverflow.com/a/12859903/10440128
    return n.to_bytes((n.bit_length() + 7) // 8, 'big') or b'\0'

if __name__ == "__main__":
    n = 1234567890123456789012345678901234567890
    b = int_to_bytes(n)
    print(f"{n} decimal = {b.hex()} hex")
