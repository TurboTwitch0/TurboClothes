export const categories = ['Shirts', 'Hoodies', 'Pants', 'Socks'];
// Preview catalog. Replace with the merchant's real catalog before opening checkout.
export const products = [
  {id:'core-tee',name:'Core Tee',category:'Shirts',color:'Chalk',hex:'#e6e4df',price:45,image:'tee-plain-white.jpg',tag:'THE DAILY ROTATION',fit:'Relaxed',description:'The starting point for every rotation. A clean crew neck and an easy silhouette with room to move.'},
  {id:'daily-hoodie',name:'Daily Hoodie',category:'Hoodies',color:'Heather grey',hex:'#969696',price:95,image:'hoodie-back-grey.jpg',tag:'CORE COLLECTION',fit:'Relaxed',description:'An everyday layer with a quiet presence. An easy hooded silhouette for early starts and late finishes.'},
  {id:'straight-pant',name:'Straight Pant',category:'Pants',color:'Black',hex:'#262626',price:85,image:'pants-black.jpg',tag:'YOUR NEW UNIFORM',fit:'Straight',description:'A strong line from waist to ankle. The foundation of a considered everyday uniform.'},
  {id:'crew-socks',name:'Core Crew Socks',category:'Socks',color:'White',hex:'#e8e8e3',price:20,image:'socks-plain.jpg',tag:'FINISH THE FIT',fit:'One size',description:'The detail that makes the look yours. Plain crew socks to bring a clean finish to the everyday.'},
  {id:'graphic-tee',name:'Essential Tee',category:'Shirts',color:'Black',hex:'#242424',price:50,image:'tee-plain-black.jpg',tag:'MAKE A STATEMENT',fit:'Relaxed',description:'Wear your own point of view. A clean black tee gives a familiar everyday shape a new attitude.'},
  {id:'studio-layer',name:'Studio Layer',category:'Hoodies',color:'Off-white',hex:'#ddd9cf',price:105,image:'hoodie-white.jpg',tag:'LAYER YOUR WAY',fit:'Relaxed',description:'An easy layer to take you through the day. Style it with a clean tee and your favorite everyday pants.'},
  {id:'off-duty-pant',name:'Off-Duty Pant',category:'Pants',color:'Olive',hex:'#696b50',price:90,image:'pants-olive.jpg',tag:'OFF THE CLOCK',fit:'Straight',description:'A lighter expression of the everyday trouser. A relaxed look with a deliberate finish.'},
];
export const sizesFor = p => p.category === 'Socks' ? ['One size'] : ['S','M','L','XL'];
export const money = n => new Intl.NumberFormat('en-US',{style:'currency',currency:'USD',maximumFractionDigits:0}).format(n);
