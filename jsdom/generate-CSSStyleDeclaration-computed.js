// jsdom/scripts/generate-CSSStyleDeclaration-computed.js
// custom proxy class (invisible proxy)
// to make proxy look like CSSStyleDeclaration object

// to save memory, we share methods across all instances
// by calling Object.defineProperty on the class prototype
// https://levelup.gitconnected.com/using-prototype-vs-this-in-a-javascript-class-can-help-save-memory-816636418c3e

// this is the generator. result is in
const fo = '../lib/jsdom/living/generated/CSSStyleDeclaration-computed.js';

// TODO restore DOMException.create
// TODO fix P.item function (etc?)
// TODO seal object? (no new props)
// "TODO hide these props with Object.defineProperty"
// TODO expose pseudo-props of CSSStyleDeclaration

// license is CC0-1.0
// aka "just steal my code and shut up license"

const cssstyle = require("cssstyle");
var { dashedToCamelCase } = require('cssstyle/lib/parsers');
const { writeFileSync } = require('fs');

// harvest property names
const decl = new cssstyle.CSSStyleDeclaration();
let propNames = Object.getOwnPropertyNames(
  cssstyle.CSSStyleDeclaration.prototype);

//console.log(propNames.length)
// 1304

// filter ....

// remove hidden props
propNames = propNames.filter(propName => {
  return propName[0] != '_';
});

// remove non-css props
const ignoreProps = new Set([
  'constructor',
  'getPropertyValue',
  'setProperty',
  'removeProperty',
  'getPropertyPriority',
  'getPropertyCSSValue',
  'getPropertyShorthand',
  'isPropertyImplicit',
  'item',
  'length',
  'cssText',
  // TODO more?
]);
propNames = propNames.filter(propName => {
  return !ignoreProps.has(propName);
})

// remove 370 'webkit' props
propNames = propNames.filter(propName => {
  return propName.slice(0,6) != 'webkit';
})

console.log(propNames.length)
// 922

let strOut = `\
// custom proxy class (invisible proxy)
// to make proxy look like CSSStyleDeclaration object

// generated by jsdom/scripts/generate-CSSStyleDeclaration-computed.js

const DOMException = require("domexception/webidl2js-wrapper");

class CSSStyleDeclaration {
  constructor(_window, defaultStyle, customStyle) {

    // TODO hide these props with Object.defineProperty
    this._window = _window;
    this._D = defaultStyle;
    this._C = customStyle;
    if (!(_window && defaultStyle && customStyle)) {
      throw new Error('need all arguments');
    }
    this._length = 0; // TODO
  }
}

const
P = CSSStyleDeclaration.prototype,
D = Object.defineProperty;


P.getPropertyValue = function(name) {
  return this._C.getPropertyValue(name) ||
    this._D.getPropertyValue(name);
};

P.getPropertyPriority = function() {
  return '';
};

// http://www.w3.org/TR/DOM-Level-2-Style/css.html#CSS-CSSStyleDeclaration-item
P.item = function(index) {
  index = parseInt(index, 10);
  if (index < 0 || index >= this._length) {
    return '';
  }
  return this[index];

  // TODO custom style and default style
  // will have different indices
};

`;



const funcsReadOnly = [
  'setProperty',
  'removeProperty',
];

strOut += 'P.'+funcsReadOnly.join(' =\nP.')+' =';
strOut += `
P._E = () => {
  
  // TODO restore
  /* only works with a valid window-object
  throw DOMException.create(this._window, [
    "Computed style is read-only.",
    "NoModificationAllowedError"
  ]);
  */
  
  throw new Error('read only');
};

`;



const funcsNotImplemented = [
  'getPropertyCSSValue',
  'getPropertyShorthand',
  'isPropertyImplicit',
];

strOut += 'P.'+funcsNotImplemented.join(' =\nP.')+' =';
strOut += `
()=>{throw new Error('not implemented')};

`;



propNames.forEach(n => {
  if (n.indexOf('-') == -1) {
    // camelCase
    strOut += "D(P,'"+n+
      "',{set:function(){this._E()},get:function(){return this._C."+n+"||this._D."+n+"}});\n";
  } else {
    // kebab-case interface
    // internally use camelCase
    const c = dashedToCamelCase(n);
    strOut += "D(P,'"+n+
      //"',{set:function(){this._E()},get:function(){return this._C['"+n+"']||this._D['"+n+"']}});\n";
      "',{set:function(){this._E()},get:function(){return this._C."+c+"||this._D."+c+"}});\n";
  }
});

strOut += `

module.exports = CSSStyleDeclaration;
`;

writeFileSync(fo, strOut);
