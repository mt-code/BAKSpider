#!/usr/bin/env python3
import re, math, random, string
from os.path import splitext
from urllib import request
from urllib.parse import urlparse
from collections import Counter

fake_page_word_dict = {}


class WebPage:
    def __init__(self, body):
        self.regex = re.compile(r'\w+')
        self.body = body

    def get_word_dict(self):
        body = self.body.read().decode(self.body.headers.get_content_charset() or "UTF-8")
        word_vector = self.regex.findall(body)

        return Counter(word_vector)

    # Credit: https://stackoverflow.com/users/1859772/vpekar
    def get_cosine_sim(self, other_dict):
        orig_dict = self.get_word_dict()

        intersection = set(orig_dict.keys()) & set(other_dict.keys())
        numerator = sum([orig_dict[x] * other_dict[x] for x in intersection])

        sum1 = sum([orig_dict[x] ** 2 for x in orig_dict.keys()])
        sum2 = sum([other_dict[x] ** 2 for x in other_dict.keys()])

        denominator = math.sqrt(sum1) * math.sqrt(sum2)

        if not denominator:
            return 0.0
        else:
            return float(numerator) / denominator


# TODO: Use different is_200_response function without global if not needed, performance impact is large currently.
class WebUtils:
    @staticmethod
    def is_200_response(url):
        try:
            body = request.urlopen(url)

            if body.getcode() == 200:
                url_page = WebPage(body)

                #global fake_page_word_dict
                if not fake_page_word_dict:
                    return True
                else:
                    cosine_sim = url_page.get_cosine_sim(fake_page_word_dict)

                    if cosine_sim < 0.85:  # TODO: Perhaps allow user to set a custom value?
                        return True
                    else:
                        return False

        except Exception:
            return False

    @staticmethod
    def is_valid_spider_url(url):
        if url.startswith("http"):
            return True

        return False

    @staticmethod
    def is_valid_target_url(url):
        if url.startswith("http") and "://" in url and url.endswith('/'):
            return True

        return False

    @staticmethod
    def get_url_extension(url):
        path = urlparse(url).path
        ext = splitext(path)[1]

        return ext[1:].split(':')[0]

    @staticmethod
    def site_has_valid_response_codes(url):
        test_url = WebUtils.generate_random_url(url, 40)

        try:
            test_body = request.urlopen(test_url)

            if test_body.getcode() == 200:
                test_page = WebPage(test_body)

                global fake_page_word_dict
                fake_page_word_dict = test_page.get_word_dict()
                return False

        except Exception:
            return True

        return True

    @staticmethod
    def generate_random_url(base_url, length):
        seq = string.ascii_lowercase + string.ascii_uppercase + string.digits

        return "{0}{1}".format(base_url, ''.join(random.choice(seq) for _ in range(length)))
