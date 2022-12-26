# hello

world

## GitHub Flavored Markdown Spec

https://github.github.com/gfm/#disallowed-raw-html-extension-

## html table

<table>
  <tbody>
    <tr>
      <td>a</td>
      <td>b</td>
    </tr>
    <tr>
      <td>c</td>
      <td>d</td>
    </tr>
  </tbody>
</table>

ok

## html div

<div class="asdf">
  html <i>italic</i>
</div>

ok

## html div with markdown content

<div class="asdf">

  **must** be *spaced* by [empty](#) lines `before` + after markdown ![missing image](./missing-image.svg)

</div>

ok

## html pre

<pre>
hello im preformatted
</pre>

ok

## html blockquote

<blockquote>
  hello im quoted &mdash; me
</blockquote>

ok

### html div with title (annotation)

<div title="hello">
  html <b>bold</b>
</div>

ok

### html span

fooo <span color="red">to</span> <span color="green">the</span> bar

ok

### html span with title (annotation)

yellow background color: no

blue text color: yes

fooo <span title="hello world" color="blue" background="yellow">lalalalalalalalala</span> bar

ok

## html svg

<svg viewBox="-50 -50 100 100" version="1.1" xmlns="http://www.w3.org/2000/svg">
  <circle r="50" stroke="red" />
</svg>

nope

## html img

<img src="./foo.svg">

ok

## tt deprecated html tag

<tt>tele to the type</tt>

ok

## html list

<ol>
  <li>one</li>
  <li>two</li>
</ol>

<ul>
  <li>some</li>
  <li>thing</li>
</ul>

ok

## markdown footnotes

useful[^1] to implement[^2] annotations[^2]

[^1]: very useful!

[^2]: yes, IMM PLEE MENNT

[^2]: collision in footnote id = only the first footnote is used

footnote id test a [^a] asdf [^asdf] 0a [^0a] a0 [^a0]

[^a]: a footnote

[^asdf]: asdf footnote

[^0a]: 0a footnote

[^a0]: a0 footnote

let me test a long footnote [^long-footnote]

[^long-footnote]: yes
this
is
working

here is the next paragraph

but the first word must be
in the same line as the footnote label

so this does NOT work

[^long-footnote]:
this does not work

test with escaped newline [^long-footnote-2]

[^long-footnote-2]: \
escaped newline works but is ugly,
as it adds an extra newline before the footnote description \
testing \
more \
\
backslashes \
so every backslash has the same effect as html `<br>` = hardbreak

lets try double space at line end of the footnote label [^long-footnote-3]

lets try double space at line end of the footnote label [^long-footnote-3]

[^long-footnote-3]:  
this does NOT work

footnote with multiple paragraphs: backslash [^long-footnote-4] div [^long-footnote-5] p [^long-footnote-6]

[^long-footnote-4]: para
graph
1
\
para
graph
2: ok

[^long-footnote-5]: <div>
para
graph
in div: not working, cannot mix markdown and html directly
</div>

[^long-footnote-6]: <p>
para
graph
in p: not working, cannot mix markdown and html directly
</p>
<p>

ok

### text link to footnote

aka: footnote with text reference

normally, only numbers are used as references like `[1]`

[working with extra ID](#footnote-text-link-to-footnote)[^text-link-to-footnote]

[^text-link-to-footnote]: <span id="footnote-text-link-to-footnote"></span> success! now back to: this is probably not working



not working [^text-link-to-footnote-2]

[^text-link-to-footnote-2]: success! now back to: this is probably not working 2



[not working][^text-link-to-footnote-3]

[^text-link-to-footnote-3]: success! now back to: this is probably not working 2



[not working]([^text-link-to-footnote-4])

[^text-link-to-footnote-4]: success! now back to: this is probably not working 2



[not working](^text-link-to-footnote-5)

[^text-link-to-footnote-5]: success! now back to: this is probably not working 2



### footnote in html

<div>
  div content unspaced [^footnote-div-unspaced] = no
</div>

<div>

  div content spaced [^footnote-div-spaced] = ok

</div>

[^footnote-div-unspaced]: asdf

[^footnote-div-spaced]: foo

### mdbook-footnote

https://github.com/daviddrysdale/mdbook-footnote

Normal text{{footnote: Or is it?}} in body.

no, as expected, this is non-standard

## markdown heading ids extension

### My Great Heading 1 {#custom-id}

[link to  My Great Heading 1](#custom-id)

no

## markdown heading all html

<h3 id="some-custom-heading-id-a">heading</h3>

[link to heading](#some-custom-heading-id-a)

<h3 id="some-custom-heading-id-b">heading</h3>

[link to heading](#some-custom-heading-id-b)

## markdown heading ids html

https://gist.github.com/asabaylus/3071099

### <a name="custom-id-html-a-name-headlink"/>[heading](#custom-id-html-a-name-headlink)

link in heading, and here:

[link to custom-id-html-a-name-headlink](#custom-id-html-a-name-headlink)

... this is probably the best solution

note: no whitespace around the `<a id="...">` tag

### <a id="custom-id-html-a-id"/>heading

[link to custom-id-html-a-id](#custom-id-html-a-id)

### heading<a id="custom-id-html-a-id-after"/>

[link to custom-id-html-a-id-after](#custom-id-html-a-id-after)

### <a name="custom-id-html-a-name"/>heading

[link to custom-id-html-a-name](#custom-id-html-a-name)

## definition lists

First Term
: This is the definition of the first term.

Second Term
: This is one definition of the second term.
: This is another definition of the second term.

no

## highlight

I need to highlight these ==very important words==.

no

## html mark

I need to highlight these <mark>very important words</mark>.

no, not visible

## html attributes with empty lines

this breaks

<div
title="a
b

c

d"
>hello</div>

## annotation as html hidden element

some text [with annotation](#note-example-annotation-in-hidden-div)

the annotation content

is stored

in a html `<div hidden>` element

<div hidden="hidden" id="note-example-annotation-in-hidden-div">

  hii
  ddd
  eeee
  nnnn

</div>

no. div is not hidden on github

## annotation as html details

some text [with annotation](#note-example-annotation-in-details)

the annotation content

is stored

in a html `<details>` element

<details id="note-example-annotation-in-details">

  dee
  tail
  ss
  ss

</details>

yes, this is better than "hidden" div

## annotation as html details, open details on click

click link to open details

idea: add an empty `<span id="x">` inside `<details>`

<a href="#note-details-clickable-0">clickme 0</a>

<a href="#note-details-clickable-1">clickme 1</a>

<a href="#note-details-clickable-2">clickme 2</a>

<a href="#note-details-clickable-3">clickme 3</a>

<details id="note-details-clickable-0">
  <summary>
    this is a clickable annotation
  </summary>
  <!--
    not working on github. details are not open on click
  -->
  <span id="note-details-clickable-1"></span>
  <a name="note-details-clickable-2">
  <div id="note-details-clickable-3">
    blah
  </div>
  blah
  blah
  blah
</details>

no. details are not open on click

but this works in mdbook

## annotation as html details, open details on click, focusable with tabindex attribute

trick: make details focusable with tabindex="-1" attribute, based on https://allyjs.io/data-tables/focusable.html and https://stackoverflow.com/questions/1599660/which-html-elements-can-receive-focus

[clickme yeah](#note-details-clickable-tabindex)

<!-- todo add tabindex/onfocus in dynamic or static render with selector details.annotation -->

<details class="annotation" id="note-details-clickable-tabindex" tabindex="-1" onfocus="if (!this.open) { this.open = true; }" style="border: 1px solid grey; margin: 1em 0px; padding: 0.5em 0.5em 0.5em 1em">
<summary>sum sum sum</summary>

here
goes
the bla
bla
bla

</details>

not working on github

todo: produce this code in rendering from markdown to html. its pretty!

## annotation as inline html details

`display="inline"` has no effect &rarr; details is block element

some text [with inline annotation](#note-example-annotation-in-inline-details) <details display="inline" id="note-example-annotation-in-inline-details">

  dee
  tail
  ss
  ss

</details> and then the text continues

yes, this is better than "hidden" div

but its more invasive than footnotes

## html pre with span color

useful for manual syntax highlighting

<pre>
<span color="red">hello</span> world
</pre>

ok

## xml tags

<asdf>
  xml asdf content
</asdf

<nw>
  xml nowrap content
</nw>

ugly, better use div or span

## html style

<style>
  * { color: red; }
</style>

no, of course not

## html script

<script>
  window.location = 'https://asdf.com/';
</script>

no, of course not

## syntax highlighting

https://docs.github.com/en/get-started/learning-about-github/github-language-support

https://docs.github.com/en/get-started/writing-on-github/working-with-advanced-formatting/creating-and-highlighting-code-blocks

https://github.com/github/linguist/blob/master/lib/linguist/languages.yml

### nix

```nix
[ 1 2 ] ++ [ 3 4 ]
```

### haskell

```hs
attrByPath :: [String] -> Any -> AttrSet -> Any
```

### console

```console
$ echo hello
hello

$ echo world
world
```

### bash

```sh
function main() {
  echo hello $1
}

main world
```

## inline images

not working. all images are display:block

the only attributes that work on images are align="left" align="right" align="top" align="bottom"

github stylesheet has

```css
img, svg, video, canvas, audio, iframe, embed, object {
    display: block;
    vertical-align: middle;
}
```

... which we can not override with html attributes like `display="inline"`

biggrin ![](biggrin.png) markdown
biggrin <img src="biggrin.png"> html
biggrin <img src="biggrin.png" display="inline"> display="inline"
biggrin <img src="biggrin.png" display="inline-block"> display="inline-block"
biggrin <img src="biggrin.png" align="right"> align="right"
biggrin <img src="biggrin.png" align="left"> align="left"
biggrin <img src="biggrin.png" align="top"> align="top"
biggrin <img src="biggrin.png" align="bottom"> align="bottom"
biggrin <img src="biggrin.png" align="char"> align="char"
biggrin <img src="biggrin.png" align="center"> align="center"
biggrin <img src="biggrin.png" align="center middle"> align="center middle"
biggrin <img src="biggrin.png" align="middle"> align="middle"
biggrin <img src="biggrin.png" float="left"> float="left"
biggrin <img src="biggrin.png" width="16" height="16"> width height
biggrin <img src="biggrin.png" compact="true"> compact="true"
biggrin <img src="biggrin.png" compact> compact
biggrin <img src="biggrin.png" alt=":D"> alt=":D"
biggrin <img src="biggrin.png" border="0"> border="0"
biggrin <img src="biggrin.png" hspace="0"> hspace="0"
biggrin <img src="biggrin.png" ismap="true"> ismap="true"
biggrin <img src="biggrin.png" ismap="false"> ismap="false"
biggrin <img src="biggrin.png" name="biggrin"> name="biggrin"
biggrin <img src="biggrin.png" vspace="0"> vspace="0"
biggrin <table><tbody><tr><td><img src="biggrin.png"></td></tr></tbody></table> table
biggrin <div><img src="biggrin.png"></div> div
biggrin <span><img src="biggrin.png"></span> span
biggrin <span float="left"><img src="biggrin.png"></span> span  float="left"
