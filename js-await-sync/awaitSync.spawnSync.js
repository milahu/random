// awaitSync.spawnSync.js
// force async function to run in sync
// license CC0-1.0

const child_process = require('child_process');
const workerScript = require.resolve('./awaitSync.spawnSync.worker.js');

const inn = `
  let f = (a) => {
    console.log('minify me');
  };
  f(1);
`;

let out = '';

try {
  const spawnRes = child_process.spawnSync(
    process.execPath, // node
    [workerScript], {
    input: inn,
    encoding: 'utf-8',
    //timeout: Infinity,
    maxBuffer: Infinity,
    windowsHide: true, // windows os
  });
  if (spawnRes.status == 0) {
    out = spawnRes.stdout;
  }
  else {
    throw spawnRes;
  }
}
catch (error) { // timeout, exit(1), exit(2)
  if (error.status === null) {
    throw new Error('awaitSync error timeout');
  }
  throw new Error('awaitSync error '+error.status+':\n'+error.stdout+'\n'+error.stderr);
}
// success
console.log(out);
