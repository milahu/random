/*
tsx2jsx.mjs
... cos fuck typescript!

npm i -D sucrase tiny-glob
node tsx2jsx.mjs

https://github.com/alangpierce/sucrase/issues/559
*/

import fs from 'fs';
import {spawnSync} from 'child_process';

import glob from 'tiny-glob';

import {HelperManager} from "sucrase/dist/HelperManager.js";
import identifyShadowedGlobalsModule from "sucrase/dist/identifyShadowedGlobals.js";
import NameManagerModule from "sucrase/dist/NameManager.js";
import {parse} from "sucrase/dist/parser/index.js";
import TokenProcessorModule from "sucrase/dist/TokenProcessor.js";
import RootTransformerModule from "sucrase/dist/transformers/RootTransformer.js";
import getTSImportedNamesModule from "sucrase/dist/util/getTSImportedNames.js";

// workaround ...
// TypeError: NameManager is not a constructor
const NameManager = NameManagerModule.default;
const TokenProcessor = TokenProcessorModule.default;
const getTSImportedNames = getTSImportedNamesModule.default;
const identifyShadowedGlobals = identifyShadowedGlobalsModule.default;
const RootTransformer = RootTransformerModule.default;

function transformTSOnly(code) {
  const {tokens, scopes} = parse(
    code,
    true /* isJSXEnabled */,
    true /* isTypeScriptEnabled */,
    false /* isFlowEnabled */,
  );
  const nameManager = new NameManager(code, tokens);
  const helperManager = new HelperManager(nameManager);
  const tokenProcessor = new TokenProcessor(code, tokens, false /* isFlowEnabled */, helperManager);

  identifyShadowedGlobals(tokenProcessor, scopes, getTSImportedNames(tokenProcessor));
  const sucraseContext = {
    tokenProcessor,
    scopes,
    nameManager,
    importProcessor: null,
    helperManager,
  };

  const transformer = new RootTransformer(sucraseContext, ["typescript"], false, {
    transforms: ["typescript"],
  });
  return transformer.transform();
}

const gitDirty = spawnSync('git', ['diff-index', 'HEAD', '--'], { encoding: 'utf8' }).stdout;
if (gitDirty != '') {
  console.log(`error: git is dirty:\n\n${gitDirty}`);
  process.exit(1);
}

// convert all files in src/ folder
for (const fi of await glob('./src/**/*.tsx')) {
  const fo = fi.slice(0, -4) + '.jsx';
  console.log(`${fi} -> ${fo}`);
  const i = fs.readFileSync(fi, 'utf8');
  const o = transformTSOnly(i);
  // always do your backups :P
  fs.writeFileSync(fi, o, 'utf8'); // replace input
  spawnSync('git', ['mv', '-v', fi, fo]); // rename
  spawnSync('git', ['add', fo]); // add
}
spawnSync('git', ['commit', '-m', 'tsx2jsx']); // commit
