from gmqtt import Client as MQTTClient

import uuid
import asyncio


class MQTTChannel:
	def __init__(self):
		self.username = None
		self.password = None

		self.host = 'lse.dev.br'
		self.port = 1883

		self.client = MQTTClient(uuid.uuid4().hex)
		self.client.on_connect = self.on_connect
		self.client.on_message = self.on_message
		self.client.on_disconnect = self.on_disconnect
		self.client.on_subscribe = self.on_subscribe

		self.publish_topic = 'scgdi/publish'
		self.subscribe_topic = 'scgdi/subscribe'

	def on_connect(self, client, flags, rc, properties):
		self.client.subscribe(self.subscribe_topic)
		print(f'connected with success in: {self.host} result code: {rc} ')

	def on_message(self, client, topic, payload, qos, properties):
		pass
		# print(f'received message: {payload} from topic: {topic}')

	def on_disconnect(self, client, packet, exc=None):
		pass

	def on_subscribe(self, client, mid, qos, properties):
		print('subscribed on topic: ', self.subscribe_topic)

	async def task_send_data(self):
		count = 0
		while True:
			self.client.publish(self.publish_topic, count)
			count += 1
			await asyncio.sleep(1)

	async def init(self):
		if self.username is not None and self.password is not None:
			self.client.set_auth_credentials(self.username, self.password)

		await self.client.connect(self.host, self.port)


async def main():
	channel = MQTTChannel()
	await channel.init()

	asyncio.create_task(channel.task_send_data())

	await asyncio.Event().wait()


if __name__ == '__main__':
	asyncio.run(main())
