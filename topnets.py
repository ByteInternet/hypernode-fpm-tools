#!/usr/bin/env python

import json
import sys
from datetime import datetime, timedelta
from collections import defaultdict, Counter
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


def read_requests(filename):
    requests = defaultdict(Counter)
    skipped = 0

    opener = gzip.open if filename.endswith('.gz') else open
    with opener(filename) as f:
        for line in f:
            try:
                request = json.loads(line)
            except ValueError:
                skipped += 1
                continue

            request["time"] = datetime.strptime(request["time"][:19], "%Y-%m-%dT%H:%M:%S") - timedelta(seconds=float(request["request_time"]))
            time_bucket = request["time"].replace(minute=int(5 * (request["time"].minute/5)), second=0, microsecond=0)
            network = request["remote_addr"].rsplit(".", 1)[0]
            requests[time_bucket][network] += float(request["request_time"])
        if skipped:
            print >>sys.stderr, skipped, "lines skipped because json couldn't be parsed"

    return requests


def main(filename):
    requests = read_requests(filename)
    for time, counts in sorted(requests.iteritems()):
        print time, 
        for ip, time in counts.most_common(3):
            print "   %-11s %6d" % (ip, time),
        print


if __name__ == '__main__':
    try:
        filename = sys.argv[1]
    except IndexError:
        print "Usage: %s <log file name>" % sys.argv[0]
        sys.exit(1)
    main(filename)
