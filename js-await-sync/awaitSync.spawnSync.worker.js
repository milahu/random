// awaitSync.spawnSync.worker.js
// force async function to run in sync
// license CC0-1.0

const terser = require('terser');

const terser_config = {
  sourceMap: false, ecma: 2020,
  compress: false, mangle: false,
  output: { beautify: false }, // uglify
};

const cl = 100; // context length for error printing

var inn = '';

process.stdin.on('readable', () => {
  let chunk;
  while (null !== (chunk = process.stdin.read())) {
    inn += chunk;
  }
});

process.stdin.on('end', async () => {
  try {
    // async terser.minify
    const minify_res = await terser.minify(inn, terser_config);

    if (!minify_res.error) {
      process.stdout.write(minify_res.code); // no newline
      process.stdout.on('drain', ()=>{
        // write is done
        process.exit(0); // success
      });
    }
    else {
      console.log('error:'); console.dir(minify_res.error);
      const ep = minify_res.error.pos;
      console.log('parse error context +-'+cl+': '+inn.substring(ep-cl, ep+cl));
      console.log('parse error raised at: '+inn.substring(ep, ep+cl));
      process.stdout.on('drain', ()=>{
        // write is done
        process.exit(1); // error 1
      });
    }
  }
  catch (error) {
    if (error.constructor.name == 'JS_Parse_Error') {
      console.log('JS_Parse_Error:');
      const {filename, line, col, pos} = error;
      console.dir({filename, line, col, pos});
      process.stdout.on('drain', ()=>{
        process.exit(2); // error 2
      });
    }
    else {
      console.log('error:'); console.dir(error);
      process.stdout.on('drain', ()=>{
        process.exit(3); // error 3
      });
    }
  }
});
