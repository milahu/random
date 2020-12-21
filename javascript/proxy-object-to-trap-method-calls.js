// based on https://stackoverflow.com/a/25069451/10440128

const obj_hidden = {};

const obj = new Proxy(obj_hidden, {
    get(target, prop) {
        if (typeof target[prop] == 'function') {
          return function (...args) {
            console.dir({ call: [prop, ...args] });
            return target[prop].apply(target, args);
          }
        }
        console.dir({ get: [prop] });
        return target[prop];
    },
    set(target, prop, value) {
        console.dir({ set: [prop, value] });
        target[prop] = value;
        return true;
    }
});
