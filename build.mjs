import {mkdirSync,copyFileSync,cpSync,rmSync,readFileSync,writeFileSync} from 'node:fs';
import {products,categories,EBAY_STORE_URL} from './catalog.js';
rmSync('dist',{recursive:true,force:true});mkdirSync('dist',{recursive:true});
for(const file of ['index.html','styles.css','app.js','catalog.js'])copyFileSync(file,'dist/'+file);
cpSync('assets','dist/assets',{recursive:true});
const shell=readFileSync('index.html','utf8');
const pages=[['shop','The collection'],['about','Our mindset'],['saved','Saved pieces'],['help','Good to know'],['checkout','Checkout on eBay'],...categories.map(c=>['shop/'+c.toLowerCase(),c]),...products.map(p=>['products/'+p.id,p.name])];
for(const [path,title] of pages){mkdirSync('dist/'+path,{recursive:true});writeFileSync('dist/'+path+'/index.html',shell.replace('<title>EVOVO — Never Stand Still.</title>',`<title>${title} — EVOVO</title>`));}
// Keep bookmarked checkout URLs working on every static host, even with JavaScript disabled.
writeFileSync('dist/checkout/index.html', `<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><meta http-equiv="refresh" content="0; url=${EBAY_STORE_URL}"><title>Checkout on eBay — EVOVO</title><link rel="stylesheet" href="/styles.css"></head><body><main class="section empty"><h1 class="page-heading">Continue to eBay.</h1><p>Shop current EVOVOFinds listings and complete your purchase on eBay. Your EVOVO bag does not transfer.</p><a class="pill" href="${EBAY_STORE_URL}">Checkout on eBay</a></main></body></html>`);
writeFileSync('dist/404.html',shell.replace('<title>EVOVO — Never Stand Still.</title>','<title>Page not found — EVOVO</title>'));
writeFileSync('dist/robots.txt','User-agent: *\nAllow: /\n');
console.log(`EVOVO: built homepage + ${pages.length} pages, local imagery, styles, and application modules.`);
