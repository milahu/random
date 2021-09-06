/*
  patch-svelte-compiler-sources.js

  replace array push with reassign

  TODO use sourcemaps to find source files

  usage:
  cp patch-svelte-compiler-sources.js node_modules/svelte/
  cd node_modules/svelte
  # install deps of svelte
  pnpm install
  # install script deps
  pnpm i -g tosource magic-string glob typescript
  export NODE_PATH=`pnpm root -g`
  # run script
  node patch-svelte-compiler-sources.js

  license is CC0-1.0
  warranty is none

*/

// replaceMethod
//   origin: a.push(...a1, ...a2, e, ...a3); // error: Max Stack Size Exceeded
//   spread: a = [...a1, ...a2, e, ...a3];
//   concat: a = a1.concat(a2, [e], a3);
//   performance is equal on nodejs (spread vs concat)

//const replaceMethod = "spread";
//const replaceMethod = "pushArray"; // TODO implement
/*
Array.prototype._concat_inplace = function(other) { // aka _push_array
  for (let i = 0; i < other.length; i++) {
    this.push(other[i]);
  }
  return this; // chainable
};

array1._concat_inplace(array2)._concat_inplace(array3);
*/
const replaceMethod = "concat";

const funcName = "push";

const do_write = true; // write output file

//const test_input_file = false;
//const test_input_file = "test_typescript.ts";



const acorn_parse = require("acorn").parse;
const estree_walk = require("estree-walker").walk;
const node_tosource = require("tosource");
const MagicString = require("magic-string");
const fs = require("fs");
const glob = require("glob");
const path = require("path");
const ts = require("typescript");
//const { SourceMapConsumer } = require('source-map-js'); // https://github.com/7rulnik/source-map
const { SourceMapConsumer } = require('source-map-closest-match'); // allow fuzzy search for nearest neighbor
const { getLocator } = require('locate-character'); // https://github.com/Rich-Harris/locate-character
const child_process = require('child_process'); // git clone



function exec(cwd, cmd, options = {}) {

  if (options.produceFiles) {
    for (const f of options.produceFiles) {
      const p = `${cwd}/${f}`;
      if (fs.existsSync(p)) {
        console.log(`\nfile exists: ${p}`)
        console.log(`ignore: ${cwd} $ ${cmd}\n`);
        return
      }
    }
  }

  fs.mkdirSync(cwd, { recursive: true });

  let result;
  try {
    console.log(`\n${cwd} $ ${cmd}\n`);
    result = child_process.execSync(cmd, { cwd, windowsHide: true, ...options });
  }
  catch (error) {
    if (options.allowFail) return error;
    throw error;
  }

  if (options.produceFiles) {
    for (const f of options.produceFiles) {
      const p = `${cwd}/${f}`;
      if (!fs.existsSync(p)) {
        throw `error: failed to generate ${p}`
      }
    }
  }

  return result;
}



// clone svelte
exec('src', `git clone --depth 1 https://github.com/sveltejs/svelte.git`, {
  produceFiles: [ 'svelte', 'svelte/package-lock.json' ]
})

// install deps with pnpm
exec('src/svelte', `pnpm import`, {
  allowFail: true, // ignore error: sh: rollup: command not found https://github.com/pnpm/pnpm/issues/3750
  produceFiles: [ 'pnpm-lock.yaml' ],
})

// install deps with pnpm
// ignore-scripts: dont download puppeteer (only needed to test web-components)
exec('src/svelte', `pnpm install --ignore-scripts`, {
  produceFiles: [ 'node_modules' ],
})

// build svelte
exec('src/svelte', `npm run build`, {
  produceFiles: [ 'compiler.js', 'compiler.js.map', 'compiler.mjs', 'compiler.mjs.map' ]
})



// locate bugs in src/svelte/compiler.js

var code_old = fs.readFileSync('src/svelte/compiler.js', 'utf8');
var locate = getLocator(code_old, { offsetLine: 1 }); // lines are one-based and columns are zero-based in SourceMapConsumer
var smc = new SourceMapConsumer(fs.readFileSync('src/svelte/compiler.js.map', 'utf8'));


const ast = acorn_parse(
  code_old, {
  // ecmaVersion: 10, // default in year 2019
  sourceType: 'module',
});

estree_walk( ast, {
  enter: function ( node, parent, prop, index ) {

    // node must be array.push()
    if (
      node.type !== 'CallExpression' ||
      node.callee === undefined ||
      node.callee.property === undefined ||
      node.callee.property.name !== funcName
    ) { return; }

    // argument list must include spread operators
    if (node.arguments.find(
      a => (a.type == 'SpreadElement')) === undefined)
    { return; }

    const nodeSrc = code_old.substring(node.start, node.end);

    const pushObj = node.callee.object;
    const arrayName = code_old.substring(pushObj.start, pushObj.end);

    const pushProp = node.callee.property;

    var nodeLoc = locate(node.start);

    var origLoc = smc.originalPositionFor(nodeLoc);

    //console.dir({ nodeSrc, nodeLoc, origLoc, pushObj, arrayName, pushProp })

    console.log(`TODO patch source file: ${origLoc.source}`)

}});

process.exit();



process.exit(); // debug

// reverse map, typescript only gives numbers
ts_SyntaxKind_back = Object.keys(ts.SyntaxKind).reduce((acc, key) => {
  const val = ts.SyntaxKind[key];
  if (val in acc) {
    acc[val] += " OR " + key;
  } else {
    acc[val] = key;
  }
  return acc;
}, {});



// debug helper
// use: async function f() { await sleep(2000); }
function sleep(ms) {
  return new Promise(resolve => setTimeout(resolve, ms));
}



function patch_file(input_file) {

  const isTypeScript = (input_file.substr(-3) == '.ts');
  console.log(`read file: ${input_file} [typescript ${isTypeScript}]`)

  const backup_file = input_file + ".orig";

  if (fs.existsSync(backup_file)) {
    console.log('error: backup file exists. run this script only once');
    return;
  }

  // input
  const code_old = fs.readFileSync(input_file, 'utf8');

  // output
  let code = new MagicString(code_old);

  // arrays to make variable (not constant)
  let arrayNameList = [];



  // first patch pass
  // replace array.push() with reassign

  if (isTypeScript) {

    const ts_source_file = ts.createSourceFile(
      path.basename(input_file), // file name
      code_old, // code
      ts.ScriptTarget.Latest, // ts.ScriptTarget.ES2015,
      true // setParentNodes
    );

    function ts_transformer(ts_context) {
      // ts_context is needed by ts.visitEachChild

      function ts_visitor(ts_node) {

        //console.log(`ts_node.kind = ${ts_SyntaxKind_back[ts_node.kind]} (${ts_node.kind})`);
        //console.dir(ts_node);

        if (
          ts_node.kind == ts.SyntaxKind.CallExpression &&
          ts_node.expression &&
          ts_node.expression.name &&
          ts_node.expression.name.escapedText == funcName &&
          ts_node.arguments.find((arg) => (arg.kind == ts.SyntaxKind.SpreadElement)) !== undefined
        ) {

          //console.log(`ts_node.kind = ${ts_SyntaxKind_back[ts_node.kind]} (${ts_node.kind})`);
          //console.dir(ts_node);

          const src_node = code_old.substring(ts_node.pos, ts_node.end);
          //console.log(`src_node = ${src_node}`);

          const arrayNameSpaced = code_old.substring(
            ts_node.pos, // too far left, includes whitespace
            (ts_node.expression.name.pos - 1)
          );
          const lenWhitespace = arrayNameSpaced.match(/^\s*/)[0].length;
          const arrayName = arrayNameSpaced.substring(lenWhitespace);
          arrayNameList.push(arrayName);

          // position of "array.push(..."
          const idxCallStart = ts_node.pos + lenWhitespace;

          // find "(" bracket after .push
          const idxCallBracketOpen = ts_node.pos + src_node.indexOf(
            "(", (ts_node.expression.name.pos - ts_node.pos)
          );

          // find ")" bracket after .push arguments
          const idxBracketClose = ts_node.pos + src_node.lastIndexOf(")");

          if (replaceMethod == "spread") {
            // push --> reassign spread

            let trailSpace = " ";
            if (
              code_old[idxCallBracketOpen + 1] == "\n" ||
              code_old[idxCallBracketOpen + 1] == "\r"
            ) {
              // remove trailing space before newline
              //trailSpace = "__SKIP_TRAIL_SPACE__"; // debug
              trailSpace = "";
            }
            code.overwrite(
              (ts_node.expression.name.pos - 1),
              (idxCallBracketOpen + 1),
              " = [..."+arrayName+","+trailSpace
            );

            // patch closing bracket
            code.overwrite(idxBracketClose, (idxBracketClose + 1), "]");
          }

          if (replaceMethod == "concat") {
            // push --> reassign concat
            // ".push" --> " = array.concat"

            code.overwrite(
              (ts_node.expression.name.pos - 1),
              (idxCallBracketOpen + 1),
              " = "+arrayName+".concat("
            );

            // patch arguments of .concat()
            ts_node.arguments.forEach(a => {
              if (a.kind == ts.SyntaxKind.SpreadElement) {
                // unspread: ...array --> array
                const spreadArgSrc = code_old.substring(a.expression.pos, a.expression.end);
                //console.log('spread argument: '+spreadArgSrc);
                code.overwrite(a.pos, a.end, spreadArgSrc);

              } else {
                // enlist: identifer --> [identifer]
                let argSrc = code_old.substring(a.pos, a.end);
                const whiteSpaceLen = argSrc.match(/^\s*/)[0].length;
                const realPos = a.pos + whiteSpaceLen;
                argSrc = code_old.substring(realPos, a.end);

                //console.log('non spread argument: '+argSrc);
                code.overwrite(realPos, a.end, "["+argSrc+"]");
              }
            });
          }
        }

        // recurse
        return ts.visitEachChild(ts_node, ts_visitor, ts_context);
      }

      return function (ts_root_node) {
        return ts.visitNode(ts_root_node, ts_visitor);
      }
    }

    new_ts_node = ts.transform(
      ts_source_file,
      [ts_transformer] // array of transformers
    );

  }

  else {
    // javascript

    const ast = acorn_parse(
      code_old, {
      // ecmaVersion: 10, // default in year 2019
      sourceType: 'module',
    });

    estree_walk( ast, {
      enter: function ( node, parent, prop, index ) {

        // node must be array.push()
        if (
          node.type !== 'CallExpression' ||
          node.callee === undefined ||
          node.callee.property === undefined ||
          node.callee.property.name !== funcName
        ) { return; }

        // argument list must include spread operators
        if (node.arguments.find(
          a => (a.type == 'SpreadElement')) === undefined)
        { return; }

        const nodeSrc = code_old.substring(node.start, node.end);

        const pushObj = node.callee.object;
        const arrayName = code_old.substring(pushObj.start, pushObj.end);

        const pushProp = node.callee.property;

        arrayNameList.push(arrayName);

        // patch .push(

        if (replaceMethod == "spread") {
          // push --> assign array

          // find "(" bracket after .push
          const pushPropLen = code_old.substring(pushProp.start, node.end).indexOf("(");

          code.overwrite(
            (pushProp.start - 1),
            (pushProp.start + pushPropLen + 1),
            //" /* PATCHED */ = [..."+arrayName+", "
            " = [..."+arrayName+", "
          );

          // patch closing bracket
          const closeIdx = node.start + nodeSrc.lastIndexOf(")");
          code.overwrite(closeIdx, (closeIdx + 1), "]");
        }

        if (replaceMethod == "concat") {
          // push --> assign concat
          // ".push" --> " = array.concat"
          code.overwrite(
            (pushProp.start - 1),
            pushProp.end,
            //" /* PATCHED */ = "+arrayName+".concat");
            " = "+arrayName+".concat");

          // patch arguments of .concat()
          node.arguments.forEach(a => {
            if (a.type == 'SpreadElement') {
              // unspread: ...array --> array
              const spreadArgSrc = code_old.substring(a.argument.start, a.argument.end);
              //console.log('spread argument: '+spreadArgSrc);
              code.overwrite(a.start, a.end, spreadArgSrc);

            } else {
              // enlist: element --> [element]
              const argSrc = code_old.substring(a.start, a.end);
              //console.log('non spread argument: '+argSrc);
              code.overwrite(a.start, a.end, "["+argSrc+"]");
            }
          });
        }

    }});
  }



  // new magicstring with new positions
  code = new MagicString(code.toString());



  function filterUnique(value, index, array) { 
    return array.indexOf(value) === index;
  }

  function filterNoProp(value) { 
    return value.indexOf(".") == -1;
  }

  arrayNameList = arrayNameList
  .filter(filterUnique)
  .filter(filterNoProp);

  //console.log('patching const declarations:');
  //console.log(arrayNameList.join('\n'));



  // second patch pass
  // replace const with let  declaration
  // TODO javascript
  // TODO less brute force:
  // find declaration in parent node of array.push()

  if (isTypeScript) {

    const ts_source_file = ts.createSourceFile(
      path.basename(input_file), // file name
      code.toString(), // result from first patch pass
      ts.ScriptTarget.Latest, // ts.ScriptTarget.ES2015,
      true // setParentNodes
    );

    function ts_transformer(ts_context) {
      // ts_context is needed by ts.visitEachChild

      function ts_visitor(ts_node) {

        //console.log(`ts_node.kind = ${ts_SyntaxKind_back[ts_node.kind]} (${ts_node.kind})`);
        //console.dir(ts_node);

        if (
          ts_node.kind == ts.SyntaxKind.VariableDeclarationList &&
          ts_node.flags == 2 // const declaration
        ) {

          // find variable to patch
          // arrayNameList was set in first patch pass
          const foundVar = ts_node.declarations.find(
            (variableDeclaration) => {
              //console.log(`variableDeclaration.name.text = ${variableDeclaration.name.text}`);
              return arrayNameList.includes(
                variableDeclaration.name.text
              );
          });
          if (foundVar == undefined) {
            // skip this node
            // recurse
            return ts.visitEachChild(ts_node, ts_visitor, ts_context);
          }

          // find real pos
          // ts_node.pos can be left-padded with whitespace
          const nodeSrc = code_old.substr(ts_node.pos, ts_node.end);
          const whiteSpaceLen = nodeSrc.match(/^\s*/)[0].length;
          const realPos = ts_node.pos + whiteSpaceLen;

          //console.log('patching const declaration: ' + code_old.substr(realPos, ts_node.end));

          // const --> let
          code.overwrite(
            realPos,
            (realPos + 5), // 5 = "const".length
            'let'
          );

        }

        // recurse
        return ts.visitEachChild(ts_node, ts_visitor, ts_context);
      }

      return function (ts_root_node) {
        return ts.visitNode(ts_root_node, ts_visitor);
      }
    }

    new_ts_node = ts.transform(
      ts_source_file,
      [ts_transformer] // array of transformers
    );
  }

  else {
    // javascript
    // TODO
  }

  /* old code. brute force replace
  arrayNameList.filter(filterUnique).forEach(arrayName => {
    if (arrayName.indexOf(".") != -1) {
      return; // skip compound names like obj.prop1.prop2
    }
    console.log(`arrayName = ${arrayName}`)

    code = code.replace(
      new RegExp("const "+arrayName+" = ", 'g'),
      "let "+arrayName+" = "
    );
  })
  */



  // magicstring to string
  code = code.toString();



  if (code != code_old) {
    // code has changed
    
    //console.log("old code:");
    //console.log(code_old);

    //console.log("new code:");
    //console.log(code);

    if (do_write) {
      console.log(`patch file: ${input_file}, keep original: ${backup_file}`)
      fs.copyFileSync(input_file, backup_file);
      fs.writeFileSync(input_file, code);
    }

  } else {
    console.log(`not patched: ${input_file}`)
  }

  // debug
  //await sleep(2000);

}



if (test_input_file) {
  // test
  patch_file(test_input_file);
  process.exit(0);
}



// patch all the files, recursive, follow symlinks
const scriptName = path.basename(__filename);
glob("src/compiler/**/*.{ts,js}", {follow: true}, (error, files) => {
  files.forEach((input_file) => {

    const baseName = path.basename(input_file);
    if (baseName == scriptName) { return; } // ignore file

    patch_file(input_file);

  });
});
