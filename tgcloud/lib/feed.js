import {fetch} from 'sdk';
import {FEED_URL} from './config.js';
export async function loadFeed(){
 const url=FEED_URL+(FEED_URL.includes('?')?'&':'?')+'t='+Math.floor(Date.now()/300000);
 const r=await fetch(url); if(!r.ok)throw new Error('Feed HTTP '+r.status);
 const v=await r.json();if(!v||!Array.isArray(v.items))throw new Error('Invalid feed'); return v;
}
export function digest(feed,lang='ar'){
 const ar=lang==='ar';const lines=[ar?'📡 رادار عروض الذكاء الاصطناعي':'📡 AI Offer Radar',
 String(feed.date||'—')+' • '+String(feed.count||0)+' '+(ar?'نتيجة':'findings'),''];
 if(!feed.items?.length)lines.push(ar?'لا توجد عروض مؤكدة حديثة في التقرير.':'No confirmed recent offers in the feed.');
 for(const [i,item] of (feed.items||[]).slice(0,10).entries()){
  const flag=item.trust==='official_source'?'🏢':item.trust==='independent_report'?'📰':'⚠️';
  const title=ar?(item.arabic_title||item.title):(item.english_title||item.title);
  const line=`${i+1}. ${flag} ${String(title||'').slice(0,115)}${item.price_mentioned?' ('+item.price_mentioned+')':''}\n🔗 ${item.url}`;
  if((lines.join('\n')+line).length>3700)break; lines.push(line,'');
 }
 lines.push(ar?'⚠️ الأسعار والباعة غير مضمونين؛ تحقق من المصدر قبل الدفع.':'⚠️ Prices and sellers are not verified; check before buying.');
 return lines.join('\n').slice(0,4000);
}
