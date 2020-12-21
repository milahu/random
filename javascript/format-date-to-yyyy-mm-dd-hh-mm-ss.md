# format date to yyyy-mm-dd hh:mm:ss

short answer:

```js
(new Date()).toLocaleString('af')

// -> '2020-12-21 11:50:15'
```

the lazy solution is to use `Date.toLocaleString` with the right region code

to get a list of matching regions you can run

```bash
#!/bin/bash

[ -f bcp47.json ] || \
wget https://raw.githubusercontent.com/pculture/bcp47-json/master/bcp47.json

grep 'tag" : ' bcp47.json | cut -d'"' -f4 >codes.txt

js=$(cat <<'EOF'
const fs = require('fs');
const d = new Date(2020, 11, 12, 20, 00, 00);
fs.readFileSync('codes.txt', 'utf8')
.split('\n')
.forEach(code => {
  try {
    console.log(code+' '+d.toLocaleString(code))
  }
  catch (e) { console.log(code+' '+e.message) }
});
EOF
)

# print THE LIST of civilized countries
echo "$js" | node - | grep '2020-12-12 20:00:00'
```

and here is .... THE LIST

```
af ce eo gv ha ku kw ky lt mg rw se sn sv xh zu 
ksh mgo sah wae AF KW KY LT MG RW SE SN SV
```

sample use:

```js
(new Date()).toLocaleString('af')

// -> '2020-12-21 11:50:15'
```

: )

(note. this MAY not be portable.)

(originally posted [here](https://stackoverflow.com/a/65391425/10440128))
