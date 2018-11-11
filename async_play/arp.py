import asyncio
import ipaddress
import socket
import time
from struct import pack, unpack
from typing import Dict
from uuid import getnode as get_mac


class DataEvent(asyncio.Event):
    def __init__(self, *args, **kwargs):
        self.data = None
        super(DataEvent, self).__init__(*args, **kwargs)


def ip_to_bytes(ip: ipaddress.IPv4Address):
    x = int(ip)
    return x.to_bytes((x.bit_length() + 7) // 8, 'big')


def mac_to_bytes(mac: str):
    return pack('!6B', *[int(segment, 16) for segment in mac.split(':')])


def mac_str_from_bytes(mac_bytes):
    return ':'.join(a + b for a, b in zip(*[iter(mac_bytes.hex())] * 2))


def ip_from_bytes(ip_bytes):
    return ipaddress.IPv4Address(socket.inet_ntoa(ip_bytes))


def arp_factory_from_source(source_mac: str, source_ip: ipaddress.IPv4Address):
    source_mac_bytes = mac_to_bytes(source_mac)
    source_ip_bytes = ip_to_bytes(source_ip)

    def make_arp(dest_ip: ipaddress.IPv4Address):
        dest_ip_bytes = ip_to_bytes(dest_ip)
        return b''.join([
            ### ETHERNET header###
            # Destination MAC address (=broadcast) :
            pack('!6B', *(0xFF,) * 6),
            # Source MAC address :
            source_mac_bytes,
            # Type of protocol (=ARP) :
            pack('!H', 0x0806),

            ### ARP payload###
            # Type of protocol hw/soft (=Ethernet/IP) :
            pack('!HHBB', 0x0001, 0x0800, 0x0006, 0x0004),
            # Operation (=ARP Request) :
            pack('!H', 0x0001),
            # Source MAC address :
            source_mac_bytes,
            # Source IP address :
            source_ip_bytes,
            # Destination MAC address (what we are looking for) (=00*6) :
            pack('!6B', *(0,) * 6),
            # Target IP address:
            dest_ip_bytes
        ])
    return make_arp


def parse_arp(packet, _local_mac_bytes):
    ethernet_header = packet[0:14]
    ethernet_detail = unpack("!6s6s2s", ethernet_header)
    if ethernet_detail[2] == b'\x08\x06':  # ARP only
        arp_header = packet[14:42]
        arp_detail = unpack("2s2s1s1s2s6s4s6s4s", arp_header)
        # print(arp_detail[7])
        # print('remote_mac', ':'.join(a + b for a, b in zip(*[iter(arp_detail[5].hex())] * 2)))
        # print('smac', ':'.join(a + b for a, b in zip(*[iter(arp_detail[7].hex())] * 2)))
        # print("local mac", mac_str_from_bytes(_local_mac_bytes))
        # print(4, arp_detail[4])
        # print("sip", ip_from_bytes(arp_detail[6]))
        # print("dip", ip_from_bytes(arp_detail[8]))

        if arp_detail[4] == b'\x00\x02' and arp_detail[7] == _local_mac_bytes:  # Replies to me only
            return {
                "remote_mac": mac_str_from_bytes(arp_detail[5]),  # MAC of remote
                "remote_ip": ip_from_bytes(arp_detail[6]),  # IP of remote
                "local_mac": mac_str_from_bytes(arp_detail[7]),  # MAC of original sender of ARP request
                "local_ip": ip_from_bytes(arp_detail[8]),  # IP of sender of original ARP request
            }


async def send_forever(_socket, queue):
    while True:
        _packet = await queue.get()
        await loop.sock_sendall(_socket, _packet)


async def recv_forever(_socket, queue):
    while True:
        _packet = await loop.sock_recv(_socket, 65565)
        await queue.put(_packet)


async def recv_worker(queue, source_mac: str, probe_map: Dict):
    source_mac_bytes = mac_to_bytes(source_mac)
    while True:
        _packet = await queue.get()
        result = parse_arp(_packet, source_mac_bytes)
        if result is not None:
            ip = result['remote_ip']
            # probe_map[ip][1].data = result
            probe_map[ip][1].set()


def create_arp_probe_coro(arp_factory, target_ip: ipaddress.IPv4Address, interval: float = 0.5, timeout: float = 0.25):
    global results
    event = DataEvent()
    assert interval > timeout

    async def arp_send_loop():
        arp = arp_factory(target_ip)
        while True:
            send_time = time.time()
            await send_queue.put(arp)
            try:
                await asyncio.wait_for(event.wait(), timeout)
                # result = event.data
                # print(result)
                recv_time = time.time()
                time_taken = recv_time - send_time
                results[target_ip] = 1
            except asyncio.TimeoutError:
                # print("TOOK TOO LONG!!!")
                time_taken = timeout
                results[target_ip] = 0
            finally:
                event.clear()
            # print(f"time for response: {time_taken}")
            sleep_time = interval - time_taken
            if sleep_time > 0:
                await asyncio.sleep(interval - time_taken)
            else:
                print("We're falling behind schedule.")
    return arp_send_loop(), event


async def results_printer():
    global results
    while True:
        await asyncio.sleep(1)
        print(sum(results.values()))
        for ip, value in results.items():
            if value:
                print(ip)


if __name__ == "__main__":

    recv_queue = asyncio.Queue()
    send_queue = asyncio.Queue()
    local_mac_str = ':'.join([("%x" % get_mac())[i:i + 2] for i in range(0, 12, 2)])
    local_ip = ipaddress.IPv4Address('192.168.0.33')

    sock = socket.socket(socket.AF_PACKET, socket.SOCK_RAW, socket.htons(3))
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
    sock.setblocking(False)
    sock.bind(('eth0', 0))

    event_map = dict()

    loop = asyncio.get_event_loop()
    recv_coro = recv_forever(sock, recv_queue)
    send_coro = send_forever(sock, send_queue)

    results = {}

    targets = [
        # ipaddress.IPv4Address('192.168.0.14'),
        # ipaddress.IPv4Address('192.168.0.1'),
        # ipaddress.IPv4Address('192.168.0.11'),
    ]
    for ii in range(1, 256):
        targets.append(ipaddress.IPv4Address('192.168.0.1'))

    arp_probes = {
        ip: create_arp_probe_coro(arp_factory_from_source(local_mac_str, local_ip), ip)
        for ip in targets
    }
    arp_coros = [probe[0] for probe in arp_probes.values()]
    work_coro = recv_worker(recv_queue, local_mac_str, arp_probes)

    results_coro = results_printer()

    loop.run_until_complete(asyncio.gather(recv_coro, work_coro, send_coro, results_coro, *arp_coros))
    loop.close()
