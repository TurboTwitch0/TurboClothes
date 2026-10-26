import {mkdirSync,copyFileSync,cpSync,rmSync,readFileSync,writeFileSync} from 'node:fs';
import {products,categories} from './catalog.js';
rmSync('dist',{recursive:true,force:true});mkdirSync('dist',{recursive:true});
for(const file of ['index.html','styles.css','app.js','catalog.js'])copyFileSync(file,'dist/'+file);
cpSync('assets','dist/assets',{recursive:true});
const shell=readFileSync('index.html','utf8');
const pages=[['shop','The collection'],['about','Our mindset'],['saved','Saved pieces'],['help','Good to know'],['checkout','Your bag'],...categories.map(c=>['shop/'+c.toLowerCase(),c]),...products.map(p=>['products/'+p.id,p.name])];
for(const [path,title] of pages){mkdirSync('dist/'+path,{recursive:true});writeFileSync('dist/'+path+'/index.html',shell.replace('<title>EVOVO — Never Stand Still.</title>',`<title>${title} — EVOVO</title>`));}
writeFileSync('dist/404.html',shell.replace('<title>EVOVO — Never Stand Still.</title>','<title>Page not found — EVOVO</title>'));
writeFileSync('dist/robots.txt','User-agent: *\nAllow: /\n');
console.log(`EVOVO: built homepage + ${pages.length} pages, local imagery, styles, and application modules.`);
