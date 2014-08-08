# Tools to do root-cause analysis on FPM workers

## topnets.py

Given a (compressed) access log, show for each window of 5 minutes what network
(determined by first 3 quads of the IP address) used the most request time.
Output is timestamp, then the top-3 networks in order of how many seconds the
used with the number of seconds.

## fpmlog.py

Given a (compressed) access log, display the access log ordered by the time the
requests came in, with a graphic display of how many FPM workers are busy and
how many requests are queued after the request came in. These numbers are
projected and highly inaccurate, but might give some clues.
