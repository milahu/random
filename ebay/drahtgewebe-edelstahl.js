/*
npm init -y
npm install node-html-parser
*/

const fs = require('fs')
const { parse } = require('node-html-parser')

const result = [];

// files p.1.html p.2.html p.3.html were downloaded with web browser (dynamic content ...)
/*
https://www.ebay.de/sch/m.html?_nkw=&_armrs=1&_from=&_ssn=kijaporz62&_pgn=1&_skc=200&rt=nc
https://www.ebay.de/sch/m.html?_nkw=&_armrs=1&_from=&_ssn=kijaporz62&_pgn=2&_skc=200&rt=nc
https://www.ebay.de/sch/m.html?_nkw=&_armrs=1&_from=&_ssn=kijaporz62&_pgn=3&_skc=200&rt=nc
*/

for (const p of [1, 2, 3]) {
  const infile = `p.${p}.html`;
  const insrc = fs.readFileSync(infile, 'utf8')
  const root = parse(insrc);

  root.querySelectorAll('#ListViewInner > li').forEach(li => {
    const a = li.querySelector('h3 > a');
    const title = a.innerHTML.replace(/<wbr>/g, '');
    const linkLong = a.getAttribute('href');
    const ebayId = linkLong.split('/').pop().split('?').shift();
    const link = `https://www.ebay.de/itm/${ebayId}`;
    const sizeMatch = title.match(/([0-9]+) ?([cm]?m) ?x ?([0-9]+) ?([cm]?m)(?: 1qm)?$/);
    const size = (sizeMatch
      ? `${sizeMatch[1]} ${sizeMatch[2]} x ${sizeMatch[3]} ${sizeMatch[4]}`
      : title
    );

    const priceEur = parseFloat(li.querySelector('ul.lvprices > li.lvprice > span.bold').innerHTML.match(/<b>EUR<\/b> ([0-9]+,[0-9]+)/)[1].replace(',', '.'));

    const match = title.match(/Edelstahl.*? *(?:([0-9]+[0-9,]*) *mm +Maschen.*? *([0-9]+[0-9,]*) *mm Draht.*?|([0-9]+[0-9,]*) *mm +Draht.*? *([0-9]+[0-9,]*) *mm Masche.*?)/i);

    const round = num => parseFloat(num.toFixed(3));

    if (match) {
      const masche = parseFloat((match[1] || match[4]).replace(',', '.'));
      const draht = parseFloat((match[2] || match[3]).replace(',', '.'));
      const partikel = round(masche - draht);

      result.push({ title, link, ebayId, priceEur, masche, draht, partikel, size });
    }
    else {
      console.log(`ignore: ${title}`);
    }

  });
}



/*

[five piece sifting pans](https://www.amazon.com/dp/B00C7YCQIQ/)
[1/30 inch sifting pan](https://www.amazon.com/dp/B00BP3NRZG/)

1. 1/2 inch mesh - 1.4 mm wire = 9.520mm - 1.4 mm = 8.12 mm particle size
2. 1/4 inch mesh - 0.95 mm wire = 4.760mm - 0.95 mm = 3.81 mm particle size
3. 1/8 inch mesh - 0.6 mm wire = 2.380mm - 0.6 mm = 1.78 mm particle size
4. 1/12 inch mesh - 0.45 mm wire = 1.680mm - 0.45 mm = 1.23 mm particle size
5. 1/20 inch mesh - 0.35 mm wire = 0.840mm - 0.35 mm = 0.49 mm particle size
6. 1/30 inch mesh - 0.3 mm wire = 0.600mm - 0.3 mm = 0.3 mm particle size

*/

const wantedParticles = [
  8.12,
  3.81,
  1.78,
  1.23,
  0.49,
  0.3,
].sort();

const partikelToleranz = 0.2;



const sortedResult =
  result
    .sort((a, b) => (a.partikel - b.partikel))
;

// sort by partikel (ascending)
const filteredResult =
  sortedResult
    .filter(({ partikel }) => wantedParticles.find(p => Math.abs(p - partikel) <= partikelToleranz))
    //.sort((a, b) => (a.partikel - b.partikel))
;

const foundParticles = Array.from(filteredResult.reduce((acc, { partikel }) => {
  acc.add(partikel);
  return acc;
}, new Set()).values());

// TODO group by particle, sort by price

//const printResult = filteredResult;
const printResult = sortedResult;

printResult.forEach(({ title, link, ebayId, priceEur, masche, draht, partikel, size }) => {
  //console.log(`p ${partikel} <- m ${masche} - d ${draht} @ ${title} = ${link}`)
  //console.log(`* p ${partikel} <- m ${masche} - d ${draht} @ [${title}](${link}) (${priceEur} EUR)`) // markdown
  //console.log(`* p ${partikel} <- m ${masche} - d ${draht} @ <a href="${link}" title="${title}">ebay ${ebayId}</a> -> ${priceEur} EUR`) // markdown
  //console.log(`* p ${partikel} <- m ${masche} - d ${draht} @ [... ${title.slice(-20)}](${link}) (${priceEur} EUR)`) // markdown
  console.log(`* p ${partikel} <- m ${masche} - d ${draht} @ [${size}](${link}) (${priceEur} EUR)`) // markdown
});

const allParticles = Array.from(result.reduce((acc, { partikel }) => {
  acc.add(partikel);
  return acc;
}, new Set()).values()).sort();

const todoParticles = wantedParticles.slice();
const combinedParticles = allParticles.reduce((acc, p, idx, arr) => {
  if (wantedParticles.includes(p)) {
    acc.push(`*${p}*`); // exact match
    todoParticles.shift();
  }
  else {
    if (p > todoParticles[0] && todoParticles[0] > arr[idx - 1]) {
      //acc.push(`(${todoParticles[0]})`); // no exact match
      acc.push(`[${todoParticles[0]}]`); // no exact match
      todoParticles.shift();
    }
    acc.push(p);
  }
  return acc;
}, [])


console.log(`wantedParticles: ${wantedParticles.join(' ')}`);
//console.log(`foundParticles: ${foundParticles.join(' ')}`);
console.log(`allParticles: ${allParticles.join(' ')}`);
console.log(`combinedParticles: ${combinedParticles.join(' ')}`);

/*

combinedParticles:

0.025 0.035 0.044 0.045 0.05 0.08 0.09 0.1 0.15 0.18 0.2 
*0.3* 
0.4 0.42 
0.47 0.48 (0.49) 0.5 
0.6 0.7 0.85 0.96 1 1.1 
1.15 (1.23) 1.5 (1.78) 1.8 
2.3 3 
(3.81) 4 
5.3 7 
(8.12) 8.5

*/
