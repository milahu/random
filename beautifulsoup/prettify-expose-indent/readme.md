# soup.prettify(indent=" ")

* https://groups.google.com/g/beautifulsoup/c/B4qryJpJqpY/m/awbl_YHIHx4J
* https://stackoverflow.com/questions/15509397/custom-indent-width-for-beautifulsoup-prettify

## similar

```py
import json
json.dumps({"a": 1}, indent="    ") == """\
{
    "a": 1
}"""
```

## demo

```py
html = """

<div><div><div>
                <div>x</div>
</div></div></div>
<pre>
                keep</pre>"""

import bs4
soup = bs4.BeautifulSoup(html, "html.parser")

soup.prettify() == """\
<div>
 <div>
  <div>
   <div>
    x
   </div>
  </div>
 </div>
</div>
<pre>
                keep</pre>"""

soup.prettify(indent="") == """\
<div>
<div>
<div>
<div>
x
</div>
</div>
</div>
</div>
<pre>
                keep</pre>"""

soup.prettify(indent="    ") == """\
<div>
    <div>
        <div>
            <div>
                x
            </div>
        </div>
    </div>
</div>
<pre>
                keep</pre>"""
```
