from .BaseDataModel import BaseDataModel
from .db_schemas import Project
from .enums.DatabaseEnum import DatabaseEnum

class ProjectModel(BaseDataModel):
    
    def __init__(self, db_client: object):
        super().__init__(db_client=db_client)
        self.collection = self.db_client[DatabaseEnum.COLLECTION_PROJECT_NAME.value]
        
        
    # we build this function, because __init__ cannot be async, and we need to create the collection and indices if they don't exist
    # so this call init as normal and init_collection as async.
    @classmethod
    async def create_instance(cls, db_client: object):
        instance = cls(db_client=db_client)
        await instance.init_collection()
        return instance

    async def init_collection(self):
        all_collections = await self.db_client.list_collection_names()
        if DatabaseEnum.COLLECTION_PROJECT_NAME.value not in all_collections:
            self.collection = await self.db_client.create_collection(DatabaseEnum.COLLECTION_PROJECT_NAME.value)
            indices = Project.get_indices()
            
            for index in indices:
                await self.collection.create_index(index["key"], 
                                                   name=index["name"], 
                                                   unique=index["unique"])
        
    async def create_project(self, project: Project):
        result = await self.collection.insert_one(project.dict(by_alias=True, exclude_unset=True)) #insert one : need dictionary format
        project._id = result.inserted_id
        
        return project
    
    async def get_project_or_create(self, project_id: str):
        record = await self.collection.find_one({"project_id": project_id}) # find one: return dictionary format
        if record is None:
            project = Project(project_id=project_id)
            project = await self.create_project(project)
            
            return project
        
        return Project(**record) # return Project object NOT dictionary format
    
    # always use pageination with get all
    async def get_all_projects(self, page: int=1, page_size: int=10):
        
        # count total number of documents in the collection
        total_documents = await self.collection.count_documents({})
        
        # calculate total number of pages
        total_pages = (total_documents + page_size - 1) // page_size
        
        pointer = self.collection.find().skip((page - 1) * page_size).limit(page_size).to_list(length=None)
        projects = []
        
        async for document in pointer:
            projects.append(Project(**document))
        
        return projects, total_pages