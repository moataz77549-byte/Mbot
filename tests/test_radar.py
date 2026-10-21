import unittest
from datetime import datetime,timezone
from collector.radar import canonical, relevant, classify, rss_xml, digest, report_for, quoted_price

class RadarTest(unittest.TestCase):
    def test_canonical(self):
        self.assertEqual(canonical('http://example.com/a?utm_source=x'),'https://example.com/a')
    def test_bad_scheme(self):
        self.assertEqual(canonical('javascript:alert(1)'),'')
    def test_relevance(self):
        self.assertTrue(relevant('ChatGPT free trial','','https://example.com'))
        self.assertFalse(relevant('leaked api key ChatGPT free trial','','https://example.com'))
    def test_no_unrelated_posts(self):
        self.assertFalse(relevant('Gemini API 403 Error — Free Tier Restricted','','https://example.com'))
        self.assertFalse(relevant('AI content gets hammered by Google SEO updates because it is cheap','','https://example.com'))
        self.assertFalse(relevant('ChatGPT is a helpful assistant','A free trial might exist','https://example.com'))
    def test_mentioned_prices(self):
        self.assertEqual(quoted_price('AI lifetime subscription for $30'), '$30')
    def test_rss(self):
        rows=rss_xml(b'<rss><channel><item><title>ChatGPT free trial</title><link>https://example.com</link></item></channel></rss>','RSS')
        self.assertEqual(len(rows),1)
    def test_source_trust(self):
        now=datetime.now(timezone.utc)
        data={'title':'ChatGPT free trial','summary':'offer','url':'https://openai.com/sale','source':'Bing/en'}
        self.assertEqual(classify(data,now)['trust'],'independent_report')
        data['source']='Direct official RSS'
        self.assertEqual(classify(data,now)['trust'],'official_source')
    def test_digest_limit(self):
        now=datetime.now(timezone.utc)
        items=[classify({'title':'ChatGPT free trial '+'X'*110,'url':'https://example.com/'+str(i),'source':'Bing/en'},now) for i in range(70)]
        rep=report_for(items,now,70)
        self.assertLessEqual(len(digest(rep)),4000)

if __name__=='__main__':unittest.main()
