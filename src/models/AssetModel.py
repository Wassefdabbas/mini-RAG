from .BaseDataModel import BaseDataModel
from .db_schemas import Asset
from .enums.DatabaseEnum import DatabaseEnum
from bson import ObjectId

class AssetModel(BaseDataModel):
    
    def __init__(self, db_client: object):
        super().__init__(db_client=db_client)
        self.collection = self.db_client[DatabaseEnum.COLLECTION_ASSET_NAME.value]
        
    # we build this function, because __init__ cannot be async, and we need to create the collection and indices if they don't exist
    # so this call init as normal and init_collection as async.
    @classmethod
    async def create_instance(cls, db_client: object):
        instance = cls(db_client=db_client)
        await instance.init_collection()
        return instance
    
    async def init_collection(self):
        all_collections = await self.db_client.list_collection_names()
        if DatabaseEnum.COLLECTION_ASSET_NAME.value not in all_collections:
            self.collection = await self.db_client.create_collection(DatabaseEnum.COLLECTION_ASSET_NAME.value)
            indices = Asset.get_indices()
            
            for index in indices:
                await self.collection.create_index(index["key"], 
                                                   name=index["name"], 
                                                   unique=index["unique"])
                
    
    async def create_asset(self, asset: Asset):
        result = await self.collection.insert_one(asset.dict(by_alias=True, exclude_unset=True)) #insert one : need dictionary format
        asset.id = result.inserted_id
        
        return asset
    
    async def get_all_project_assets(self, asset_project_id: str):
        return await self.collection.find({"asset_project_id": ObjectId(asset_project_id)}if isinstance(asset_project_id, str) else asset_project_id).to_list(length=None)