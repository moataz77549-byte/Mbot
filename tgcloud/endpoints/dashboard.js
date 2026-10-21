import {EndpointError} from 'sdk';
import {loadFeed} from '../lib/feed.js';
import {isAdmin} from '../lib/config.js';
export default async function(_input,ctx){const uid=ctx.initData?.user?.id;if(!uid)throw new EndpointError('Telegram login required');
 try{return {...await loadFeed(),admin:isAdmin(uid)};}catch(e){throw new EndpointError('Report unavailable');}}
