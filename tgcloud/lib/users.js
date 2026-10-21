import {db} from 'sdk';
import {eq} from 'sdk/db';
import {preferences} from '../schema.js';
export async function getLang(uid){const row=await db.select().from(preferences).where(eq(preferences.userId,Number(uid))).get();return row?.language==='en'?'en':'ar';}
export async function setLang(uid,language){await db.insert(preferences).values({userId:Number(uid),language}).onConflictDoUpdate({target:preferences.userId,set:{language}}).run();}
