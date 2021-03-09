// pretty-print XML in javascript
// https://stackoverflow.com/questions/376373/pretty-printing-xml-with-javascript/49458964#49458964

function formatXML(xml, tab = '\t', nl = '\n') {
  let formatted = '', indent = '';
  const nodes = xml.trim().slice(1, -1).split(/>\s*</);
  if (nodes[0][0] == '?') formatted += '<' + nodes.shift() + '>' + nl;
  for (let i = 0; i < nodes.length; i++) {
    const node = nodes[i];
    if (node[0] == '/') indent = indent.slice(tab.length); // decrease indent
    formatted += indent + '<' + node + '>' + nl;
    if (node[0] != '/' && node[node.length - 1] != '/' && node.indexOf('</') == -1) indent += tab; // increase indent
  }
  return formatted;
}

/*
// demo
// https://www.w3schools.com/xml/xml_examples.asp
const demo_xml = `<?xml version='1.0' encoding='UTF-8'?><guestbook><guest><fname>Terje</fname><lname>Beck</lname></guest><guest><fname>Jan</fname><lname>Refsnes</lname></guest><guest><fname>Torleif</fname><lname>Rasmussen</lname></guest><guest><fname>anton</fname><lname>chek</lname></guest><guest><fname>stale</fname><lname>refsnes</lname></guest><guest><fname>hari</fname><lname>prawin</lname></guest><guest><fname>Hege</fname><lname>Refsnes</lname></guest></guestbook>`;
document.write(
  '<textarea style="position: absolute; width: 100%; height: 100%; white-space: pre">' +
  formatXML(demo_xml, '  ') +
  '</textarea>'
);
*/
