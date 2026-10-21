import {db,EndpointError} from 'sdk';
import {desc} from 'sdk/db';
import {suggestions} from '../schema.js';
import {isAdmin} from '../lib/config.js';
export default async function(_input,ctx){if(!isAdmin(ctx.initData?.user?.id))throw new EndpointError('Admin only');
 return {items:await db.select().from(suggestions).orderBy(desc(suggestions.id)).limit(100).all()};}
