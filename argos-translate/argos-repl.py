#!/usr/bin/env python3

# argos repl
# reduce translation time
# from (13 + 8 + 2) = 23 seconds to 2 seconds
# https://github.com/argosopentech/argos-translate

src_lang = "en"
dst_lang = "es"

import time

# If the readline module was loaded, then input() will use it
# to provide elaborate line editing and history features.
import readline

# 13 seconds
print("importing argostranslate... ", end="")
t1 = time.time()
import argostranslate.translate
t2 = time.time()
print(f"done in {(t2 - t1):.1f} seconds")

# hide warnings: "Language %s package %s expects mwt, which has been added"
import logging
logging.getLogger("stanza").disabled = True

prompt_format = "{}: "
src_prompt = prompt_format.format(src_lang)
dst_prompt = prompt_format.format(dst_lang)

# load the language model
# 8 seconds
print("loading the language model... ", end="")
t1 = time.time()
argostranslate.translate.translate("hello", src_lang, dst_lang)
t2 = time.time()
print(f"done in {(t2 - t1):.1f} seconds")

print()

while True:
    try:
        src = input(src_prompt)
    except (EOFError, KeyboardInterrupt):
        break
    # translate
    # 2 seconds
    t1 = time.time()
    dst = argostranslate.translate.translate(src, src_lang, dst_lang)
    dt = time.time() - t1
    print(dst_prompt + dst + "\n")
    #print(dst_prompt + dst + "\n" + f"dt = {dt}\n") # debug: print time
