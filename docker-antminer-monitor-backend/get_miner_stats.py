#!/usr/bin/python
import socket
import json
import re
import os
import sys, getopt, time
from influxdb import InfluxDBClient

class CgminerAPI_priv(object):
    """ Cgminer RPC API wrapper. """
    def __init__(self, host='localhost', port=4028):
        self.data = {}
        self.host = host
        self.port = port

    def command(self, command, arg=None):
        """ Initialize a socket connection,
        send a command (a json encoded dict) and
        receive the response (and decode it).
        """
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(5.0)

        try:
            sock.connect((self.host, self.port))
            payload = {"command": command}
            if arg is not None:
                # Parameter must be converted to basestring (no int)
                payload.update({'parameter': unicode(arg)})

            sock.send(json.dumps(payload))
            received = self._receive(sock)
        finally:
            sock.shutdown(socket.SHUT_RDWR)
            sock.close()

        return received[:-1]

    def _receive(self, sock, size=4096):
        msg = ''
        while 1:
            chunk = sock.recv(size)
            if chunk:
                msg += chunk
            else:
                break
        return msg

    def __getattr__(self, attr):
        """ Allow us to make command calling methods.

        >>> cgminer = CgminerAPI()
        >>> cgminer.summary()

        """
        def out(arg=None):
            return self.command(attr, arg)
        return out

def main(argv):
    host = os.environ.get('MINER_HOST')
    db_host = os.environ.get('MINER_DB_HOST')

    try:
        opts, args = getopt.getopt(argv,"h:d:")
    except getopt.GetoptError:
        print 'Usage: get_miner_stats.py -h host -d influxdb_host'
        sys.exit(2)

    for opt, arg in opts:
        if opt == '-h':
            host = arg
        elif opt == '-d':
            db_host = arg

    if host == None or db_host == None:
        print 'Usage: get_miner_stats.py -h host -d influxdb_host'
        sys.exit(2)

    miner = CgminerAPI_priv(host=host)
    client = InfluxDBClient(db_host, 8086, 'root', 'root', 'stats')
    client.create_database('stats')

    while 1:
        stats_j = json.loads(re.sub('}{', '},{', miner.command("stats")))

        json_body = [
                {
                    "measurement": "temp1",
                    "fields": { "value": stats_j["STATS"][1]["temp1"] }
                }, {
                    "measurement": "temp2",
                    "fields": { "value": stats_j["STATS"][1]["temp2"] }
                }, {
                    "measurement": "temp3",
                    "fields": { "value": stats_j["STATS"][1]["temp3"] }
                }, {
                    "measurement": "temp2_1",
                    "fields": { "value": stats_j["STATS"][1]["temp2_1"] }
                }, {
                    "measurement": "temp2_2",
                    "fields": { "value": stats_j["STATS"][1]["temp2_2"] }
                }, {
                    "measurement": "temp2_3",
                    "fields": { "value": stats_j["STATS"][1]["temp2_3"] }
                }, {
                    "measurement": "ghs",
                    "fields": { "value": stats_j["STATS"][1]["GHS av"] }
                }
                ]

        client.write_points(json_body)

        print stats_j["STATS"][1]["temp1"]
        print stats_j["STATS"][1]["temp2"]
        print stats_j["STATS"][1]["temp3"]
        print stats_j["STATS"][1]["temp2_1"]
        print stats_j["STATS"][1]["temp2_2"]
        print stats_j["STATS"][1]["temp2_3"]
        print stats_j["STATS"][1]["GHS av"]

        time.sleep(10)

if __name__ == "__main__":
    main(sys.argv[1:])

