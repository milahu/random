#!/usr/bin/env python3

# https://stackoverflow.com/questions/436220
# How to determine the encoding of text

# guess text encoding of bytestring

# [cchardet]: https://github.com/PyYoshi/cChardet
# [faust-cchardet]: https://github.com/faust-streaming/cChardet
# [uchardet]: https://gitlab.freedesktop.org/uchardet/uchardet
# good for short strings
# fails on long strings
def guess_encoding_cchardet(bs: bytes):
    return cchardet.detect(bs).get("encoding")

# [charset_normalizer]: https://github.com/jawah/charset_normalizer
# [charset_normalizer#566]: https://github.com/jawah/charset_normalizer/issues/566
# good for long strings
# fails on short strings
#   https://github.com/jawah/charset_normalizer/issues/486
# 20x faster than chardet [charset_normalizer]
#   -> 200x slower than cchardet
# 5x slower than cchardet [charset_normalizer#566]
# benchmark versus chardet
#   https://github.com/jawah/charset_normalizer/raw/master/bin/performance.py
def guess_encoding_charset_normalizer(bs: bytes):
    match = charset_normalizer.from_bytes(bs).best()
    if match:
        return match.encoding
    return None

# [rs_chardet]: https://github.com/emattiza/rs_chardet
# 40x slower than cchardet [rs_chardet]
def guess_encoding_rs_chardet(bs: bytes):
    return rs_chardet.detect_rs_enc_name(bs)
    # return rs_chardet.detect_codec(bs).name

# [chardet]: https://github.com/chardet/chardet
# 4000x slower than cchardet [rs_chardet]
# 2000x slower than cchardet [cchardet]
def guess_encoding_chardet(bs: bytes):
    return chardet.detect(bs).get("encoding")

# [magic]: https://github.com/ahupp/python-magic
# fails on short strings
def guess_encoding_magic(bs: bytes):
    e = magic.detect_from_content(bs).encoding
    if e in ("binary", "unknown-8bit"):
        return None
    return e

# [icu]: https://github.com/unicode-org/icu
# fails on short strings
def guess_encoding_icu(bs: bytes):
    try:
        return icu.CharsetDetector(bs).detect().getName()
    except icu.ICUError:
        return None



if __name__ == "__main__":

    # test

    import random

    bytes_encoding_list = [
        ("ü".encode("latin1"), "latin1"),
        ("üü".encode("latin1"), "latin1"),
        ("üüü".encode("latin1"), "latin1"),
    ]

    for _ in range(10):
        bytes_encoding_list += [
            (random.randbytes(20), None),
        ]

    def test(guess_encoding):
        global bytes_encoding_list
        module_name = guess_encoding._name
        for input_bytes, expected_encoding in bytes_encoding_list:
            assert isinstance(input_bytes, bytes)
            # TODO better...
            guessed_encoding = guess_encoding(input_bytes)
            actual_string = None
            if guessed_encoding:
                try:
                    actual_string = input_bytes.decode(guessed_encoding)
                except Exception as exc:
                    if expected_encoding == None:
                        print(f"{module_name}: fail. found wrong encoding {guessed_encoding} in random bytes {input_bytes}")
                        continue
                    else:
                        print(f"{module_name}: FIXME failed to decode bytes: {exc}")
            if expected_encoding == None:
                # the guessed encoding can be anything -> dont compare encoding
                if guessed_encoding == None:
                    print(f"{module_name}: ok. found no encoding in random bytes {input_bytes}")
                else:
                    print(f"{module_name}: ok. found encoding {guessed_encoding} in random bytes {input_bytes} -> string {actual_string!r}")
            else:
                expected_string = input_bytes.decode(expected_encoding)
                if actual_string == expected_string:
                    print(f"{module_name}: ok. decoded {actual_string} from {guessed_encoding} bytes {input_bytes}")
                else:
                    #print(f"{module_name}: fail. actual {actual_string!r} from {guessed_encoding}. expected {expected_string!r} from {expected_encoding} bytes {input_bytes}")
                    print(f"{module_name}: fail. string: {actual_string!r} != {expected_string!r}. encoding: {guessed_encoding} != {expected_encoding}. bytes: {input_bytes}")

    for k in list(globals().keys()):
        if not k.startswith("guess_encoding_"):
            continue
        module_name = k[15:]
        module_found = False
        try:
            module = __import__(module_name)
            globals()[module_name] = module
            module_found = True
        except ModuleNotFoundError as exc:
            print(f"{module_name}: module not found. hint: pip install {module_name}")
            pass
        if module_found:
            guess_encoding = locals()[k]
            guess_encoding._name = module_name
            test(guess_encoding)
