/**
* parse html document from http response. also handle non-utf8 data
* @param {Response} response
* @return {Document}
*/
async function docOfResponse(response) {
  // example content-type: text/html; charset=ISO-8859-1
  const type = response.headers.get("content-type").split(";")[0] || "text/html"
  const charset = (response.headers.get("content-type").match(/;\s*charset=(.*)(?:;|$)/) || [])[1]
  let html = ""
  if (charset && charset != "UTF-8") { // TODO check more? utf-8, utf8, UTF8, ...
    const decoder = new TextDecoder(charset)
    const buffer = await response.arrayBuffer()
    html = decoder.decode(buffer) // convert to utf8
  }
  else {
    html = await response.text()
  }
  return new DOMParser().parseFromString(html, type)
}

/*
// demo
const response = await fetch("https://github.com/")
const doc = await docOfResponse(response)
const title = doc.querySelector("title")
console.log(title)
*/

/*
published at
https://stackoverflow.com/questions/38292228/how-to-parse-non-utf8-xml-in-browsers-with-javascript
*/
