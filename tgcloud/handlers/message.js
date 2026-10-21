import {api} from 'sdk';
import {loadFeed,digest} from '../lib/feed.js';
import {keyboard,welcome} from '../lib/interface.js';
import {getLang,setLang} from '../lib/users.js';
import {queueSuggestion} from '../lib/suggest.js';
import {isAdmin} from '../lib/config.js';
export default async function(message){
 const id=message.chat?.id,uid=message.from?.id;if(!id||!uid)return;
 const input=String(message.text||'').trim();const cmd=input.split(/\s+/)[0].split('@')[0].toLowerCase();
 let lang=await getLang(uid);const ar=lang==='ar';
 if(cmd==='/whoami')return api.sendMessage({chat_id:id,text:`Telegram user ID: ${uid}\nAdmin: ${isAdmin(uid)}`});
 if(cmd==='/language'){lang=ar?'en':'ar';await setLang(uid,lang);return api.sendMessage({chat_id:id,text:lang==='ar'?'تم اختيار العربية':'English selected',reply_markup:keyboard(lang)});}
 if(cmd==='/submit'){
  try{await queueSuggestion(uid,input.slice(cmd.length).trim());return api.sendMessage({chat_id:id,text:ar?'تم استلام الرابط للمراجعة، وليس توصية بالشراء.':'Source queued for review, not endorsed.'});}
  catch(e){return api.sendMessage({chat_id:id,text:ar?'الرابط غير صالح أو تجاوزت حد الإرسال. استخدم /submit https://example.com':'Invalid URL or daily limit exceeded. Use /submit https://example.com'});}
 }
 if(cmd==='/today'){
  try{return api.sendMessage({chat_id:id,text:digest(await loadFeed(),lang),reply_markup:keyboard(lang),link_preview_options:{is_disabled:true}});}
  catch(e){return api.sendMessage({chat_id:id,text:ar?'تعذر جلب تقرير اليوم':'Report unavailable'});}
 }
 if(cmd==='/sources')return api.sendMessage({chat_id:id,text:ar?'نجمع نتائج RSS عامة متعددة اللغات، ونصنف الروابط الرسمية والمستقلة وغير الموثقة. القنوات والمجموعات الخاصة غير متاحة.':'We scan multilingual public RSS and accessible sources. Private communities are not accessible.',reply_markup:keyboard(lang)});
 return api.sendMessage({chat_id:id,text:welcome(lang),parse_mode:'Markdown',reply_markup:keyboard(lang)});
}
