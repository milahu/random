#!/usr/bin/env python3

# hate discorse

# discourse is such a piece of shit software
# no surprise that fascists love discourse
# because discourse helps fascist to
# lie, hide, censor, confuse, obfuscate, mystify

import os
import re
import sys
import json

inn = sys.argv[1]

with open(inn) as fd:
    str = fd.read()

r = '<div class="hidden" id="data-preloaded" data-preloaded="(.*)"'
m = re.search(r, str)
assert m
str = m.group(1)
str = str.replace("&quot;", '"')

data = json.loads(str)

# find key "topic_15231"
key = list(filter(lambda k: k.startswith("topic_"), data.keys()))[0]
data = json.loads(data[key])

import urllib.request

if 0:
    # debug
    str = json.dumps(data, indent=2)


else:
    def fetch(url, name):
        if not os.path.exists(name):
            print(f"fetching {name} from {url}", file=sys.stderr)
            urllib.request.urlretrieve(url, name)
    def format_post(post):
        body = post["cooked"]
        # sample: https://cdn.tarnkappe.info/forum/user_avatar/tarnkappe.info/milahu/60/17020_2.png
        r = r"(https://cdn.tarnkappe.info/forum/user_avatar/tarnkappe.info/([^/]+)/([0-9]+)/([0-9_]+.png))"
        def f(m):
            url = m.group(1)
            name = "avatar." + ".".join(m.groups()[1:])
            fetch(url, name)
            return name
            #return f'"{name}"'
        body = re.sub(r, f, body)
        avatar = post["avatar_template"].replace("/{size}/", "/120/")
        avatar_url = "https://cdn.tarnkappe.info" + avatar
        # sample: /forum/user_avatar/tarnkappe.info/ghandy/120/16973_2.png
        r = r"/forum/user_avatar/tarnkappe.info/([^/]+)/([0-9]+)/([0-9_]+.png)"
        avatar = re.sub(r, r"avatar.\1.\2.\3", avatar)
        fetch(avatar_url, avatar)
        # samples:
        # https://cdn.tarnkappe.info/forum/uploads/default/original/2X/4/4d4e6f9a145d72437019ec8fff87d74ef915bd1a.png
        # https://cdn.tarnkappe.info/forum/uploads/default/optimized/2X/4/4d4e6f9a145d72437019ec8fff87d74ef915bd1a_2_636x500.png
        #r = r"https://cdn.tarnkappe.info/forum/uploads/default/[^/]+/[^/]+/[0-9a-f]/([0-9a-f]{40}(?:_[0-9]+_[0-9x]+)?.png)"
        r = r'src="(https://cdn.tarnkappe.info/forum/uploads/[^"]+/([^"/]+))"'
        def f(m):
            url = m.group(1)
            name = "upload." + m.group(2)
            fetch(url, name)
            return f'src="{name}"'
        body = re.sub(r, f, body)
        # sample: https://cdn.tarnkappe.info/forum/images/emoji/apple/slight_smile.png?v=12
        r = r'"(https://cdn.tarnkappe.info/forum/images/emoji/([^/]+)/([^/?"]+)(?:\?v=[0-9]+)?)"'
        def f(m):
            url = m.group(1)
            name = "emoji." + ".".join(m.groups()[1:])
            fetch(url, name)
            #return name
            return f'"{name}"'
        body = re.sub(r, f, body)
        str = (
            '<img src="' + avatar + '">' +
            "\n<br>\n" +
            post["created_at"] +
            "\n<br>\n" +
            post["username"] +
            "\n<br>\n" +
            body
        )
        return str

    str = "\n\n<hr>\n\n".join(
        map(
            format_post,
            data["post_stream"]["posts"]
        )
    )

if 0:
    out = inn + ".out.json"
    print("writing", out)
    with open(out, "w") as fd:
        json.dump(data, fd, indent=2)

else:
    print(str)
