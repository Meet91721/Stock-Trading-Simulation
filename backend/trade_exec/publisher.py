from backend.config.activemq_config import *
import stomp

user = ACTIVEMQ_USER
password = ACTIVEMQ_PASSWORD
host = ACTIVEMQ_HOST
port = ACTIVEMQ_PORT
destination = ACTIVEMQ_DESTINATION

def sendMessage(dbid, message):
	conn = stomp.Connection(host_and_ports = [(host, port)])
	conn.connect(login=user,passcode=password)
	conn.send(body=message, destination=f"/queue/{dbid}", persistent='false')
	conn.disconnect()
