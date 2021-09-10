// push-array.js start
// TODO move pushArray to npm module
Array.prototype.pushArray = function pushArray(...otherList) {
  let c = 0; // count pushed elements
  for (let a = 0; a < otherList.length; a++) {
    const other = otherList[a];
    for (let i = 0; i < other.length; i++) {
      this.push(other[i]);
      c++;
    }
  }
  return c;
};
// push-array.js end
