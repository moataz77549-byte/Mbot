# AI Offer Radar | رادار عروض الذكاء الاصطناعي

بوت Telegram Serverless ثنائي اللغة ولوحة Mini App مع مجمّع يومي من المصادر العامة. المستودع مخصص للبوت `@Moatazahai1bot` بشرط تأكيد المعرّف من BotFather.

## التكوين

- البوت يعمل في Telegram Serverless باستخدام JavaScript وSQLite؛ مجمع بحث Python يعمل عبر GitHub Actions الساعة **18:00 UTC / 21:00 Asia/Aden** يوميًا، مع إمكانية التأخر بسبب جدولة GitHub.
- يستخدم Google News وBing RSS بلغات متعددة وروابط عامة (قنوات Telegram العامة عند إضافتها إلى `sources.json`). لا تصل العملية إلى مجموعات WhatsApp أو Facebook الخاصة.
- النتيجة في `data/latest.json` وعرضها عبر `tgcloud/endpoints/dashboard.js`. كل رابط يبيّن إن كان رسميًا أو منشورًا مستقلاً أو مصدرًا غير موثق؛ لا توجد ضمانات للأسعار.
- لوحة التحكم عربية/إنجليزية والأزرار شفافة؛ تسمح بالبحث والتصفية واقتراح مصادر، وعرض الاقتراحات للمدير المحدد.

## مفاتيح GitHub Actions (لا توضع في الكود)

افتح [Actions Secrets](https://github.com/moataz77549-byte/Mbot/settings/secrets/actions) وأنشئ هذه القيم:

| Secret | Purpose |
| --- | --- |
| `TGCLOUD_TOKEN` | رمز `app...:...` من BotFather → Serverless → CLI Access؛ نشر إلى تيليجرام |
| `TELEGRAM_BOT_TOKEN` | Bot API token الخاص بالبث المسائي فقط |
| `TELEGRAM_AR_CHAT_ID` | Chat ID لمحادثة مع البوت، أو `@public_channel` للبوت المشرف عليها |
| `TELEGRAM_EN_CHAT_ID` | اختياري للنشرة الإنجليزية |
| `TELEGRAM_EN_BOT_TOKEN` | اختياري إذا كانت قناة الإنجليزية على بوت آخر |
| `MYMEMORY_CONTACT_EMAIL` | اختياري لتوسيع هامش ترجمة العناوين العامة |

**تنبيه**: رموز الاعتماد التي نُشرت داخل محادثة يجب تجديدها من BotFather، ثم حفظ الرموز الجديدة داخل Secrets حصراً. لا تقم بكتابتها في ملفات GitHub أو مدخلات workflow_dispatch.

## نشر البوت

1. فعّل Serverless للبوت من BotFather وتأكد من هوية بوتك.
2. أضف `TGCLOUD_TOKEN` إلى Secrets، ثم نفّذ [Deploy Telegram Serverless](https://github.com/moataz77549-byte/Mbot/actions/workflows/deploy-serverless.yml) عبر **Run workflow**.
3. ينفذ الإجراء `npm install` و `npm run build` ثم `npx tgcloud push` و`npx tgcloud migrate --safe`؛ تنشر Mini App داخل Telegram وتُنشأ الجداول الآمنة.
4. بعد أن يعمل البوت، افتح `/start` و`/whoami`. عيّن معرف المدير في `tgcloud/lib/config.js` داخل `ADMIN_IDS` ثم أعد النشر.
5. أضف البوت إلى القناة كمشرف قادر على النشر، وسجل `TELEGRAM_BOT_TOKEN` و`TELEGRAM_AR_CHAT_ID` في Secrets.
6. شغل [Daily AI Offer Radar](https://github.com/moataz77549-byte/Mbot/actions/workflows/daily-radar.yml) يدويًا مع `publish=false` لفحص البحث الحي، ثم `publish=true` لاختبار أول رسالة؛ بعد ذلك سينفذ الجدول كل ليلة تلقائيًا.

يمكن استخدام المحادثة الخاصة مكان القناة، بشرط أن تكون قد ضغطت Start للبوت وأن يعرف النظام Chat ID الخاص بك.

## تشغيل الاختبارات

```bash
python -m pip install -r requirements.txt
python -m unittest discover -s tests -v
npm run check
npm run build
# local deploy requires Node and TGCLOUD_TOKEN environment variable
TGCLOUD_TOKEN='(set locally, never commit)' npx tgcloud push
```

## حدود البحث والأمان

هذا أداة اكتشاف وليست متجرًا. النتائج تأتي من خلاصات بحث عامة، وليست مراجعة مالية أو ضمان عمل الحسابات أو صلاحية API. لا يطلب المشروع كلمات مرور أو مفاتيح مشترين، ولا يدرج بيانات اعتماد مسرّبة. يصنّف عروض الجهات المستقلة بوضوح، ولا يؤكد البائعين تلقائيًا. خدمة الترجمة الخارجية قد تفشل أو تفرض حصصًا؛ يعرض عندها العنوان بلغته الأصلية دون ادعاء ترجمة ناجحة. البوتان اللذان اقترحهما المستخدم ضمن `watched_bot_handles` أهداف بحث، لا توصية بشرائهما.

## ملاحظة النشر

وجود الملف في GitHub ليس تأكيدًا بأن Telegram Serverless نُشر فعليًا. راجع سجل `Deploy Telegram Serverless`، وتأكد من نجاح `push` و`migrate`. غياب Secret يؤدي لتجاوز النشر بدل تسريب بيانات.
