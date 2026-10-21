import {db,EndpointError} from 'sdk';
import {eq,desc} from 'sdk/db';
import {suggestions} from '../schema.js';
export async function queueSuggestion(uid,url){
 url=String(url||'').trim();if(!/^https:\/\/[^\s]{4,480}$/i.test(url))throw new EndpointError('Public HTTPS link required');
 const recent=await db.select().from(suggestions).where(eq(suggestions.userId,Number(uid))).orderBy(desc(suggestions.id)).limit(10).all();
 const now=Date.now(); const today=recent.filter(x=>x.createdAt&&now-new Date(x.createdAt).getTime()<86400000);
 if(today.length>=5)throw new EndpointError('Max five suggestions per day');
 if(recent.some(x=>x.url===url))throw new EndpointError('Duplicate suggestion');
 await db.insert(suggestions).values({userId:Number(uid),url,status:'pending'}).run();return {saved:true};
}
