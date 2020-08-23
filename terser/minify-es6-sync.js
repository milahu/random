#!/usr/bin/env node

// minify-es6-sync.js
// synchronous minify of es6 javascript
// license CC-0 + no warranty

if (false) { // sample use

  const child_process = require('child_process');
  const code_in = '(()=>(1))();';
  let code_out = '';

  try {
    code_out = child_process.execSync(
      "node minify-es6-sync.js", {
      input: code_in,
      timeout: 10000,
      encoding: 'utf-8',
    }); 
  } catch (error) {
    // timeout or exit(1)
    console.log('error in minify:');
    console.log(error.stdout);
    throw new Error("minify failed");
  }
}

const terser_minify = require("terser").minify; // async

const terser_config = {
  sourceMap: false,
  ecma: 11, // year 2020
  compress: false,
  mangle: false,
  output: {
    beautify: false,
    //semicolons: true,
  },
  keep_fnames: true,
  keep_classnames: true,
};

const readable = process.stdin;
var code_in = '';

readable.on('readable', () => {
  let chunk;
  while (null !== (chunk = readable.read())) {
    code_in += chunk;
  }
});

readable.on('end', async () => { // async
  try {

    const minify_res = await terser_minify(code_in, terser_config);

    if (minify_res.error) {
      console.log('error:'); console.dir(minify_res.error);
      const cl = 100; const ep = minify_res.error.pos;

      const err_ctx = code_in.substring(ep - cl, ep + cl);
      console.log(`parse error context +-${cl}: ${err_ctx}`);

      const err_raised = code_in.substring(ep, ep + cl);
      console.log(`parse error raised at: ${err_raised}`);

      process.exit(1);
    }

    process.stdout.write(minify_res.code);
    process.exit(0); // success

  } catch (error) {
    console.log('error:');
    console.dir(error);
    process.exit(1);
  }
});
