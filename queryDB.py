#imports
from pinecone.grpc import PineconeGRPC as Pinecone

from dotenv import load_dotenv
import os



load_dotenv() #import environment variables 



def query_db_outreach(top_n, query):

    #initialize pinecone client
    PINECONE_API_KEY = os.getenv('PINECONE_API_KEY')
    pc = Pinecone(api_key=PINECONE_API_KEY)

    #target index
    index = pc.Index(host=os.getenv('PINECONE_HOST'))

    #convert query into embedding
    query_embedding = pc.inference.embed(
        model="llama-text-embed-v2",
        inputs=[query],
        parameters={
            "input_type": "query"
        }
    )
    
    
    #search index for top_n most similar vectors
    results = index.query(
        namespace="example-namespace",
        vector=query_embedding[0].values,
        top_k=top_n,
        include_values=False,
        include_metadata=True,
        # filter=(
        #     {"messaged": False}
        # )
    )

    
    #mark each result as messaged
    # for result in results.get("matches", []):
    #     index.update(id=result.get("metadata", {})["id"], set_metadata={"messaged" : True}, namespace="example-namespace")


    #reformat results
    company_data = [
        {
            "id": match["id"],
            "name": match["metadata"].get("company_name", ""),
            "overview": match["metadata"].get("overview", ""),
            "industry": match["metadata"].get("industry", ""),
            "size": match["metadata"].get("employees", ""),
            "followers": match["metadata"].get("followers", ""),
            "location": match["metadata"].get("location", ""),
            "logo_url": match["metadata"].get("logo_url", "")
        }
        for match in results.get("matches", [])
    ]

    return company_data





