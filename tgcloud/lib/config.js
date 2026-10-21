// PUBLIC CONFIGURATION ONLY. Never put Bot API or Serverless CLI tokens in git.
export const FEED_URL='https://raw.githubusercontent.com/moataz77549-byte/Mbot/main/data/latest.json';
export const MINI_APP_URL='https://app8809490385.tgcloud.ai/'; // available only after Telegram deployment
export const ADMIN_IDS=[]; // set only from your /whoami Telegram ID
export const isAdmin=id=>ADMIN_IDS.includes(Number(id));
