from asyncua.server.history import HistoryStorageInterface
from asyncua.ua import NodeId, DataValue


class HistoryMongoDB(HistoryStorageInterface):
	def __init__(self, max_history_data_response_size=10000):
		super().__init__(max_history_data_response_size)

	@staticmethod
	def datavalue_to_dict(datavalue: DataValue):
		return {
			'variant': datavalue.Value.VariantType,
			'timestamp': datavalue.SourceTimestamp,
			'value': datavalue.Value,
			'server_timestamp': datavalue.ServerTimestamp
		}

	async def init(self):
		pass

	async def new_historized_node(self, node_id, period, count=0):
		print(f"Creating new historized node: {node_id}, period: {period}, count: {count}")
		# return await super().new_historized_node(node_id, period, count)

	async def save_node_value(self, node_id: NodeId, datavalue: DataValue):
		print(f"Saving node value: {node_id}, datavalue: {datavalue}")
		# return await super().save_node_value(node_id, datavalue)

	async def read_node_history(self, node_id, start, end, nb_values):
		pass
		# print(f"Reading node history: {node_id}, start: {start}, end: {end}, nb_values: {nb_values}")
		# return await super().read_node_history(node_id, start, end, nb_values)
