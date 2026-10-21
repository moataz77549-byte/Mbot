import {readdirSync} from 'node:fs';
import {execFileSync} from 'node:child_process';
import {join} from 'node:path';
function walk(d){for(const e of readdirSync(d,{withFileTypes:true})){let p=join(d,e.name);if(e.isDirectory())walk(p);else if(p.endsWith('.js'))execFileSync(process.execPath,['--check',p],{stdio:'inherit'});}}
walk('tgcloud'); walk('scripts'); console.log('All JS syntax checks passed');
