from PodSixNet.Channel import Channel
from PodSixNet.Server import Server
import time


class ClientChannel(Channel):
    """Create the channel to deal with incoming requests from the client.
    A new channel is created every time a client connects.
    """
    def Network(self, data):
        print(data)

    def Network_card(self, data):
        print(f"card: {data['card']}")

class GameServer(Server):
    """Receive and send data to players"""
    # Set the channel to deal with incoming requests
    # TODO: find out how this works
    channelClass = ClientChannel 

    def __init__(self, *args, **kwargs):
        Server.__init__(self, *args, **kwargs)
        self.start = time.time()
        print('Server launched')

    def print_status(self, gap):
        """Outup current time each N seconds (N==gap)"""
        end = time.time()
        elapsed = end - self.start
        if elapsed > gap:
            self.start = time.time()
            print(f"Server working {time.strftime('%a, %d %b %Y %X +0000', time.gmtime())}")

    def Connected(self, channel, addr):
        """This method will be called whenever 
        a new client connects to the server.
        """
        print(f"somebody connected: {addr}, {channel}")
        channel.Send({"action": "hello", "message": "hello client!"})

if __name__ == "__main__":
    gameserver = GameServer(localaddr=('localhost', 1337))
    while True:
        gameserver.Pump()
        gameserver.print_status(3)
        time.sleep(0.0001)
        