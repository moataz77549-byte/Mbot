import {EndpointError} from 'sdk';
import {queueSuggestion} from '../lib/suggest.js';
export default async function(input,ctx){const uid=ctx.initData?.user?.id;if(!uid)throw new EndpointError('Telegram login required');return queueSuggestion(uid,input?.url);}
