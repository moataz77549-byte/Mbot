import {MINI_APP_URL} from './config.js';
export function keyboard(lang='ar'){
 const a=lang==='ar';const rows=[
  [{text:a?'🔥 عروض اليوم':'🔥 Today',callback_data:'report'},{text:a?'🆓 المجاني':'🆓 Free',callback_data:'free'}],
  [{text:a?'🔌 واجهات API':'🔌 APIs',callback_data:'api'},{text:a?'🏷️ الاشتراكات':'🏷️ Subscriptions',callback_data:'subscription'}],
  [{text:a?'📊 الإحصائيات':'📊 Statistics',callback_data:'stats'},{text:a?'🌐 English':'🌐 العربية',callback_data:'toggle_language'}],
  [{text:a?'🤖 بوتات قيد البحث':'🤖 Tracked bots',callback_data:'tracked_bots'}],
  [{text:a?'🖥 لوحة التحكم':'🖥 Dashboard',web_app:{url:MINI_APP_URL}}],
 ];return {inline_keyboard:rows};
}
export const welcome=lang=>lang==='ar'?'📡 *رادار عروض الذكاء الاصطناعي*\nاكتشف عروض الاشتراكات المجانية والمخفضة وواجهات API من مصادر عامة، مع روابط مباشرة وتقييم للمصدر.\n\nأوامر: /today /sources /language /whoami /submit رابط':'📡 *AI Offer Radar*\nFind public AI subscription deals, free tiers and APIs in different languages.\n\nCommands: /today /sources /language /whoami /submit URL';
