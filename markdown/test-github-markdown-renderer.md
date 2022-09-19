# hello

world

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

### html div with title

<div title="hello">
  html <b>bold</b>
</div>

ok

### html span

fooo <span color="red">to</span> <span color="green">the</span> bar

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

### footnote in html

<div>
  div content unspaced [^footnote-div-unspaced] = no
</div>

<div>

  div content spaced [^footnote-div-spaced] = ok

</div>

[^footnote-div-unspaced]: asdf

[^footnote-div-spaced]: foo
  
## markdown heading ids

### My Great Heading 1 {#custom-id}

[link to  My Great Heading 1](#custom-id)

no

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
