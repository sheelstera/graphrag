import os

from langchain_community.document_loaders import TextLoader, JSONLoader
from langchain_community.embeddings import OpenAIEmbeddings
from langchain_community.vectorstores import Neo4jVector
from langchain_neo4j import Neo4jGraph
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_openai import ChatOpenAI
from langchain_experimental.graph_transformers import LLMGraphTransformer

jq_schema = """
[
  .[] | {
    customer_id: .Customer.customer_id,
    name: .Customer.name,
    email: .Customer.email,
    phone: .Customer.phone,
    age: .Customer.age,
    gender: .Customer.gender,
    location: (.Customer.city + ", " + .Customer.country),
    income: .Customer.income,
    segment: .Customer.segment,
    personality: .Customer.personality,
    demographics: .Demographics,
    psychographics: .Psychographics,
    social_media: .SocialMedia
  }
]
"""

graph = Neo4jGraph(
    url='bolt://localhost:7687',
    username='neo4j',
    password='password',
)
loader = JSONLoader(
    file_path="/path/to/your/file.json",
    jq_schema=jq_schema,
    text_content=False
)
docs = loader.load()

text_splitter = RecursiveCharacterTextSplitter(chunk_size=500, chunk_overlap=100)
documents = text_splitter.split_documents(documents=docs)
llm=ChatOpenAI()
llm_transformer = LLMGraphTransformer(llm=llm)

graph_documents = llm_transformer.convert_to_graph_documents(documents)

print(graph_documents[0])

graph.add_graph_documents(
    graph_documents,
    baseEntityLabel=True,
    include_source=True
)



