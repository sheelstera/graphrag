from langchain_community.vectorstores.neo4j_vector import remove_lucene_chars
import os

from langchain_community.document_loaders import TextLoader
from langchain_community.embeddings import OpenAIEmbeddings
from langchain_community.vectorstores import Neo4jVector
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import RunnablePassthrough
from langchain_neo4j import Neo4jGraph
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_openai import ChatOpenAI
from langchain_experimental.graph_transformers import LLMGraphTransformer
from neo4j import GraphDatabase
from pydantic import BaseModel, Field

driver = GraphDatabase.driver(
    uri = "bolt://localhost:7687",
    auth = ("neo4j",
            "password"))

def create_fulltext_index(tx):
    query = '''
    CREATE FULLTEXT INDEX `fulltext_entity_id` 
    FOR (n:__Entity__) 
    ON EACH [n.id];
    '''
    tx.run(query)

def create_index():
    with driver.session() as session:
        session.execute_write(create_fulltext_index)
        print("Fulltext index created successfully.")

try:
    create_index()
except:
    pass

driver.close()




vector_index = Neo4jVector.from_existing_graph(
    OpenAIEmbeddings(),
    search_type="hybrid",
    node_label="Document",
    text_node_properties=["text"],
    embedding_node_property="embedding",
    url='bolt://localhost:7687',
    username='neo4j',
    password='Abcd1234'
)


vector_retriever = vector_index.as_retriever()
graph = Neo4jGraph(
    url='bolt://localhost:7687',
    username='neo4j',
    password='password',
)
class Entities(BaseModel):

    names: list[str] = Field(
        ...,
        description="All the person, organization, or business entities that appear in the text",
    )

prompt = ChatPromptTemplate.from_messages(
    [
        (
            "system",
            "You are extracting organization and person entities from the text.",
        ),
        (
            "human",
            "Use the given format to extract information from the following "
            "input: {question}",
        ),
    ]
)

llm=ChatOpenAI()
entity_chain = llm.with_structured_output(Entities)

def graph_retriever(question: str) -> str:
    """
    Collects the neighborhood of entities mentioned
    in the question
    """
    result = ""
    entities = entity_chain.invoke(question)
    for entity in entities.names:
        response = graph.query(
            """CALL db.index.fulltext.queryNodes('fulltext_entity_id', $query, {limit:2})
            YIELD node,score
            CALL {
              WITH node
              MATCH (node)-[r:!MENTIONS]->(neighbor)
              RETURN node.id + ' - ' + type(r) + ' -> ' + neighbor.id AS output
              UNION ALL
              WITH node
              MATCH (node)<-[r:!MENTIONS]-(neighbor)
              RETURN neighbor.id + ' - ' + type(r) + ' -> ' +  node.id AS output
            }
            RETURN output LIMIT 50
            """,
            {"query": entity},
        )
        result += "\n".join([el['output'] for el in response])
    return result

def full_retriever(question: str):
    graph_data = graph_retriever(question)
    vector_data = [el.page_content for el in vector_retriever.invoke(question)]
    final_data = f"""Graph data:
{graph_data}
vector data:
{"#Document ". join(vector_data)}
    """
    return final_data


template = """Answer the question based only on the following context:
{context}

Question: {question}
Use natural language and be concise.
Answer:"""
prompt = ChatPromptTemplate.from_template(template)

chain = (
        {
            "context": full_retriever,
            "question": RunnablePassthrough(),
        }
        | prompt
        | llm
        | StrOutputParser()
)
response=chain.invoke(input="Are there any customers who have the same personality?")
print(response)
