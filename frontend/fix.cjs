const fs = require('fs');
const path = 'src/components/ui/Hyperspeed.tsx';
let txt = fs.readFileSync(path, 'utf8');
txt = txt.replace(/\\`/g, '`');
txt = txt.replace(/\\\$/g, '$');
fs.writeFileSync(path, txt);
