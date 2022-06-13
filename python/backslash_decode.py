# https://stackoverflow.com/questions/1885181/how-to-un-escape-a-backslash-escaped-string

# custom string parser to decode only some backslash-escapes, in this case \" and \'

def backslash_decode(src):
    "decode backslash-escapes"
    slashes = 0 # count backslashes
    dst = ""
    for loc in range(0, len(src)):
        char = src[loc]
        if char == "\\":
            slashes += 1
            if slashes == 2:
                dst += char # decode backslash
                slashes = 0
        elif slashes == 0:
            dst += char # normal char
        else: # slashes == 1
            if char == '"':
                dst += char # decode double-quote
            elif char == "'":
                dst += char # decode single-quote
            else:
                dst += "\\" + char # keep backslash-escapes like \n or \t
            slashes = 0
    return dst


# test

src = "a" + "\\\\" + r"\'" + r'\"' + r"\n" + r"\t" + r"\x" + "z" # input
exp = "a" + "\\"   +  "'"  +  '"'  + r"\n" + r"\t" + r"\x" + "z" # expected output

res = backslash_decode(src)

print(res)
assert res == exp
