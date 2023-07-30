# markdown file extensions

the obvious file extension for markdown files is `.md`. test file: [test.md](test.md).

but there are multiple "flavors" of markdown, and ideally, github would render these different flavors.

at least, github should render "github flavored markdown" (gfm, ghmd), which is used in github issues/PRs/comments. test files: [test.gfm](test.gfm), [test.ghmd](test.ghmd). fail: these files are rendered as text files.

## workarounds

### pandoc

im using pandoc in combination with [gh2md](https://github.com/mattduck/gh2md/issues/11) to archive github issues to the git repository.

```sh
GITHUB_REPOSITORY=https://github.com/milahu/alchi
GH2MD_OUTPUT_PATH=archive/github/issues/

gh2md $GITHUB_REPOSITORY $GH2MD_OUTPUT_PATH --idempotent --multiple-files --file-extension .ghmd

find $GH2MD_OUTPUT_PATH -name '*.ghmd' -type f | while read path
do
  base="${path%.*}"
  pandoc --verbose -f gfm+hard_line_breaks -t markdown_strict "$base.ghmd" -o "$base.md"
done
```

see also: https://github.com/milahu/alchi/blob/master/.github/workflows/issues2md.yml

example output: https://github.com/milahu/alchi/tree/master/archive/github/issues
