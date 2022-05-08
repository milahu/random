#! /bin/sh

# why blobHash?
# * content-addressing of isolated files
#   * no need to fetch all files to verify treeHash and commitHash
#   * no need for filePath. the file is fetched ONLY by its blob hash
#   * no need for additional checksum. nix: sha256 = "...";

# github
# https://docs.github.com/en/rest/reference/git#get-a-blob
# GET https://api.github.com/repos/{owner}/{repo}/git/blobs/{blobHash}

# gitlab
# https://docs.gitlab.com/ee/api/repository_files.html
# https://docs.gitlab.com/ee/api/repositories.html#get-a-blob-from-repository
# GET /projects/:id/repository/blobs/:sha
# https://docs.gitlab.com/ee/api/repositories.html#raw-blob-content
# GET /projects/:id/repository/blobs/:sha/raw

echo github small file

commitHash=6ed65d9b5f5f40af285edb73577d2ec690d40237
base=default.nix
filePath=default.nix

expected=$base.expected
[ -e $expected ] || curl -L -o $expected https://github.com/NixOS/nixpkgs/raw/$commitHash/$filePath
# https://stackoverflow.com/questions/7225313/how-does-git-compute-file-hashes
blobHash=$(git hash-object --no-filters $expected)
echo "$blobHash  $expected (blob)"
# faed7e26354037f783701ebfee695757bd8f34da
json=$base.json
actual=$base.actual__
[ -e $json ] || curl -L -o $json https://api.github.com/repos/NixOS/nixpkgs/git/blobs/$blobHash
# success!! file was found, but response is json
jq -r .content $json | base64 -d >$actual
echo "$(sha1sum $expected) (sha1)"
echo "$(sha1sum $actual) (sha1)"
# success

# test the gitlab api on github ...
#curl -I https://api.github.com/repos/NixOS/nixpkgs/git/blobs/$blobHash/raw
# error: 404 not found



echo
echo github large file json

# large files
# https://docs.github.com/en/rest/reference/git#get-a-blob
# GET /repos/{owner}/{repo}/git/blobs/{file_sha}
# Note: This API supports blobs up to 100 megabytes in size.
# https://github.com/pnpm/pnpm/blob/main/verdaccio/storage-1.0.0.tgz
commitHash=f0007b077cc801e1a07b05485da8b5a1a5536252
filePath=verdaccio/storage-1.0.0.tgz
base=pnpm-verdaccio-storage-1.0.0.tgz
expected=$base.expected
[ -e $expected ] || curl -L -o $expected https://github.com/pnpm/pnpm/raw/$commitHash/$filePath

# https://git-scm.com/docs/git-hash-object

# https://stackoverflow.com/questions/7225313/how-does-git-compute-file-hashes
# You can also compare this to the output of echo 'Hello, World!' | git hash-object --stdin.
# Optionally you can specify --no-filters to make sure no crlf conversion happens,
# or specify --filePath=somethi.ng to let git use the filter specified via gitattributes (also @user420667).
# And -w to actually submit the blob to .git/objects (if you are in a git repo). – Tobias Kienzler

blobHash=$(git hash-object --no-filters $expected)
echo "$blobHash  $expected (blob)"
# compare ... luckily, they are all the same
#echo "blobHash = $blobHash (git hash-object --no-filters)"
#blobHash=$(git hash-object $expected)
#echo "blobHash = $blobHash (git hash-object)"
#blobHash=$(git hash-object --path verdaccio/storage-1.0.0.tgz $expected)
#echo "blobHash = $blobHash (git hash-object --path verdaccio/storage-1.0.0.tgz)"

json=$base.json
actual=$base.actual__
[ -e $json ] || curl -L -o $json https://api.github.com/repos/pnpm/pnpm/git/blobs/$blobHash
jq -r .content $json | base64 -d >$actual
echo "$(sha1sum $expected) (sha1)"
echo "$(sha1sum $actual) (sha1)"

false && {
#true && {
echo benchmark
echo
echo raw api with commitHash
time curl -L -o /dev/null https://github.com/pnpm/pnpm/raw/$commitHash/$filePath
echo
echo blob-raw api with blobHash
time curl -L -o /dev/null -H "Accept: application/vnd.github.v3.raw" https://api.github.com/repos/pnpm/pnpm/git/blobs/$blobHash
echo
echo blob-json api with blobHash
time curl -L -o /dev/null https://api.github.com/repos/pnpm/pnpm/git/blobs/$blobHash | jq -r .content | base64 -d >$actual

# result: blob api 2x slower -> overhead from json + base64
cat >/dev/null <<EOF

benchmark

raw api with commitHash
  % Total    % Received % Xferd  Average Speed   Time    Time     Time  Current
                                 Dload  Upload   Total   Spent    Left  Speed
100   178  100   178    0     0    288      0 --:--:-- --:--:-- --:--:--   288
100 36.0M  100 36.0M    0     0  2555k      0  0:00:14  0:00:14 --:--:-- 2734k

real	0m14.456s
user	0m0.527s
sys	0m0.596s

blob-raw api with blobHash
  % Total    % Received % Xferd  Average Speed   Time    Time     Time  Current
                                 Dload  Upload   Total   Spent    Left  Speed
100 36.0M  100 36.0M    0     0  2696k      0  0:00:13  0:00:13 --:--:-- 3995k

real	0m13.698s
user	0m0.678s
sys	0m0.498s

blob-json api with blobHash
  % Total    % Received % Xferd  Average Speed   Time    Time     Time  Current
                                 Dload  Upload   Total   Spent    Left  Speed
100 49.6M    0 49.6M    0     0  2720k      0 --:--:--  0:00:18 --:--:-- 3804k

real	0m18.706s
user	0m1.041s
sys	0m0.752s

EOF
}



echo
echo github large file raw
# https://stackoverflow.com/questions/21804065/github-json-api-blob-binary-data-as-base64-encoded-strings
actual=$base.actual_r
[ -e $actual ] || curl -L -o $actual -H "Accept: application/vnd.github.v3.raw" https://api.github.com/repos/pnpm/pnpm/git/blobs/$blobHash
echo "$(sha1sum $expected) (sha1)"
echo "$(sha1sum $actual) (sha1)"




echo
echo gitlab large file

# https://docs.gitlab.com/ee/api/repositories.html#get-a-blob-from-repository
# GET /projects/:id/repository/blobs/:sha
# GET /projects/:id/repository/blobs/:sha/raw

# large file
# https://gitlab.com/mildlyparallel/pscircle/-/blob/master/docs/default.png
# 1.15 MB
# download link
# https://gitlab.com/mildlyparallel/pscircle/-/raw/master/docs/default.png?inline=false
base=pscircle-default.png
expected=$base.expected
actual=$base.actual__
[ -e $expected ] || curl -o $expected "https://gitlab.com/mildlyparallel/pscircle/-/raw/master/docs/default.png?inline=false"
blobHash=$(git hash-object --no-filters $expected)
# https://docs.gitlab.com/ee/api/index.html#namespaced-path-encoding
projectPath=$(echo mildlyparallel/pscircle | sed 's,/,%2F,g')
[ -e $actual ] || curl -L -o $actual https://gitlab.com/api/v4/projects/$projectPath/repository/blobs/$blobHash/raw
echo "$blobHash  $expected (blob)"
echo "$(sha1sum $expected) (sha1)"
echo "$(sha1sum $actual) (sha1)"



exit 0

# what did NOT work ...

fileHash=$(sha1sum $expected)
fileHash=${fileHash:0:40}
# abcc252f77fba5a1ce7fffb4cd17d45032201878

# https://stackoverflow.com/questions/34456176/getting-all-versions-of-a-file-using-github-blob-api

#curl GET https://api.github.com/repos/:owner/:repo/contents/:FILE_PATH?ref=SHA
actual=default.nix.actual
[ -e $actual ] || curl -L -o $actual https://api.github.com/repos/NixOS/nixpkgs/contents/$filePath?ref=$fileHash
# error: No commit found for the ref abcc252f77fba5a1ce7fffb4cd17d45032201878
sha1sum $expected
sha1sum $actual

# GET /repos/:owner/:repo/git/blobs/:sha
actual2=default.nix.actual2
[ -e $actual2 ] || curl -L -o $actual2 https://api.github.com/repos/NixOS/nixpkgs/git/blobs/$fileHash
sha1sum $expected
sha1sum $actual2
# error: Not Found

#curl GET https://api.github.com/repos/:owner/:repo/contents/:FILE_PATH?ref=SHA
actual=default.nix.actual4
[ -e $actual ] || curl -L -o $actual https://api.github.com/repos/NixOS/nixpkgs/contents/$filePath?ref=$blobHash
# error: No commit found for the ref abcc252f77fba5a1ce7fffb4cd17d45032201878
sha1sum $expected
sha1sum $actual
# error: No commit found for the ref faed7e26354037f783701ebfee695757bd8f34da

actual=default.nix.actual5
[ -e $actual ] || curl -L -o $actual https://github.com/NixOS/nixpkgs/raw/$blobHash/$filePath
# error: 404 not found (html page)
sha1sum $expected
sha1sum $actual

actual=default.nix.actual6
[ -e $actual ] || curl -L -o $actual https://github.com/NixOS/nixpkgs/raw/$blobHash
# error: 404 not found (html page)
sha1sum $expected
sha1sum $actual

