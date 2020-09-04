// awaitSync.worker_threads.js
// force async functions to run in sync
// block the main thread until the async function is done
// inspired by https://discourse.entropic.dev/t/looking-for-help-synchronous-ipc-in-node/219/11
// license CC0-1.0

// alternatives include:
// * ForbesLindesay/sync-rpc: pure javascript using fs.spawnSync and TCP connections
// * JacobFischer/netlinkwrapper: C++ code, using TCP connections
// * MMhunter/node-sync-ipc: C++ code, using sockets or named pipes
// related:
// * abbr/deasync: C++ code, watching the event loop, not working to await promises

// status: working prototype
// only stdout.write from child thread has wrong timing = is printed after parent output

const worker_threads = require('worker_threads');

if (worker_threads.isMainThread) {

  // worker parent

  //const sharedInt32ArraySize = 1024;
  const sharedInt32ArraySize = 16;

  const payloadOffsetInt32 = 4;
  const payloadOffsetInt8 = 4 * payloadOffsetInt32;
  const maxPayloadBytes = 4*(sharedInt32ArraySize - payloadOffsetInt32);

  const w = new worker_threads.Worker(
    __filename,
    {
      workerData: {
        payloadOffsetInt8,
        payloadOffsetInt32,
        maxPayloadBytes,
      },
    }
  );

  // 4 byte = 1 int32
  // we need Int32Array for Atomics.wait

  const sharedArrayBuffer = new SharedArrayBuffer(4 * sharedInt32ArraySize);

  const sharedInt32Array = new Int32Array(sharedArrayBuffer);
  const sharedUint8Array = new Uint8Array(sharedArrayBuffer);

  var textEncoder = new TextEncoder(); // always utf-8
  const inn = "This is a string converted to a Uint8Array";
  console.log('parent inn = '+inn);
  const strUint8 = textEncoder.encode(inn);

  // fill array
  sharedInt32Array[0] = 1; // parent is done = this is last inn chunk
  sharedInt32Array[1] = 0; // child is done
  sharedInt32Array[2] = strUint8.byteLength; // inn chunk size
  //sharedInt32Array[3] = 0; // reserved

  // TODO split array in chunks of maxPayloadBytes
  for (let [idx, char] of strUint8.entries()) {
    sharedUint8Array[payloadOffsetInt8 + idx] = char;
  }
  // send array
  w.postMessage(sharedInt32Array);

  // wait for response
  console.log('parent wait ....');
  const waitRes = Atomics.wait(
    sharedInt32Array, // array
    1, // index 1 = child is done
    0, // wait value, other value = continue
    4000, // timeout
  );
  console.log('parent wait result: '+waitRes);

  // get response from sharedArray
  const bytesToRead = sharedInt32Array[2];

  console.log('parent got '+bytesToRead+' bytes to read');

  //console.log('parent got sharedUint8Array:');
  //console.dir(sharedUint8Array);

  let out = '';
  var textDecoder = new TextDecoder('utf-8');
  // TODO loop outChunk-s until sharedInt32Array[1] == 1 (child outbuf is empty)
  let outChunk = textDecoder.decode(sharedUint8Array.slice(
    payloadOffsetInt8, payloadOffsetInt8 + bytesToRead
  ));
  out += outChunk;

  console.log('parent out = '+out);

  // exit process
  w.unref();

}

else {

  // worker child

  let inn = ''; // input string
  let out = ''; // output string

  // globals
  const {
    payloadOffsetInt8,
    payloadOffsetInt32,
    maxPayloadBytes,
  } = worker_threads.workerData;

  worker_threads.parentPort.on('message', sharedInt32Array => {

    // assert: value is always Int32Array
    //if (value.constructor && value.constructor.name == 'Int32Array') {

    const sharedArrayBuffer = sharedInt32Array.buffer;
    const sharedUint8Array = new Uint8Array(sharedArrayBuffer);
    const bytesToRead = sharedInt32Array[2];

    console.log('child got '+bytesToRead+' bytes to read');

    //console.log('child got sharedUint8Array:');
    //console.dir(sharedUint8Array);

    // TODO loop innChunk-s until sharedInt32Array[0] == 1 (parent outbuf is empty)
    var textDecoder = new TextDecoder('utf-8');
    let innChunk = textDecoder.decode(sharedUint8Array.slice(
      payloadOffsetInt8, payloadOffsetInt8 + bytesToRead
    ));
    inn += innChunk;

    const parentIsDone = Boolean(sharedInt32Array[0]);
    if (parentIsDone) {
      // all input is stored in `inn`
      // start working

      // delay result
      const delayMs = 1000;
      setTimeout(() => {

        out = inn.split('').map(char => String.fromCharCode((1+char.charCodeAt(0))%255)).join('');

        // all output is stored in `out`
        // send result back to parent

        // convert string to uint8 array
        const textEncoder = new TextEncoder(); // always utf-8
        let strUint8 = textEncoder.encode(out);

        const outAbAligned = new ArrayBuffer(Math.ceil(strUint8.byteLength/4)*4);
        const strUint8Aligned = new Uint8Array(outAbAligned);
        //strUint8Aligned.set(strUint8.buffer);
        for (let [idx, ui8] of strUint8.entries()) {
          strUint8Aligned[idx] = ui8;
        }

        const strInt32 = new Int32Array(strUint8Aligned.buffer);
        // TODO split chunks to maxPayloadBytes

        // write to shared array
        Atomics.store(sharedInt32Array, 2, strUint8.byteLength); // out chunk size
        for (let [idx, i32] of strInt32.entries()) {
          Atomics.store(
            sharedInt32Array,
            payloadOffsetInt32 + idx,
            i32
          );
        }

        // set workerIsDone to true
        // unblock parent thread (Atomics.wait)
        Atomics.notify(sharedInt32Array, 1, 1); // child is done = this is last out chunk

      }, delayMs);
    }
  });
}
