import asyncio
import pymongo


async def main():
	client = pymongo.AsyncMongoClient(
		host='0.0.0.0',
		port=27017,
		username='shell-manager-user',
		password='743bce6144f65c117b7673bc6787db01',
	)

	db = client['scgdi']
	alunos = db['alunos']

	# buscar todos os alunos
	cursor = alunos.find(
		{"$and": [{"idade": {"$gte": 18}}, {"idade": {"$lte": 22}}]}
		# {
		# 	"curso": "Ciência da Computação", 
		# 	"idade": {"$lte": 20}
		# }
	)

	async for aluno in cursor:
		print(aluno)



if __name__ == '__main__':
	asyncio.run(main())
