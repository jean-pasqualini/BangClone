from PodSixNet.Channel import Channel
from PodSixNet.Server import Server
import time, math


class ClientChannel(Channel):
    def Network(self, data):
        print(data)

    def Network_card(self, data):
        print(f"card: {data['card']}")

class GameServer(Server):
    """"""
    channelClass = ClientChannel

    def __init__(self, *args, **kwargs):
        super().__init__(self, *args, **kwargs)
        print('Server launched')

    def Connected(self, channel, addr):
        """This method will be called whenever 
        a new client connects to the server.
        """
        print("somebody connected")
        channel.Send({"action": "hello", "message": "hello client!"})


gameserver = GameServer(localaddr=('localhost', 1337))
start = time.time()
while True:
    gameserver.Pump()
    time.sleep(0.0001)
    # run your code
    end = time.time()   
    elapsed = end - start
    if elapsed > 3:
        start = time.time()
        print(f"Server working {time.strftime('%a, %d %b %Y %X +0000', time.gmtime())}")