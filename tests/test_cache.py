import nodeflow as nf

import requests


class Request(nf.Operator):
    def __init__(self, url: nf.Constant):
        super().__init__(url)
        self.url = url

    def __call__(self, url):
        print("call", self)
        response = requests.get(url)
        return response.text

class StripHTML(nf.Operator):
    def __init__(self, html: nf.Operator):
        super().__init__(html)
        self.html:nf.Operator = html

    def __call__(self, html:str):
        import re
        return re.sub('<[^<]+?>', '', html)


url = nf.Variable("https://444.hu")
request = Request(url)
cached_request = nf.Cache(request)
strip = StripHTML(cached_request)
output = strip

# Cache works if call Request print only once!
print("""Make requests!
should call Request only twice. once for each url""")
output.evaluate()
output.evaluate()
url.value = "https://telex.hu/"
result = output.evaluate()
print("""Done!""")