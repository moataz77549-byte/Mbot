"""Multilingual public AI offers collector. Not a seller endorsement."""
from __future__ import annotations
import argparse, html, hashlib, json, logging, os, re, time
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime, timedelta, timezone
from email.utils import parsedate_to_datetime
from pathlib import Path
from urllib.parse import urlsplit, urlunsplit, urlencode, parse_qsl
from xml.etree import ElementTree as ET
from zoneinfo import ZoneInfo
import requests
from bs4 import BeautifulSoup

ROOT=Path(__file__).resolve().parents[1]
LOG=logging.getLogger("radar")
TZ=ZoneInfo("Asia/Aden")
SESSION=requests.Session()
SESSION.headers.update({"User-Agent":"AIOfferRadar/1.0 (public RSS research)"})
OFFER=("free trial","free tier","discount","promo","coupon","deal","credits","sale","offer",
       "cheap","wholesale","bulk price","special price","% off","save $",
       "خصم","مجاني","تجربة مجانية","عرض","تخفيض","كوبون","سعر مخفض","للجملة",
       "descuento","gratis","oferta","gratuit","réduction","скидка","бесплатно",
       "indirim","ücretsiz","desconto","优惠","免费","رایگان")
TOPIC=("chatgpt","openai","gemini","google ai","grok","xai","claude","anthropic","openrouter",
       "groq","mistral","deepseek","qwen","llama","nvidia","api","llm","tokens"," ai ",
       "ذكاء اصطناعي","شات جي بي تي","جيمناي")
BANNED=("stolen token","leaked api key","cracked account","session cookie","cookie login",
        "hacked api","bypass payment","حسابات مسروقة","توكنات مسربة","كوكيز مسروقة")
OFFICIAL=("openai.com","chatgpt.com","ai.google.dev","aistudio.google.com","cloud.google.com",
          "x.ai","grok.com","docs.x.ai","anthropic.com","openrouter.ai","groq.com",
          "mistral.ai","build.nvidia.com","developer.nvidia.com","huggingface.co")
MAX_AGE=timedelta(days=4)

def clean(value, n=240):
    return re.sub(r"\s+"," ",BeautifulSoup(html.unescape(str(value or "")),"html.parser").get_text(" ",strip=True)).strip()[:n]

def canonical(url):
    try:
        p=urlsplit(str(url).strip())
        if p.scheme not in ("http","https") or not p.hostname:return ""
        host=p.hostname.lower()
        q=[(k,v) for k,v in parse_qsl(p.query) if not k.lower().startswith("utm_") and k.lower() not in ("fbclid","gclid")]
        return urlunsplit(("https",host,p.path.rstrip("/") or "/",urlencode(q),""))
    except ValueError:return ""

BAD_TITLE=("request for review","request to review","request for manual","request for free tier",
           "403 error","403 permission","billing tier unavailable","project restricted",
           "free tier restricted","restricted project","quota clarification","access restricted",
           "google ai developers forum","google ai developer forum","pet insurance",
           "insurance plugin","bond yield","bitcoin when you trade","stock picks",
           "trading signal","active plan offered","3 ways gemini","review complete free trial",
           "i have an active","my google one settings","practical training","i'm hosting a",
           "i’m hosting a","start reselling","teach you","created inside","metro boomin",
           "instrumental","ai content gets","seo system","free tier access restricted",
           "developer forum","please how can","request to review")
def relevant(title,summary,url):
    # The headline must describe a DEAL; body-only mentions trigger false positives.
    headline=title.lower()
    context=(title+" "+summary).lower()
    return (any(t in context for t in TOPIC)
        and (any(t in headline for t in OFFER) or bool(re.search(r"(?<!\w)(?:[$€£]\s*\d+|\d+%\s*off)",headline)))
        and not any(t in context for t in BANNED)
        and not any(t in headline for t in BAD_TITLE))

def parse_date(s):
    try:
        d=parsedate_to_datetime(s) if "," in s else datetime.fromisoformat(s.replace("Z","+00:00"))
        return d.replace(tzinfo=timezone.utc) if d.tzinfo is None else d
    except (TypeError,ValueError,OverflowError):return None

def rss_xml(raw,label):
    try:root=ET.fromstring(raw)
    except ET.ParseError:return []
    entries=[]
    for el in list(root.findall(".//item"))+list(root.findall(".//{http://www.w3.org/2005/Atom}entry")):
        def field(*names):
            for name in names:
                v=el.find(name)
                if v is not None:
                    return v.text or v.get("href") or ""
            return ""
        title=clean(field("title","{http://www.w3.org/2005/Atom}title"),175)
        link=canonical(field("link","{http://www.w3.org/2005/Atom}link"))
        if not title or not link:continue
        summary=clean(field("description","summary","{http://www.w3.org/2005/Atom}summary"),270)
        published=field("pubDate","{http://www.w3.org/2005/Atom}published","{http://www.w3.org/2005/Atom}updated")
        entries.append(dict(title=title,url=link,summary=summary,source=label,published=published))
    return entries

def get_feed(url,label):
    try:
        r=SESSION.get(url,timeout=14,allow_redirects=True);r.raise_for_status()
        if len(r.content)>2_000_000:return []
        return rss_xml(r.content,label)
    except (requests.RequestException,ValueError) as e:
        LOG.warning("Unavailable public feed %s: %s",label,str(e)[:70]);return []

def get_channel(name):
    name=name.strip().lstrip("@")
    if not re.fullmatch("[A-Za-z][A-Za-z0-9_]{4,31}",name):return []
    try:
        r=SESSION.get("https://t.me/s/"+name,timeout=14);r.raise_for_status()
        soup=BeautifulSoup(r.text,"html.parser");out=[]
        for card in soup.select(".tgme_widget_message_wrap")[-25:]:
            body=card.select_one(".tgme_widget_message_text")
            link=card.select_one(".tgme_widget_message_date")
            if not body or not link:continue
            txt=clean(body.get_text(" ",strip=True),450)
            if not relevant(txt,"","https://t.me/"):continue
            ts=link.select_one("time")
            out.append(dict(title=txt[:165],url=canonical(link.get("href","")),summary=txt,
                  source="Telegram @"+name,published=ts.get("datetime","") if ts else ""))
        return out
    except requests.RequestException:return []

def feeds(cfg):
    jobs=[]
    for item in cfg.get("queries",[]):
        lang=item.get("lang","en");country=item.get("country","US");q=item["q"]
        jobs.append(("https://news.google.com/rss/search?"+urlencode({"q":q+" when:4d","hl":lang+"-"+country,"gl":country,"ceid":country+":"+lang}),"Google News/"+lang))
        jobs.append(("https://www.bing.com/search?"+urlencode({"q":q,"format":"rss","setlang":lang}),"Bing/"+lang))
    for h in cfg.get("watched_bot_handles",[]):
        jobs.append(("https://www.bing.com/search?"+urlencode({"q":'"'+h+'" (ChatGPT OR Gemini OR Grok OR API) (discount OR offer OR free)',"format":"rss"}),"Bing/watch"))
    jobs += [(x["url"],x.get("label","Custom RSS")) for x in cfg.get("rss",[])]
    return jobs

def quoted_price(title):
    m=re.search(r"(?i)(?:USD\s*|[$€£]\s*)\d{1,5}(?:[.,]\d{1,2})?|\b\d{1,2}%\s*(?:off|discount|خصم)",title)
    return m.group(0)[:28] if m else None

def classify(entry,now):
    u=canonical(entry["url"])
    title=entry["title"];summary=entry.get("summary","")
    if not u or not relevant(title,summary,u):return None
    d=parse_date(entry.get("published",""))
    if d and (now.astimezone(timezone.utc)-d.astimezone(timezone.utc)>MAX_AGE or d>now+timedelta(hours=5)):return None
    host=urlsplit(u).hostname or ""
    src=entry.get("source","Public")
    official=any(host==x or host.endswith("."+x) for x in OFFICIAL)
    trust="independent_report" if src.startswith(("Bing/","Google News/")) else "official_source" if official else "unverified_third_party"
    s=(title+" "+summary).lower()
    kind="api" if any(x in s for x in ("api","token","credits","توكن")) else "free" if any(x in s for x in ("free","مجاني","gratis","gratuit","бесплатно","免費","免费","ücretsiz")) else "community" if "t.me/" in u else "subscription"
    return dict(id=hashlib.sha256(u.encode()).hexdigest()[:14],title=title,summary=summary,url=u,source=src,
      kind=kind,trust=trust,published_at=d.isoformat() if d else None,price_mentioned=quoted_price(title),
      arabic_title=None,arabic_translated=False,english_title=None,english_translated=False)

def translate(title,source,language):
    # Public translation service expects explicit source/destination codes.
    if source==language:return title,True
    try:
        params={"q":title,"langpair":source+"|"+language}
        if os.getenv("MYMEMORY_CONTACT_EMAIL"):params["de"]=os.environ["MYMEMORY_CONTACT_EMAIL"]
        r=SESSION.get("https://api.mymemory.translated.net/get",params=params,timeout=9)
        r.raise_for_status();res=r.json()
        if res.get("responseStatus")==200:
            translated=clean(res.get("responseData",{}).get("translatedText",""),180)
            if translated and "MYMEMORY WARNING" not in translated.upper():
                return translated,True
    except (requests.RequestException,ValueError,KeyError):pass
    return None,False

def collect(cfg,now):
    jobs=feeds(cfg);out=[]
    with ThreadPoolExecutor(max_workers=7) as pool:
        futures=[pool.submit(get_feed,u,label) for u,label in jobs]
        futures += [pool.submit(get_channel,ch) for ch in cfg.get("telegram_channels",[])]
        for f in as_completed(futures):
            try:
                for e in f.result():
                    item=classify(e,now)
                    if item:out.append(item)
            except Exception as ex:LOG.warning("Could not parse source: %s",str(ex)[:100])
    unique={}
    # Cross-engine duplicates and slightly different syndicated links.
    for item in out:
        titlekey=re.sub(r"[^a-z0-9\u0600-\u06ff]+"," ",item["title"].lower()).strip()[:115]
        key=titlekey if len(titlekey)>15 else item["url"]
        prior=unique.get(key)
        if not prior or (item.get("published_at") or "")>(prior.get("published_at") or ""):unique[key]=item
    out=list(unique.values())
    out.sort(key=lambda x:(x["trust"]=="official_source",bool(x["published_at"]),x["published_at"] or ""),reverse=True)
    out=out[:32]
    # Translate a bounded set. Keep original text visible if the service fails.
    for item in out[:10]:
        title=item["title"]
        if re.search(r"[\u0600-\u06FF]",title):source="ar"
        elif re.search(r"[\u0400-\u04FF]",title):source="ru"
        elif re.search(r"[\u4E00-\u9FFF]",title):source="zh-CN"
        else:
            candidate=item["source"].split("/")[-1]
            source=candidate if candidate in ("en","es","fr","pt","tr","id","de","ru","ar") else "en"
        item["arabic_title"],item["arabic_translated"]=translate(title,source,"ar")
        item["english_title"],item["english_translated"]=translate(title,source,"en")
    return out

def report_for(items,now,scanned):
    kinds=("free","api","subscription","community")
    return dict(project="AI Offer Radar",generated_at=now.isoformat(),timezone="Asia/Aden",
      date=now.strftime("%Y-%m-%d"),scanned_feeds=scanned,count=len(items),
      counts={x:sum(i["kind"]==x for i in items) for x in kinds},items=items,
      disclaimer_ar="الروابط والأسعار ليست ضمانًا؛ تحقّق قبل الدفع.",
      disclaimer_en="Prices and sellers are not verified.")

def digest(report,lang="ar"):
    ar=lang=="ar"
    lines=["📡 رادار عروض الذكاء الاصطناعي" if ar else "📡 AI Offer Radar",
           report["date"]+" • "+str(report["count"]) + (" نتائج" if ar else " findings"),""]
    if not report["items"]:lines.append("لا توجد نتائج حديثة موثقة اليوم." if ar else "No recent results found.")
    for idx,item in enumerate(report["items"][:10],1):
        flag={"official_source":"🏢","independent_report":"📰"}.get(item["trust"],"⚠️")
        title=item.get("arabic_title") if ar else item.get("english_title")
        line=f"{idx}. {flag} {(title or item['title'])[:120]}\n🔗 {item['url']}"
        if len("\n".join(lines+[line]))>3600:break
        lines.extend([line,""])
    lines.append("⚠️ روابط المصدر ليست ضمانًا لصحة العرض." if ar else "⚠️ Verify all offers independently.")
    return "\n".join(lines)[:4000]

def post(token,chat,text):
    if not token or not chat:return False
    r=requests.post("https://api.telegram.org/bot"+token+"/sendMessage",
            json={"chat_id":chat,"text":text,"disable_web_page_preview":True},timeout=18)
    try: data=r.json()
    except ValueError:raise RuntimeError("Telegram response unavailable") from None
    if not data.get("ok"):raise RuntimeError("Telegram send failed: "+str(data.get("description","unknown"))[:120])
    return True

def main():
    p=argparse.ArgumentParser();p.add_argument("--publish",action="store_true")
    p.add_argument("--dry-run",action="store_true",help="Save empty report without network")
    args=p.parse_args();logging.basicConfig(level=logging.INFO,format="%(levelname)s %(message)s")
    now=datetime.now(TZ);cfg=json.loads((ROOT/"sources.json").read_text(encoding="utf-8"))
    items=[] if args.dry_run else collect(cfg,now)
    report=report_for(items,now,len(feeds(cfg))+len(cfg.get("telegram_channels",[])))
    dest=ROOT/"data";dest.mkdir(exist_ok=True);(dest/"archive").mkdir(exist_ok=True)
    data=json.dumps(report,ensure_ascii=False,indent=2)+"\n"
    (dest/"latest.json").write_text(data,encoding="utf-8")
    (dest/"archive"/(report["date"]+".json")).write_text(data,encoding="utf-8")
    LOG.info("Scan completed: %d items from %d configured public endpoints",report["count"],report["scanned_feeds"])
    if args.publish:
        if not os.getenv("TELEGRAM_BOT_TOKEN") or not os.getenv("TELEGRAM_AR_CHAT_ID"):
            LOG.warning("Channel not configured; feed updated but no message delivered")
        else:
            post(os.environ["TELEGRAM_BOT_TOKEN"],os.environ["TELEGRAM_AR_CHAT_ID"],digest(report))
            if os.getenv("TELEGRAM_EN_CHAT_ID"):
                post(os.getenv("TELEGRAM_EN_BOT_TOKEN") or os.environ["TELEGRAM_BOT_TOKEN"],os.environ["TELEGRAM_EN_CHAT_ID"],digest(report,"en"))
            LOG.info("Digest delivery completed")
if __name__=="__main__":main()
