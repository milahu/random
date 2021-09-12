/*
  patch-svelte-compiler-sources.js

  replace array.push with array.pushArray

  usage:
  npm run patch

  license is CC0-1.0
  warranty is none

  based on
  https://astexplorer.net/

*/

const first_input_file = 'src/svelte/compiler.js';
const backup_file_extension = '.patchbak';

// replaceMethod
//   original: a.push(...a1, e, ...a2); // error: Max Stack Size Exceeded
//   pushArray: a.pushArray(a1, [e], a2);
//   pushArrayNoMethod: push_array(a, a1, [e], a2);
//   concat: a = a.concat(a1, [e], a2);
//   spread: a = [...a, ...a1, e, ...a2];
// performance depends on input data,
// but usually push (mutable) is faster than concat (immutable)

const replaceMethod = "pushArrayNoMethod";
const pushArrayFuncName = "push_array"; // svelte library
const pushArrayLibraryPathBase = "svelte/src/compiler/utils/push_array"; // svelte library
//const replaceMethod = "pushArray";
//const replaceMethod = "concat";
//const replaceMethod = "spread";

file_pushArray_js = 'push-array.js';
file_pushArray_ts = 'push-array.ts';

//file_pushArrayNoMethod_js = 'push-array-no-method.js';
//file_pushArrayNoMethod_ts = 'push-array-no-method.ts';

file_pushArrayNoMethod_base = 'push-array-no-method-svelte-module';

const funcName = "push"; // replace this function

const do_write = true; // write output file



// DONT not required in this case
// TODO before patching a dependency:
// install the dependency from git (git clone, pnpm install, npm run build)
// se we get the source files,
// and so we can base our patch on git HEAD
// -> also must rebuild svelte



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

const code_pushArray_js = fs.readFileSync(file_pushArray_js);
const code_pushArray_ts = fs.readFileSync(file_pushArray_ts);

/*
const code_pushArrayNoMethod_js = fs.readFileSync(file_pushArrayNoMethod_js);
const code_pushArrayNoMethod_ts = fs.readFileSync(file_pushArrayNoMethod_ts);
*/

/*
// TODO for each source file, resolve relative import path
// typescript error: Cannot find module 'svelte/src/compiler/utils/push_array'
const code_pushArrayNoMethod_js = `\
import { ${pushArrayFuncName} } from '${pushArrayLibraryPathBase}';

`;
const code_pushArrayNoMethod_ts = code_pushArrayNoMethod_js;
*/


patchedFileList = [];

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
    //console.log(`\n${cwd} $ ${cmd}\n`);
    console.log(`\n( cd ${cwd} && ${cmd} )\n`);
    options = {
      cwd,
      windowsHide: true,
      encoding: 'utf8',
      stdio: [
        (options.input ? 'pipe' : 'inherit'),
        'inherit', 'inherit'// show live output
      ],
      ...options
    }
    //console.dir({ options })
    result = child_process.execSync(cmd, options);
  }
  catch (error) {
    if (options.allowFail) return error;
    console.log(`\ncommand failed:`);
    console.log(`( cd ${cwd} && ${cmd} )\n`);
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

/*
// TEST
exec('src/svelte', 'cat', {
  input: 'hello\n',
});
process.exit();
*/



// clone svelte
exec('src', `git clone --depth 1 https://github.com/sveltejs/svelte.git`, {
  produceFiles: [ 'svelte', 'svelte/package-lock.json' ]
})

// reset all files. this requires rebuild -> slower
//exec('src/svelte', 'git reset --hard HEAD');

exec('src/svelte', 'git checkout origin/master --force');

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



async function patch_file(input_file, patchState = null, fileHistory = null) {

  console.log(`\npatch_file: input_file = ${input_file}`)

  if (!fileHistory) fileHistory = [];
  fileHistory = [...fileHistory] // copy
  fileHistory.push(input_file);

  if (!patchState) {
    patchState = {};
    patchState.doneFileSet = new Set();
  }

  if (patchState.doneFileSet.has(input_file)) {
    console.log(`skip doneFile ${input_file}`);
    return;
  }

  if (fileHistory.length > 4) {
    // debug
    console.log(`stop recursion. fileHistory.length = ${fileHistory.length}`);
    console.log(`stop recursion. fileHistory:\n  ${fileHistory.join('\n  ')}`);
    return;
  }



  var origFileSet = new Set();

  const isTypeScript = Boolean(input_file.match(/\.ts$/i));
  console.log(`read file: ${input_file} [isTypeScript = ${isTypeScript}]`)

  const backup_file = input_file + backup_file_extension;
  if (fs.existsSync(backup_file)) {
    console.log(`error: backup file exists: ${backup_file}\nrun this script only once`);
    //console.log(`undo patch:\n  mv ${backup_file} ${input_file}`);
    console.log('undo patch:\n  find src -name "*.patchbak" | while read p; do o=${p%.*}; mv -v "$p" "$o"; done');
    process.exit(1);
    //return;
  }

  // input
  const code_old = fs.readFileSync(input_file, 'utf8');

  // output
  let code = new MagicString(code_old);

  var locate = getLocator(code_old, { offsetLine: 1 }); // lines are one-based and columns are zero-based in SourceMapConsumer

  var smc = null;
  if (fs.existsSync(`${input_file}.map`)) {
    smc = new SourceMapConsumer(fs.readFileSync(`${input_file}.map`, 'utf8'));
  }
  else {
    console.log(`info: no sourcemap for ${input_file}`)
  }



  // first patch pass
  // replace array.push() with array.pushArray()

  let isSourcePatched = false;
  // in this file, do we need to set Array.prototype.pushArray ?

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

          isSourcePatched = true;

          //console.log(`ts_node.kind = ${ts_SyntaxKind_back[ts_node.kind]} (${ts_node.kind})`);
          //console.dir(ts_node);

          const src_node = code_old.substring(ts_node.pos, ts_node.end);
          //console.log(`src_node = ${src_node}`);

          // TODO just use ts_node.expression.expression as arrayName?
          const arrayNameSpaced = code_old.substring(
            ts_node.pos, // too far left, includes whitespace
            (ts_node.expression.name.pos - 1)
          );
          const lenWhitespace = arrayNameSpaced.match(/^\s*/)[0].length;
          const arrayName = arrayNameSpaced.substring(lenWhitespace);
          //arrayNameList.push(arrayName);

          // position of "array.push(..."
          const idxCallStart = ts_node.pos + lenWhitespace;

          // find "(" bracket after .push
          const idxCallBracketOpen = ts_node.pos + src_node.indexOf(
            "(", (ts_node.expression.name.pos - ts_node.pos)
          );

          // find ")" bracket after .push arguments
          const idxBracketClose = ts_node.pos + src_node.lastIndexOf(")");

          if (replaceMethod == "pushArrayNoMethod") {
            // a.push(...b, c) --> pushArray(a, b, [c])
            code.overwrite(
              (ts_node.expression.name.pos - 1 - arrayName.length),
              idxCallBracketOpen + 1, // consume (
              `${pushArrayFuncName}(${arrayName},` // no trailing whitespace. let eslint fix formatting
            );

            // patch arguments of pushArray()
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

          if (replaceMethod == "pushArray") {
            // ".push" --> ".pushArray"

            // patch object (array)
            // quickfix for
            // src/compiler/compile/css/Stylesheet.ts:376:28 - error TS2339: Property 'pushArray' does not exist on type 'Declaration[]'.
            // src/compiler/compile/nodes/shared/map_children.ts:83:12 - error TS2339: Property 'pushArray' does not exist on type 'any[]'.
            // ...
            code.overwrite(
              (ts_node.expression.name.pos - 1 - arrayName.length),
              (ts_node.expression.name.pos - 1),
              `(${arrayName} as any)`
            );

            // patch method (.push)
            code.overwrite(
              ts_node.expression.name.pos,
              (idxCallBracketOpen + 1),
              `${pushArrayFuncName}(`
            );

            // patch arguments of .pushArray()
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

        isSourcePatched = true;

        const nodeSrc = code_old.substring(node.start, node.end);

        const pushObj = node.callee.object;
        const arrayName = code_old.substring(pushObj.start, pushObj.end);

        const pushProp = node.callee.property;

        //arrayNameList.push(arrayName);


    
        var nodeLoc = locate(node.start);
    
        if (smc) {
          var origLoc = smc.originalPositionFor(nodeLoc);
    
          const origFile = path.join(path.dirname(input_file), origLoc.source);
          origFileSet.add(origFile);

          //console.log(`found branch file ${input_file} (has sourcemap)`)
          //console.dir({ input_file, nodeSrc, nodeLoc, pushObj, arrayName, pushProp, origFile, origLoc })
        }
        else {
          //console.log(`found leaf file? ${input_file} (has no sourcemap)`)
          //console.dir({ input_file, nodeSrc, nodeLoc, pushObj, arrayName, pushProp })
        }

        // patch .push(

        if (replaceMethod == "pushArrayNoMethod") {
          // a.push(...b, c) --> pushArray(a, b, [c])
          code.overwrite(
            node.callee.object.start,
            (pushProp.end + 1),
            `${pushArrayFuncName}(${arrayName},` // no trailing whitespace. let eslint fix formatting
          );

          // patch arguments of pushArray()
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

        if (replaceMethod == "pushArray") {
          // ".push" --> ".pushArray"
          code.overwrite(pushProp.start, pushProp.end, pushArrayFuncName);

          // patch arguments of .pushArray()
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

        console.log(`done: patch node in ${input_file} ${nodeLoc.line + 1}:${nodeLoc.column}`)
    }});
  }

  if (!isSourcePatched) {
    console.log(`not patched: ${input_file}`)
    return;
  }

  // code was changed

  // new magicstring with new positions
  //code = new MagicString(code.toString());

  // magicstring to string
  // we dont need MagicString any more
  // TODO refactor: use different variable names for String and MagicString
  code = code.toString();

  if (replaceMethod == "pushArray") {
    // add implementation of array.pushArray
    if (isTypeScript) {
      code = code_pushArray_ts + '\n\n' + code;
    }
    else {
      code = code_pushArray_js + '\n\n' + code;
    }
  }

  // FIXME immediately handle errors from here.
  // currently, the script will finish, and then throw errors
  //throw 'TEST';

  if (replaceMethod == "pushArrayNoMethod") {
    // add implementation of array.pushArray

    // use relative import path to appease typescript
    const libPath = `src/${pushArrayLibraryPathBase}`;
    const input_dir = path.dirname(input_file);
    const relPath = path.relative(input_dir, libPath);
    
    const code_pushArrayNoMethod = [
      `import { ${pushArrayFuncName} } from '${relPath}';`,
    ].map(line => line + '\n').join('');

    code = code_pushArrayNoMethod + code;
  }

  // debug
  //console.log("old code:\n${code_old}\n:old code");
  //console.log("new code:\n${code}\n:new code");

  patchedFileList.push(input_file);

  if (do_write) {
    console.log(`patch file: ${input_file}\nkeep backup: ${backup_file}`)
    console.log(`compare:`)
    console.log(`  diff -u ${backup_file} ${input_file} | less`)
    fs.copyFileSync(input_file, backup_file);
    fs.writeFileSync(input_file, code);
  }

  // debug
  //await sleep(2000); // FIXME why does this not work
  //throw 'test'; // FIXME why is this not visible?


  var origFileSetList = [];
  for (const v of origFileSet.values()) {
    origFileSetList.push(v);
  }
  console.log(`origFileSetList:${origFileSetList.map(s => `\n  ${s}`).join('')}\n:origFileSetList`)

  patchState.doneFileSet.add(input_file);

  origFileSet.forEach(origFile => {
    // recurse
    console.log(`recurse from ${input_file} to ${origFile}`);
    patch_file(origFile, patchState, fileHistory)
  });

} // end of function patch_file



if (first_input_file) {
  patch_file(first_input_file);
}
else {

// patch all the files, recursive, follow symlinks
const scriptName = path.basename(__filename);
glob("src/compiler/**/*.{ts,js}", {follow: true}, (error, files) => {
  files.forEach(async (input_file) => {

    const baseName = path.basename(input_file);
    if (baseName == scriptName) { return; } // ignore file

    await patch_file(input_file);

  });
});

}



// add new files
// required for the new build
//for (const ext of ['ts', 'js']) {
for (const ext of ['ts']) { // svelte needs only the *.ts file
    fs.copyFileSync(`${file_pushArrayNoMethod_base}.${ext}`, `src/${pushArrayLibraryPathBase}.${ext}`)
  patchedFileList.push(`src/${pushArrayLibraryPathBase}.${ext}`)
  const pathInRepo = `${pushArrayLibraryPathBase}.${ext}`.split('/').slice(1).join('/'); // fix: path is outside repository
  exec('src/svelte', `git add ${pathInRepo}`);
}

// add patched files
exec('src/svelte', `git add src/compiler/**/*.ts`);
//exec('src/svelte', `git add .eslintrc.js`); // only needed here



// summary
console.log(`\npatched files:\n${patchedFileList.join('\n')}`)

// summary
console.log(`
full diff:

#!/usr/bin/env bash
# write to fix-push-array.patch
echo -n "\\
${patchedFileList.join('\n')}
" | while read f
do
  diff -u "$f.patchbak" "$f"
done >fix-push-array.patch

`)

//process.exit() // debug



// build svelte from patched sourcefiles
//var runTests = true;
var runTests = false; // save some time, assume tests are passing
if (runTests) {
  // this ... is ... slow ... -> allow to skip
  // remove tests that need puppeteer
  exec('src/svelte', `rm -rf test/custom-elements`)
  exec('src/svelte', `rm -rf test/runtime-puppeteer`)
  exec('src/svelte', `sed -i "s|runRuntimeSamples('runtime-puppeteer');||" test/server-side-rendering/index.ts`)
  // run full test. this will first run: npm run build
  exec('src/svelte', `npm run test`)

  exec('src/svelte', `git restore test`)
}
else {
  // this will throw on error
  exec('src/svelte', `npm run build`) // just check if it builds
}



// NOTE svelte uses tabs for indent
const eslintrc_patch = `\

diff --git a/.eslintrc.js b/.eslintrc.js
index a093de6..99f97a0 100644
--- a/.eslintrc.js
+++ b/.eslintrc.js
@@ -11,4 +11,11 @@ module.exports = {
 		],
 		'svelte3/compiler': require('./compiler')
 	}
+
+	// NOTE this is only used to fix the transform
+	,
+	rules: {
+		'comma-spacing': 'error'
+	}
+
 };

`;
exec('src/svelte', 'patch -p1', {
  input: eslintrc_patch,
});



// eslint requires a working compiler.js
// src/svelte/.eslintrc.js: 'svelte3/compiler': require('./compiler')
// so first we build, then we lint
exec('src/svelte', `npm run lint -- --fix`) // required. patching creates ugly syntax



// publish patch for svelte

const branchTime = (new Date()).toLocaleString('af').replace(/[-:]/g, '').replace(/ /g, '-');

//exec('src/svelte', 'git branch --delete --force fix-maximum-call-stack-size-exceeded', { allowFail: true });
exec('src/svelte', `git branch fix-maximum-call-stack-size-exceeded-${branchTime}`);
exec('src/svelte', `git switch fix-maximum-call-stack-size-exceeded-${branchTime}`);
exec('src/svelte', 'git status');



// allow manual postprocessing
/*
exec('src/svelte', 'git commit -a -m "fix: Maximum call stack size exceeded (#4694)"');
exec('src/svelte', 'git remote add fork https://milahu@github.com/milahu/svelte.git', { allowFail: true })
exec('src/svelte', 'git push fork --force')
// TODO publish patch for code-red
*/
console.log(`
TODO next steps:

cd src/svelte
git status
# edit files

git commit -m "[fix] Maximum call stack size exceeded (#4694)"
git remote add fork https://milahu@github.com/milahu/svelte.git
git push --force fork fix-maximum-call-stack-size-exceeded-${branchTime}:fix-maximum-call-stack-size-exceeded

cd ../code-red
cp ../svelte/node_modules/.pnpm/code-red@0.2.2/node_modules/code-red/src/print/handlers.js src/print/handlers.js
# add whitespace after comma (eslint rule: comma-spacing)
sed -i -E 's|${pushArrayFuncName}\(([^,]+),(.)|${pushArrayFuncName}(\\1, \\2|' src/print/handlers.js
cp ../../push-array-no-method-svelte-module.js src/utils/push_array.js

# TODO fix import path in src/print/handlers.js:
# import { push_array } from '../utils/push_array';

git add src/print/handlers.js src/utils/push_array.js

# publish patch for code-red
`)

