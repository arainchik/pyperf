import socket
import time
import sys
try:
    import hashlib
except ImportError:
    hashlib = False

from optparse import OptionParser

PORT=55555

def process_server(opt, args):
    print "Entering Server mode"
    print "Listening on port", opt.portnumber
    s = socket.socket(family=socket.AF_INET, type=socket.SOCK_STREAM)

    if opt.bind_to_host:
       print "Binding to ", opt.bind_to_host

    s.bind((opt.bind_to_host, opt.portnumber))
    if opt.window:
        s.setsockopt(socket.SOL_SOCKET, socket.SO_SNDBUF, opt.window)
        s.setsockopt(socket.SOL_SOCKET, socket.SO_RCVBUF, opt.window)

    if opt.congestion:
        s.setsockopt(socket.IPPROTO_TCP, 13, opt.congestion)
        print "Setting congestion avoiding algo to: ", opt.congestion
    # TCP_CONGESTION in /usr/include/linuxr/.tcp.h /usr/include/netinet/tcp.h

    print "TCP Window size RECV:", s.getsockopt(socket.SOL_SOCKET, socket.SO_RCVBUF), "SEND:", s.getsockopt(socket.SOL_SOCKET, socket.SO_SNDBUF)

    s.listen(1)



    while True:
        if opt.checksum:
            xsum = hashlib.md5()

        conn, addr = s.accept()
        print "Connection from", addr[0], "port", addr[1]
        t_start = time.time()
        transferred = 0

        while True:
            data = conn.recv(opt.buflen)
            if not data:
                break
            transferred += len(data)
            if opt.checksum:
                xsum.update(data)

        t_total = time.time() - t_start
        conn.close()

        print "Received %d bytes in %.2f seconds"  % (transferred, t_total)
        print "Speed %.2f B/sec %.2f KB/sec %.2f MB/sec" % (transferred/t_total, transferred/t_total/1024,transferred/t_total/(1024*1024))
        if opt.checksum:
            print "Checksum", xsum.hexdigest()


def process_client(opt, args):
    print "Entering Client mode"
    print "Connecting to", opt.connect_to_hostname, "port", opt.portnumber, "buffer size", opt.buflen, "bytes time", opt.time, "seconds" 
    buf = " " * opt.buflen
    s = socket.socket(family=socket.AF_INET, type=socket.SOCK_STREAM)


    if opt.bind_to_host:
        s.bind((opt.bind_to_host, 0))
        print "Binding to ", opt.bind_to_host

    if opt.window:
        s.setsockopt(socket.SOL_SOCKET, socket.SO_RCVBUF, opt.window)
        s.setsockopt(socket.SOL_SOCKET, socket.SO_SNDBUF, opt.window)


    if opt.qos:
        s.setsockopt(socket.IPPROTO_IP, socket.IP_TOS, opt.qos)


    if opt.congestion:
        s.setsockopt(socket.IPPROTO_TCP, 13, opt.congestion)
        print "Setting congestion avoiding algo to: ", opt.congestion
    # TCP_CONGESTION in /usr/include/linuxr/.tcp.h /usr/include/netinet/tcp.h


    print "TCP Window size RECV:", s.getsockopt(socket.SOL_SOCKET, socket.SO_RCVBUF), "SEND:", s.getsockopt(socket.SOL_SOCKET, socket.SO_SNDBUF)

    s.connect((opt.connect_to_hostname, opt.portnumber))

    if opt.checksum:
        xsum = hashlib.md5()


    t_start = time.time()
    transferred = 0
    while time.time() - t_start < opt.time:
        s.send(buf)
        transferred += opt.buflen
        if opt.checksum:
            xsum.update(buf)


    t_total = time.time() - t_start
    s.close()
    print "Transferred  %d bytes in %.2f seconds"  % (transferred, t_total)
    print "Speed %.2f B/sec %.2f KB/sec %.2f MB/sec" % (transferred/t_total, transferred/t_total/1024,transferred/t_total/(1024*1024))
    if opt.checksum:
        print "Checksum", xsum.hexdigest()



parser = OptionParser()
parser.add_option('-s', '--server', action="store_true", dest="server_mode")
parser.add_option('-c', '--client', action="store", type="string", dest="connect_to_hostname")

if hashlib:
    parser.add_option('-X', '--checksum', action="store_true", dest="checksum")

parser.add_option('-W', '--window', type='int', dest='window')
parser.add_option('-B', '--bind', dest="bind_to_host", type="string", default='')
parser.add_option('-l', '--len', dest="buflen", type="int", default=8192)
parser.add_option('-p', '--port', dest="portnumber", type="int", default=PORT)
parser.add_option('-t', '--time', dest="time", type="int", default=10, help="Time to run a test")
parser.add_option('-Q', '--qos', dest="qos", type="int", default=0)
parser.add_option('-C', '--congestion', dest="congestion", type="string", default='', help="Specify congestion aviodance algorithm, like reno or cubic")

opt,args = parser.parse_args()

if opt.server_mode and opt.connect_to_hostname:
    print "-s and -c are mutually exclusive"
    sys.exit(-1)


if opt.server_mode:
    process_server(opt, args)
    sys.exit(0)

if opt.connect_to_hostname:
    process_client(opt, args)
    sys.exit(0)

print "-s or -c has to be selected"
sys.exit(-1)

