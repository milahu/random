// push-array.ts start
// TODO move pushArray to npm module
//export{}
//declare global {
//  interface Array<T>  {
//    pushArray(...otherList: any[]): number;
//  }
//}
(Array.prototype as any).pushArray = function pushArray(...otherList: any[]) {
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
// push-array.ts end
