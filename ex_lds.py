from asyncua import ua, Server
from asyncua.server.server import InternalServer
from asyncua.ua.uaprotocol_auto import RegisteredServer

import asyncio
import uvloop


class InternalLocalDiscoveryService(InternalServer):
    def __init__(self):
        super().__init__()
        self.loop = asyncio.get_running_loop()
        self._known_servers_expired_registered = dict()

    def find_servers(self, params, sockname):
        print(f"Servers known: {self._known_servers}")
        
        for key, val in self._known_servers_expired_registered.items():
            task: asyncio.Task = val

            if task.done() is True and key in self._known_servers:
                del self._known_servers[key]

        return super().find_servers(params)

    def register_server(self, server: RegisteredServer, conf=None):
        if server.ServerUri not in self._known_servers_expired_registered:
            # cria um novo registro
            print(f"New server registered: {server.ServerUri}")
            self._known_servers_expired_registered[server.ServerUri] = self.loop.create_task(
                self.task_expired_register(),
                name=str(server.ServerUri)
            )

        else:
            # renova o registro
            print(f"Server re-registered: {server.ServerUri}")
            task: asyncio.Task = self._known_servers_expired_registered[server.ServerUri]
            task.cancel()

            self._known_servers_expired_registered[server.ServerUri] = self.loop.create_task(
                self.task_expired_register(),
                name=str(server.ServerUri)
            )

        super().register_server(server, conf)

    async def task_expired_register(self):
        """
        Se elq for concluida, quer dizer que o Servidor esta offline
        """
        await asyncio.sleep(20)


class LocalDiscoveryService(Server):
    def __init__(self):
        iserver = InternalLocalDiscoveryService()
        super().__init__(iserver)


async def main():
    server = LocalDiscoveryService()
    await server.init()
    server.set_endpoint('opc.tcp://0.0.0.0:4840')
    server.set_server_name('Local Discovery Service')

    async with server:
        while True:
            await asyncio.sleep(1)


if __name__ == '__main__':
    asyncio.set_event_loop_policy(uvloop.EventLoopPolicy())
    asyncio.run(main(), debug=False)
