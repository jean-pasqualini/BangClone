import time
import json
from PodSixNet.Channel import Channel
from PodSixNet.Server import Server
from data.player import Player
from data.card import Card
from data.tools import get_filename


class ClientChannel(Channel):
    """Create the channel to deal with incoming requests from the client.
    A new channel is created every time a client connects.
    """
    def Network(self, data):
        print(data)

    def Network_card(self, data):
        print(f"card: {data['card']}")

    def Network_deck(self, data):
        """Update self.deck"""
        deck = json.loads(data["cards"])
        server_deck = []
        for path in deck:
            server_deck.append(Card(path))
        self._server.deck = server_deck
        self._server.print_cards()


class GameServer(Server):
    """Receive and send data to players"""
    # Set the channel to deal with incoming requests
    # TODO: find out how this works
    channelClass = ClientChannel 

    def __init__(self, *args, **kwargs):
        Server.__init__(self, *args, **kwargs)
        self.start = time.time()
        print('Server launched')
        self.deck = []
        self.discard = []

    def Connected(self, channel, addr):
        """This method will be called whenever 
        a new client connects to the server.
        """
        print(f"somebody connected: {addr}, {channel}")
        channel.Send({"action": "hello", "message": "hello client!"})

    def print_status(self, gap):
        """Outup current time each N seconds (N==gap)"""
        end = time.time()
        elapsed = end - self.start
        if elapsed > gap:
            self.start = time.time()
            print(f"Server working {time.strftime('%a, %d %b %Y %X +0000', time.gmtime())}")

    def print_cards(self):
        print(len(self.deck))

if __name__ == "__main__":
    gameserver = GameServer(localaddr=('0.0.0.0', 1337))
    while True:
        gameserver.Pump()
        gameserver.print_status(3)
        time.sleep(0.0001)
        