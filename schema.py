from enum import StrEnum
from pydantic import BaseModel, Field
from uuid import UUID, uuid4
from datetime import datetime
from typing import Literal

# Resource, ResourceKind, ContentBlock, BlockType, Import, CourseUserData
class ResourceKind(StrEnum):#all the file type that we are going to extracte the data from for ingestion 
    folder="folder"
    text = "text"
    pdf="pdf"
    pptx="pptx"
    docx="docx"
    markdown="markdown"
    video="video"
    webpage="webpage"

class BlockType(StrEnum):
    text="text" #extracted text from pdf, docx,pptx,.md
    transcript="transcript" | None  # speech to text transcript from video or audio
    summary="summary"
    structure="structure"  # folder level description

class ResourceStatus(StrEnum):
    active = "active"
    archived = "archived"  # prune = mark, never delete

class ImportStatus(StrEnum):
    running = "running"
    completed = "completed"
    completed_with_errors = "completed_with_errors"
    failed = "failed"

class Resource(BaseModel):
    id:UUID = Field(default_factory=uuid4)                             #every resource will have a unique id to track and work with, also help in working with dedublication, parent id refereal,recursive tree extraction and discovery
    parent_id:UUID | None  = None              # IF NONE means it is a root folder 
    kind:ResourceKind                   #what kind of file it is 
    title:str                           # what is the title originally given to the file
    path:str                            #reletive path to the folder like Aiml_system/introduction/why/why was the AIML so promising in the computer world.mp4
    modified_at:datetime | None  = None       #datetime when it was modified 
    source_uri:str                      #original url to file access 
    order_index:int | None    =None          #order index
    mime:str | None=None
    import_id: UUID # provenance: which ingest run produced this
    size_bytes: int | None=None
    status:ResourceStatus


class ContentBlock(BaseModel):
    id:UUID 
    resource_id:UUID
    type:BlockType
    content:str
    created_by:Literal["extractor","llm","user"]
    # created_at: datetime = Field(default_factory=datetime.now)
    started_at: datetime = Field(default_factory=datetime.now)


class Import(BaseModel):
    id:UUID = Field(default_factory=uuid4)
    params:dict[str,str | int] = Field(default_factory=dict) #parameters used for the import maxdepth, maxfilesize, etc
    started_at: datetime = Field(default_factory=datetime.now)
    finished_at: datetime | None = None   # None = still running
    input_raw:str
    source_id:str
    status:ImportStatus
    problems:list[str]=[]
    counts:dict[str,int] = Field(default_factory=dict) #counts of the resources and content blocks ingested


class CourseUserData(BaseModel):
    user_id :UUID
    course_id :UUID
    goal: str | None = None
    context: str | None = None
    level: str | None = None
