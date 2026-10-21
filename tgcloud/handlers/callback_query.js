import {api} from 'sdk';
import {loadFeed,digest} from '../lib/feed.js';
import {keyboard} from '../lib/interface.js';
import {getLang,setLang} from '../lib/users.js';
export default async function(callback){
 const uid=callback.from?.id,id=callback.message?.chat?.id;if(!uid||!id)return;
 const action=callback.data||'';await api.answerCallbackQuery({callback_query_id:callback.id});
 let lang=await getLang(uid);if(action==='toggle_language'){
  lang=lang==='ar'?'en':'ar';await setLang(uid,lang);return api.sendMessage({chat_id:id,text:lang==='ar'?'تم تغيير اللغة':'Language changed',reply_markup:keyboard(lang)});
 }
 try{const feed=await loadFeed();let result='';
  if(action==='report')result=digest(feed,lang);
  else if(action==='stats')result=lang==='ar'?`📊 آخر فحص: ${feed.date||'—'}\nالنتائج: ${feed.count||0}\nالمصادر المفحوصة: ${feed.scanned_feeds||0}`:`📊 Last scan: ${feed.date||'—'}\nResults: ${feed.count||0}\nSources scanned: ${feed.scanned_feeds||0}`;
  else if(['api','free','community','subscription'].includes(action)){const items=feed.items.filter(x=>x.kind===action);result=digest({...feed,items,count:items.length},lang);}else return;
  await api.sendMessage({chat_id:id,text:result,reply_markup:keyboard(lang),link_preview_options:{is_disabled:true}});
 }catch(e){await api.sendMessage({chat_id:id,text:lang==='ar'?'مصدر البيانات غير متاح':'Feed unavailable'});}
}
