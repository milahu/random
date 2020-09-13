// jsdom/test/test-generated-proxy.js

const CSSStyleDeclarationComputed = require(
  '../lib/jsdom/living/generated/CSSStyleDeclaration-computed.js');

const _window = {foo:'bar'};
const defaultStyle = {fontSize:'10px',color:'black'};
const customStyle = {fontSize:'20px'};

const p = new CSSStyleDeclarationComputed(
  _window, defaultStyle, customStyle);

console.log('fontSize = '+p.fontSize);
console.log('color = '+p.color);

console.log('font-size = '+p['font-size']);

console.dir(p); // CSSStyleDeclaration object

// throws 'read only'
p.fontSize = '40px';
