import nodeflow as nf

import requests
import unittest

class Request(nf.Operator):
    def __init__(self, url: nf.Constant):
        super().__init__(url)

    def __call__(self, url):
        print("call", self)
        response = requests.get(url)
        return response.text


class CacheOperator(unittest.TestCase):
    def test_request(self):
        import requests
        
        url = nf.Variable("https://444.hu")
        request = Request(url)
        cached_request = nf.Cache(request)
        output = cached_request

        # Cache works if call Request print only once!
        print("""Make requests!
        should call Request only twice. once for each url""")
        output.evaluate()
        output.evaluate()
        url.value = "https://telex.hu/"
        result = output.evaluate()
        print("""Done!""")

        # test against raw requests lib
        self.assertEqual(requests.get(url.value).text[:10], result[:10])


if __name__ == '__main__':
    unittest.main(verbosity=2)