from PodSixNet.Channel import Channel
from PodSixNet.Server import Server
from time import sleep


class ClientChannel(Channel):
	"""Server-representation-of-a-client.
	Each time a client connects, a new Channel based class will be created.
	"""
    def Network(self, data):
    	"""Whenever the client does connection.Send(mydata), 
    	this method will be called.
    	"""
        print(data)

    # will only be called if your data has a key called ‘action’, 
    # with a value of “Network_%methodname%”
    def Network_update_player(self, data):
        print(f"update_player: {data}")

    def Network_update_table(self, data):
        print(f"update_table: {data}")

class GameServer(Server):

    channelClass = ClientChannel

    def Connected(self, channel, addr):
    	"""This method will be called whenever 
    	a new client connects to the server.
    	"""
        print(f"new connection: {channel}")

gameserver = GameServer()
while True:
    gameserver.Pump()
    sleep(0.0001)