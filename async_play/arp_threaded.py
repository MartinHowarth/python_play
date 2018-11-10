import threading
from multiprocessing.queues import Queue
from scapy.all import *


recv_queue = Queue()


def single_threaded():
    arp = ARP(op=ARP.who_has, psrc='192.168.0.14', pdst='192.168.0.33')

    results, unanswered = sr(arp)
    print(results, unanswered)


def recv_forever():
    def recv_handler(_packet):
        recv_queue.put(_packet)

    sniff(prn=recv_handler, filter="arp")


def recv_worker():
    while True:
        _packet = recv_queue.get()
        if _packet.haslayer(ARP):
            arp_layer = _packet.getlayer(ARP)
            print("[!] New ARP: {hwsrc}".format(hwsrc=arp_layer.hwsrc))
        if _packet.haslayer(IP):
            ip_layer = _packet.getlayer(IP)
            print("[!] New Packet: {src} -> {dst}".format(src=ip_layer.src, dst=ip_layer.dst))


if __name__ == "__main__":
    recv_thread = threading.Thread(target=recv_forever)
    recv_thread.start()

    recv_worker_thread = threading.Thread(target=recv_worker)
    recv_worker_thread.start()

    input("...")
