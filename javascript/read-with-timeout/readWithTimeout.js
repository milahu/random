// readWithTimeout.js

const child_process = require('child_process');
const fs = require('fs');

/**
* read with timeout. unix only
*
* https://stackoverflow.com/questions/20808126/how-to-timeout-an-fs-read-in-node-js
*
* @param {number | string} fdOrPath
* @param {number} blockSize
* @param {number} timeout
* @param {Object} options
* @param {number} [options.numBlocks=1]
* @param {string=} options.encoding
*/
function readWithTimeout(fdOrPath, blockSize, timeout, options = {}) {
  if (!options) options = {};
  const numBlocks = options.numBlocks || 1;
  if (options.numBlocks) delete options.numBlocks;
  if (options.timeout) throw Error('dont set options.timeout');
  const ddArgs = [`bs=${blockSize}`, `count=${numBlocks}`, 'status=none'];
  const stdio = [fdOrPath, 'pipe', 'pipe'];
  if (typeof fdOrPath == 'string') {
    if (!fs.existsSync(fdOrPath)) throw Error(`no such file: ${fdOrPath}`);
    ddArgs.push(`if=${fdOrPath}`);
    stdio[0] = null;
  }
  else if (typeof fdOrPath != 'number') {
    throw Error(`fdOrPath must be number or string`);
  }
  //console.dir({ fdOrPath, blockSize, timeout, stdio, ddArgs });
  const reader = child_process.spawnSync('dd', ddArgs, {
    timeout,
    stdio,
    windowsHide: true,
    ...options,
  });
  if (reader.error) throw reader.error;
  return reader.stdout;
}

// demo: read (1 byte) token from gnumake jobserver on fd 3
try {
  const readLen = 1;
  const output = readWithTimeout(3, 1, 1000, {
  //const output = readWithTimeout('/dev/null', 1, 1000, {
    encoding: 'utf8',
  });
  if (output.length == 0) {
    console.log(`read nothing`);
  }
  else if (output.length < readLen) {
    console.log(`read partial: ${output.length} of ${readLen} bytes`);
  }
  else {
    console.log('read ok');
  }
  console.dir(output);
}
catch (e) {
  if (e.errno == -110) {
    console.log('read error: timeout');
  }
  else {
    console.log('read error:');
    console.dir(e);
  }
}
