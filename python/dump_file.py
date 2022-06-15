# https://stackoverflow.com/questions/43197657/printing-out-each-line-from-file-with-line-number-python

def dump_file(file):
    "print file contents with line numbers"
    with open(file, "r") as fh:
        for num, line in enumerate(fh, start=1):
            print(f"{file}:{num}: {line}", end="")
