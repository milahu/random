#! /usr/bin/env node

const tree = [ '+', 1, 1 ];

function getThunk(tree, idx) {
  const op = tree[idx];
  if (op == '+') {
    return {
      thunk: () => (tree[idx+1] + tree[idx+2]),
      idx: idx + 2,
    };
  }
}

console.log(`tree = ${JSON.stringify(tree)}`);

var thunk = null;
var idx = 0;

console.log(`idx = ${idx}`);
var { thunk, idx } = getThunk(tree, idx);
console.log(`thunk = ${thunk}`);
console.log(`thunk() = ${thunk()}`);
