import {copyFileSync,mkdirSync} from 'node:fs';
mkdirSync('dist',{recursive:true});
for (const f of ['index.html']) copyFileSync('miniapp/'+f,'dist/'+f);
console.log('Mini App ready: dist/');
