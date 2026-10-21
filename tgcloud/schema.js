import {table,integer,text,sql} from 'sdk/db';
export const preferences=table('radar_preferences',{
  userId:integer('user_id').primaryKey(),language:text('language').notNull().default('ar'),
  createdAt:integer('created_at',{mode:'timestamp'}).default(sql`(unixepoch())`),
});
export const suggestions=table('radar_suggestions',{
  id:integer('id').primaryKey({autoIncrement:true}),userId:integer('user_id').notNull(),
  url:text('url').notNull(),status:text('status').notNull().default('pending'),
  createdAt:integer('created_at',{mode:'timestamp'}).default(sql`(unixepoch())`),
});
