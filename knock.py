#!/usr/bin/env python3

import argparse
import select
import socket
import sys
import time


class Knocker(object):
    def __init__(self, args: list):
        self._parse_args(args)

    def _parse_args(self, args: list):
        parser = argparse.ArgumentParser(description=' port-knocking клиент на python3.\n')

        parser.add_argument('-t', '--timeout', type=int, default=200,
                            help='продолжительность ожиданий. По умолчанию, 200 мс.')
        parser.add_argument('-d', '--delay', type=int, default=200,
                            help='Ожидание между каждым стуком. По умолчанию 200 мс.')
        parser.add_argument('-u', '--udp', help='Использовать UDP вместо TCP по умолчанию.', action='store_true')
        parser.add_argument('host', help='Имя узла или IP адрес для  Port Knock. Поддерживает IPv6.')
        parser.add_argument('ports', metavar='port[:protocol]', nargs='+',
                            help='Порт(ы) для «стука», протокол (tcp, udp) опционально.')

        args = parser.parse_args(args)
        self.timeout = args.timeout / 1000
        self.delay = args.delay / 1000
        self.default_udp = args.udp
        self.ports = args.ports
        self.verbose = args.verbose

        self.address_family, _, _, _, ip = socket.getaddrinfo(
            host=args.host,
            port=None,
            flags=socket.AI_ADDRCONFIG
        )[0]
        self.ip_address = ip[0]

    def knock(self):
        last_index = len(self.ports) - 1
        for i, port in enumerate(self.ports):
            use_udp = self.default_udp
            if port.find(':') != -1:
                port, protocol = port.split(':', 2)
                if protocol == 'tcp':
                    use_udp = False
                elif protocol == 'udp':
                    use_udp = True
                else:
                    error = 'Неверный протокол "{}". Разрешенные значения "tcp" и "udp".'
                    raise ValueError(error.format(protocol))

            if self.verbose:
                print('hitting %s %s:%d' % ('udp' if use_udp else 'tcp', self.ip_address, int(port)))

            s = socket.socket(self.address_family, socket.SOCK_DGRAM if use_udp else socket.SOCK_STREAM)
            s.setblocking(False)

            socket_address = (self.ip_address, int(port))
            if use_udp:
                s.sendto(b'', socket_address)
            else:
                s.connect_ex(socket_address)
                select.select([s], [s], [s], self.timeout)

            s.close()

            if self.delay and i != last_index:
                time.sleep(self.delay)


if __name__ == '__main__':
    Knocker(sys.argv[1:]).knock()
