from typing import List, Tuple, Union
from asyncua.server.history import HistoryStorageInterface
from asyncua.ua import NodeId, DataValue, Variant, VariantType, LocalizedText
from asyncua.server import Server
from asyncua.common.events import Event
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
		self.database_name = "condition_monitoring"
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
	
	@staticmethod
	def event_to_dict(event: Event) -> dict:
		"""
		<class 'asyncua.common.events.Event'>, Event(
		['Current:0.0', 
		'Temperature:0.0', "EventId:b'609f8b642f5e4d6f8dedb9d32b14539b'", 'EventType:NodeId(Identifier=15, NamespaceIndex=2, NodeIdType=<NodeIdType.FourByte: 1>)', 'SourceNode:NodeId(Identifier=2, NamespaceIndex=2, NodeIdType=<NodeIdType.FourByte: 1>)', 'SourceName:Submodel:ConditionMonitoring', 'Time:2025-08-07 14:40:28.430593+00:00', 'ReceiveTime:2025-08-07 14:40:28.430594+00:00', 'LocalTime:TimeZoneDataType(Offset=-240, DaylightSavingInOffset=True)', "Message:LocalizedText(Locale=None, Text='Contador passou de 10!')", 'Severity:990', 'ConditionClassId:None', 'ConditionClassName:None', 'ConditionSubClassId:None', 'ConditionSubClassName:None'])
		"""
		
		fields = {}
		fields_for_select = ['EventId', 'Time', 'ReceiveTime', 'Message', 'Severity']
		for field, value in event.get_event_props_as_fields_dict().items():
			if field in fields_for_select:
				if field == "Message":
					fields[field] = {"VariantType": value.VariantType, "Value": value.Value.Text}
					continue

				fields[field] = {"VariantType": value.VariantType, "Value": value.Value}

		return fields
	
	@staticmethod
	def event_from_dict(data: dict) -> Event:
		event = Event()
		for field, value in data.items():
			if field == '_id':
				continue

			if field == "Message":
				event.add_property(
					name=field,
					val=Variant(
						Value=LocalizedText(Text=value["Value"]),
						VariantType=VariantType(value["VariantType"])
					),
					datatype=None
				)
				continue

			event.add_property(
				name=field,
				val=Variant(
					Value=value["Value"],
					VariantType=VariantType(value["VariantType"])
				),
				datatype=None
			)

		return event
			

	async def init(self):
		pass

	async def stop(self):
		pass

	async def new_historized_node(self, node_id: NodeId, period: timedelta, count=0):
		name_parente = await self.get_parent_name(node_id)

		await self.connection[self.database_name][name_parente].create_index(
			'server_timestamp', unique=True, name='server_timestamp_index'
		)

	async def save_node_value(self, node_id: NodeId, datavalue: DataValue):
		collection_name = await self.get_parent_name(node_id)

		db = self.connection[self.database_name]
		await db[collection_name].insert_one(self.datavalue_to_dict(datavalue))

	async def read_node_history(self, node_id: NodeId, start: datetime, end: datetime, nb_values: int) -> Tuple[List[DataValue], Union[datetime | None]]:
		db = self.connection[self.database_name]
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
	
	async def new_historized_event(self, source_id, evtypes, period, count=0):
		print(f"new_historized_event: {source_id}, {evtypes}, {period}, {count}")
		# return await super().new_historized_event(source_id, evtypes, period, count)

	async def save_event(self, event: Event):
		event_dict = self.event_to_dict(event)
		db = self.connection[self.database_name]
		await db['events'].insert_one(event_dict)

	async def read_event_history(
			self, source_id: NodeId, start: datetime, end: datetime, nb_events: int, select_clauses) -> Tuple[List[Event], Union[datetime | None]]:

		db = self.connection[self.database_name]
		query = {"$and": [
			{"Time.Value": {"$gte": start}},
			{"Time.Value": {"$lte": end}}
		]}

		count = await db['events'].count_documents(query)
		cursor = db['events'].find(query).sort('Time.Value', pymongo.ASCENDING).limit(nb_events)
		events = []

		async for document in cursor:
			events.append(self.event_from_dict(document))

		return events, events[-1].Time.Value if count > nb_events else None
