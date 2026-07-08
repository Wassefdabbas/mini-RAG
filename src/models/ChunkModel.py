from .BaseDataModel import BaseDataModel
from .db_schemas import DataChunk
from .enums.DatabaseEnum import DatabaseEnum
from bson.objectid import ObjectId
from pymongo import InsertOne

class ChunkModel(BaseDataModel):
    
    def __init__(self, db_client: object):
        super().__init__(db_client=db_client)
        
        self.collection = self.db_client[DatabaseEnum.COLLECTION_CHUNK_NAME.value]
        
    # do not inster chunk one by one in database, this is too slow, and bad for database
    # we need to use 'Batch Insert' to insert multiple chunks at once, this is much faster and better for database
    async def create_chunk(self, chunk: DataChunk):
        result = await self.collection.insert_one(chunk.dict(by_alias=True, exclude_unset=True)) #insert one : need dictionary format
        chunk._id = result.inserted_id
        
        return chunk
    
    async def get_chunk(self, chunk_id: str):
        result = await self.collection.find_one({"_id": ObjectId(chunk_id)}) # id in database must be ObjectId type, so we need to convert the string to ObjectId
        
        if result is None:
            return None
        
        return DataChunk(**result) # return DataChunk object NOT dictionary format
    
    async def insert_many_chunks(self, chunks: list[DataChunk], batch_size: int = 500):
        
        for i in range(0, len(chunks), batch_size):
            batch = chunks[i:i + batch_size]
        
            operations = [InsertOne(chunk.dict(by_alias=True, exclude_unset=True)) for chunk in chunks]
            await self.collection.bulk_write(operations)
        
        return len(chunks)
    
    async def delete_chunks_by_project_id(self, project_id: str):
        result = await self.collection.delete_many({"chunk_project_id": ObjectId(project_id)})
        
        return result.deleted_count