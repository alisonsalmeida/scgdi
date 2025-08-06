from typing import List, Tuple, Union
from asyncua.server.history import HistoryStorageInterface
from asyncua.ua import NodeId, DataValue, Variant, VariantType
from asyncua.server import Server
from datetime import timedelta, datetime

import pymongo


class HistoryMongoDB(HistoryStorageInterface):
	def __init__(self, server: Server, max_history_data_response_size=10000):
		self.connection = pymongo.AsyncMongoClient(
			host='0.0.0.0',
			port=27017,
			username='shell-manager-user',
			password='743bce6144f65c117b7673bc6787db01',
		)
		self.server = server
		super().__init__(max_history_data_response_size)

	async def get_parent_name(self, node_id: NodeId) -> str:
		node = self.server.get_node(node_id)
		node_name = (await node.read_browse_name()).Name

		parent = await node.get_parent()
		parent_name = (await parent.read_browse_name()).Name

		return f'{parent_name}_{node_name}'

	@staticmethod
	def datavalue_to_dict(datavalue: DataValue):
		return {
			'variant': datavalue.Value.VariantType,
			'timestamp': datavalue.SourceTimestamp,
			'value': datavalue.Value.Value,
			'server_timestamp': datavalue.ServerTimestamp
		}
	
	@staticmethod
	def datavalue_from_dict(data: dict) -> DataValue:
		variant = Variant(Value=data['value'], VariantType=VariantType(data['variant']))
		timestamp = data['timestamp']
		server_timestamp = data['server_timestamp']

		return DataValue(variant, SourceTimestamp=timestamp, ServerTimestamp=server_timestamp)

	async def init(self):
		pass

	async def new_historized_node(self, node_id: NodeId, period: timedelta, count=0):
		name_parente = await self.get_parent_name(node_id)

		await self.connection.condition_monitoring[name_parente].create_index(
			'server_timestamp', unique=True, name='server_timestamp_index'
		)

	async def save_node_value(self, node_id: NodeId, datavalue: DataValue):
		collection_name = await self.get_parent_name(node_id)

		db = self.connection.condition_monitoring
		await db[collection_name].insert_one(self.datavalue_to_dict(datavalue))

	async def read_node_history(self, node_id: NodeId, start: datetime, end: datetime, nb_values: int) -> Tuple[List[DataValue], Union[datetime | None]]:
		print('nb_values:', nb_values)
		
		db = self.connection.condition_monitoring
		collection_name = await self.get_parent_name(node_id)
		query = {"$and": [
			{"server_timestamp": {"$gte": start}},
			{"server_timestamp": {"$lte": end}}
		]}

		result = []
		count = await db[collection_name].count_documents(query)
		cursor = db[collection_name].find(query).sort('server_timestamp', pymongo.ASCENDING).limit(nb_values)
	    
		async for document in cursor:
			result.append(self.datavalue_from_dict(document))

		return result, result[-1].ServerTimestamp if count > nb_values else None
