import pathlib, unittest
from html.parser import HTMLParser
ROOT=pathlib.Path(__file__).resolve().parents[1]/"interface/preview"
class Tags(HTMLParser):
 def __init__(self): super().__init__();self.ids=set();self.views=set()
 def handle_starttag(self,tag,attrs):
  attrs=dict(attrs)
  if attrs.get("id"):self.ids.add(attrs["id"])
  if attrs.get("data-view"):self.views.add(attrs["data-view"])
class PreviewTests(unittest.TestCase):
 def test_required_views(self):
  p=Tags();p.feed((ROOT/"index.html").read_text())
  self.assertTrue({"home","library","online","settings","notice","contrast"}<=p.ids)
  self.assertEqual(p.views,{"home","library","online","settings"})
 def test_offline_first(self):
  h=(ROOT/"index.html").read_text()
  self.assertNotIn("https://",h)
  self.assertIn("OFFLINE MODE",h)
  self.assertIn("Not available in preview",h)
