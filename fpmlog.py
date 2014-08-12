#!/usr/bin/env python

import sys
import json
from datetime import datetime, timedelta
from heapq import heappush, heappop
from operator import itemgetter
import gzip

# {u'body_bytes_sent': u'154',
# u'handler': u'',
# u'host': u'sonnenbrillen.com',
# u'referer': u'-',
# u'remote_addr': u'66.249.64.239',
# u'remote_user': u'-',
# u'request': u'GET /shop/sonnenbrillen+vollrand/Tom+Ford/Tom+Ford+Sonnenbrille+Callum+FT+0289+S+53E/6-275.00.html HTTP/1.1',
# u'request_time': u'0.000',
# u'status': u'302',
# u'time': u'2014-08-05T06:32:11+00:00',
# u'user_agent': u'Mozilla/5.0 (compatible; Googlebot/2.1; +http://www.google.com/bot.html)'}

NUM_SLOTS = 10

def read_requests(filename):
    opener = gzip.open if filename.endswith('.gz') else open
    requests = []
    with opener(filename) as f:
        skipped = 0
        for line in f:
            try:
                request = json.loads(line)
            except ValueError:
                skipped += 1
                continue

            if request["handler"] != "phpfpm":
                continue

            request["request_time"] = float(request["request_time"])
            request["end_time"] = request["time"] = datetime.strptime(request["time"][:19], "%Y-%m-%dT%H:%M:%S")
            request["time"] = request["time"] - timedelta(seconds=request["request_time"])
            request["time"] = request["time"].replace(microsecond=0)
            requests.append(request)
        if skipped:
            print >>sys.stderr, skipped, "lines skipped because json couldn't be parsed"

    return requests

def stat(num_active):
    return (min(NUM_SLOTS, num_active) * ".").ljust(NUM_SLOTS) + (max(0, num_active - NUM_SLOTS) * "*")

def main(filename):
    requests = read_requests(filename)

    num_active= 0
    endings = []
    for row in sorted(requests, key=itemgetter("time")):
        # Process ended requests
        while endings and endings[0] < row["time"]:
            if num_active > 0:
                num_active -= 1
            else:
                print >>sys.stderr, "Negative workers??!?"
            heappop(endings)

        num_active += 1

        row["stat"] = stat(num_active)
        print "%(time)s %(request_time)7.3f %(stat)s %(remote_addr)-15s -> %(status)s %(host)s %(request)s (%(user_agent)s)" % row

        heappush(endings, row["end_time"])

if __name__ == '__main__':
    try:
        filename = sys.argv[1]
    except IndexError:
        print "Usage: %s <log file name>" % sys.argv[0]
        sys.exit(1)
    main(filename)
