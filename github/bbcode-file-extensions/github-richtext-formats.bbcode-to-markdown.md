https://docs.github.com/en/repositories/working-with-files/using-files/working-with-non-code-files

<blockquote>
  
Prose rendering is supported for rendered documents supported by [github/markup](https://github.com/github/markup):

- Markdown
- AsciiDoc
- Textile
- ReStructuredText
- Rdoc
- Org
- Creole
- MediaWiki
- Pod

</blockquote>

so... bad luck, bbcode

will have to use pandoc

```
$ pandoc -f bbcode -t md_strict input.bbcode
Unknown input format bbcode
```

well shit. probably cos bbcode is not well-defined...

https://www.brain-dump.org/blog/bbcode-reader-for-pandoc/

https://jondum.github.io/BBCode-To-Markdown-Converter/

https://github.com/JonDum/BBCode-To-Markdown-Converter
