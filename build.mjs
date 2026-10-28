import {mkdirSync,copyFileSync,cpSync,rmSync,readFileSync,writeFileSync,existsSync} from 'node:fs';
import {products,categories,EBAY_STORE_URL} from './catalog.js';
rmSync('dist',{recursive:true,force:true});mkdirSync('dist',{recursive:true});
for(const file of ['index.html','styles.css','app.js','catalog.js','interactions.js','boot.js'])copyFileSync(file,'dist/'+file);
cpSync('assets','dist/assets',{recursive:true});
if (existsSync('outputs/evovo-brand-kit')) cpSync('outputs/evovo-brand-kit','dist/brand-kit',{recursive:true});
if (existsSync('outputs/evovo-brand-kit.zip')) copyFileSync('outputs/evovo-brand-kit.zip','dist/brand-kit/evovo-brand-kit.zip');
const shell=readFileSync('index.html','utf8');
const pages=[['shop','Style ideas'],['about','About EVOVOFinds'],['saved','Saved ideas'],['help','How to shop'],['checkout','Checkout on eBay'],...categories.map(c=>['shop/'+c.toLowerCase(),c]),...products.map(p=>['products/'+p.id,p.name])];
for(const [path,title] of pages){mkdirSync('dist/'+path,{recursive:true});writeFileSync('dist/'+path+'/index.html',shell.replace('<title>EVOVO — Find your style. Keep your edit.</title>',`<title>${title} — EVOVO</title>`).replace('href="https://evovo.vercel.app/"', `href="https://evovo.vercel.app/${path}/"`));}
// Keep bookmarked checkout URLs working on every static host, even with JavaScript disabled.
writeFileSync('dist/checkout/index.html', `<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><meta http-equiv="refresh" content="0; url=${EBAY_STORE_URL}"><title>Checkout on eBay — EVOVO</title><link rel="stylesheet" href="/styles.css"></head><body><main class="section empty"><h1 class="page-heading">Continue to eBay.</h1><p>Choose from the current EVOVOFinds listings and complete your purchase on eBay.</p><a class="pill" href="${EBAY_STORE_URL}">Checkout on eBay</a></main></body></html>`);
writeFileSync('dist/404.html',shell.replace('<title>EVOVO — Find your style. Keep your edit.</title>','<title>Page not found — EVOVO</title>'));
writeFileSync('dist/robots.txt','User-agent: *\nAllow: /\n');
console.log(`EVOVO: built homepage + ${pages.length} pages, local imagery, styles, and application modules.`);
