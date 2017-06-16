#!/usr/bin/env python3
from urllib import parse
from multiprocessing import Pool
from lib.core.Util import Util


class DirScanner:
    @staticmethod
    def scan(root_url, dir_list, thread_count):
        print("Checking for additional directories to search...")
        dir_urls = []
        dir_lines = Util.read_file_into_array(dir_list)

        for dir_line in dir_lines:
            dir_urls.append(parse.urljoin(root_url, dir_line))

        thread_pool = Pool(int(thread_count))
        found_dirs = thread_pool.map(DirScanner.scan_dirs_threaded, dir_urls)

        thread_pool.close()
        thread_pool.join()
        return found_dirs

    @staticmethod
    def scan_dirs_threaded(url):
        if Util.is_200_response(url):
            url = url.rstrip()
            if not url.endswith('/'):
                url += '/'

            print("[200 - OK] Directory found: ", url)
            return url
