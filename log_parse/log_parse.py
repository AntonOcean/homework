# -*- encoding: utf-8 -*-
import re
from datetime import datetime
from collections import Counter


def get_urls(
    ignore_files=False,
    ignore_urls=[],
    start_at=None,
    stop_at=None,
    request_type=None,
    ignore_www=False,
    slow_queries=False
):
    urls = []
    pattern = r'^\[(\d{2}\/\w{3}\/\d{4} \d{2}:\d{2}:\d{2})\] \"(.*)\" (\d+) (\d+)'
    with open('log.log', 'r') as file:
        for line in file:
            log = re.search(pattern, line.strip())
            if log:
                date, response, status_code, timer = log.groups()
                method, url, protocol = response.split()
                date = datetime.strptime(date, '%d/%b/%Y %H:%M:%S')
                url = url.split('//')[1].split('?')[0]
                postfix_file = r'\.\w+$'
                if (not ignore_files or not re.search(postfix_file, url)) and \
                        (url not in ignore_urls) and \
                        (not request_type or request_type == method) and \
                        (not stop_at or date < stop_at) and \
                        (not start_at or date > start_at):
                    if ignore_www:
                        url = re.sub(r'^www\.', '', url)
                    if slow_queries:
                        urls.append((url, int(timer)))
                    else:
                        urls.append(url)
    return urls


def parse(
    ignore_files=False,
    ignore_urls=[],
    start_at=None,
    stop_at=None,
    request_type=None,
    ignore_www=False,
    slow_queries=False
):
    urls = get_urls(ignore_files, ignore_urls, start_at, stop_at, request_type, ignore_www, slow_queries)
    if slow_queries:
        slow_urls = {}
        for url, time in urls:
            if url not in slow_urls:
                slow_urls[url] = [time, ]
            else:
                slow_urls[url].append(time)
        urls = [(url, time_list) for url, time_list in slow_urls.items()]
        urls.sort(key=lambda x: max(x[1]), reverse=True)
        top_slow_urls = urls[:5]
        res = [int(sum(timing)/len(timing)) for url, timing in top_slow_urls]
        res.sort(reverse=True)
    else:
        res = [num for url, num in Counter(urls).most_common(5)]
    return res


if __name__ == '__main__':
    # stop_at = datetime.strptime('2018-03-28', '%Y-%m-%d')
    # start_at = datetime.strptime('2018-03-28', '%Y-%m-%d')
    print(parse(ignore_www=True))
