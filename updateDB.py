# imports
import os
import json
import asyncio
from math import ceil

from scrape import run_scraper_api

from pinecone.grpc import PineconeGRPC as Pinecone
from pinecone import ServerlessSpec

from apscheduler.schedulers.asyncio import AsyncIOScheduler

from dotenv import load_dotenv
import google.generativeai as genai

from datetime import datetime

import csv

from pymongo.mongo_client import MongoClient 
from pymongo.server_api import ServerApi



load_dotenv()  # Load environment variables



#setup
uri = "mongodb+srv://knowmayus:guest666wasrealguys@cluster0.octhd90.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0"
client = MongoClient(uri, server_api=ServerApi('1'))
genai.configure(api_key="AIzaSyC_SZPN-cpkm4e1KoIRlVcRLhgbrQv7s18")
#we can worry about the open api keys later.
try:
    client.admin.command('ping')
    print("Pinged your deployment. You successfully connected to MongoDB!")
except Exception as e:
    print(e)

db = client.flask_db
users = db.users
companies = db.companies
optimal_companies = db.optimal_companies



#Vincent's Functions (we would automate the storing new posts and checking w the RAG, except linkedin sucks so were manually doing it)
def store_elements_from_key(data):
    """
    Iterates through the hashmap (data) and stores all elements in the specified key to the MongoDB database.
    Each element is inserted as a separate document in the 'users' collection.
    Arguments:
        data: dict — the input hashmap
        key: str — the key whose elements should be stored
    """
    for key, elements in data.items():
        if isinstance(elements, list):
            companies.update_one(
                {"name": key},
                {"$push": {"element": {"$each": elements}}},
                upsert=True
            )


# bogos_data = {
#     "Company EWQ": ["Element 1", "Element 2", "Element 3"],
#     "Company BEQW": ["Element 4", "Element 5"],
#     "Company EWQC": ["Element 6"]
# }
# store_elements_from_key(bogos_data)


def store_post(company, post):
    companies.update_one(
        {"name": company},
        {"$push": {"element": post}},
        upsert=True
    )


# store_post("ExampleCompany", "This is a sample post for the company.")
# store_post("ExampleCompany", "This is another sample post for the company.")

# store_post("ExampleCompany", "This is another sample post for the company.")


#mongo db functions
def check_if_exists(company, post):
    """
    Checks if a post exists for a given company in the companies collection.
    If not, uses the generative model to analyze the post.
    """
    for item in companies.find({"name": company}):
        if post in item.get("element", []):
            return True
    # doesn't exist yet thus
    #a new post

    store_post(company, post)
    model = genai.GenerativeModel("gemini-2.5-flash")
    response = model.generate_content(
          "You are to answer only \"Yes\" or \"No\". Respond with only these one word options. Does this post indicate the company is more open to outreach (e.g. more funding, new plans, etc.)?" + str(post)
    )
    print(response.text)

    if response.text== "Yes":
        optimal_companies.update_one(
            {"name": company},
            {"$set": {"willing_to_outreach": True}},
            upsert=True
        )
    else:
        optimal_companies.update_one(
            {"name": company},
            {"$set": {"willing_to_outreach": False}},
            upsert=True
        )

    return False

#print(check_if_exists("Amazon", "Get ready for Prime Day 2025 coming July 8–11, plus Amazon's record-setting investment in Australia's AI future, and more"))

#vector db functions
async def fetch_user_info(top_n):
    email = ""
    password = ""

    try:
        with open("companies.json", "r", encoding="utf-8") as file:
            companies = json.load(file)
    except Exception as e:
        return []

    data = []
    n = 0

    for company in companies:
        try:
            # data.append(run_scraper_api(company, email, password))

            with open('Untitled spreadsheet - Sheet1.csv', newline='') as csvfile:
                reader = csv.reader(csvfile)
                for row in reader:
                    data.append({
                        "company": row["company_name"],
                        "profile": {
                            "company_name": row["company_name"],
                            "logo_url": row["logo_url"],
                            "industry": row["industry"],
                            "location": row["location"],
                            "followers": row["followers"],
                            "employees": row["employees"],
                        },
                        "overview": row['overview'],
                    })

            n += 1

            if n >= top_n:
                break

        except Exception as e:
            continue

    return data


async def update_db(top_n):
    data = await fetch_user_info(top_n)
    if not data:
        return

    batch_size = 100
    total_batches = ceil(len(data) / batch_size)

    try:
        PINECONE_API_KEY = os.getenv('PINECONE_API_KEY')
        pc = Pinecone(api_key=PINECONE_API_KEY)
    except Exception as e:
        return

    embeddings = []
    for i in range(total_batches):
        batch = data[i * batch_size : (i + 1) * batch_size]
        try:
            batch_data = [d["overview"] for d in batch]
            batch_embeddings = pc.inference.embed(
                model="llama-text-embed-v2",
                inputs=batch_data,
                parameters={
                    "input_type": "passage",
                    "truncate": "END"
                }
            )
            embeddings.extend(batch_embeddings)
        except Exception as e:
            continue

    try:
        records = []
        for d, e in zip(data, embeddings):
            records.append({
                "id": d["company"],
                "values": e["values"],
                "metadata": {
                    "company_name": d['profile']['company_name'],
                    "logo_url": d['profile']['logo_url'],
                    "industry": d['profile']['industry'],
                    "location": d['profile']['location'],
                    "followers": d['profile']['followers'],
                    "employees": d['profile']['employees'],
                    "overview": d["overview"],
                    "messaged": False
                }
            })
    except Exception as e:
        return

    try:
        index = pc.Index(host=os.getenv('PINECONE_HOST'))
        index.upsert(
            vectors=records,
            namespace="example-namespace"
        )
    except Exception as e:
        return


async def schedule():
    scheduler = AsyncIOScheduler()
    scheduler.add_job(update_db, 'interval', minutes=60, args=[1], next_run_time=datetime.now())
    scheduler.start()
    await asyncio.Event().wait()

# asyncio.run(schedule())










# #code used for csv:
# # imports
# import os
# import json
# import asyncio
# from math import ceil

# from scrape import run_scraper_api

# from pinecone.grpc import PineconeGRPC as Pinecone
# from pinecone import ServerlessSpec

# from apscheduler.schedulers.asyncio import AsyncIOScheduler

# from dotenv import load_dotenv
# import google.generativeai as genai

# from datetime import datetime

# import csv



# load_dotenv()  # Load environment variables



# async def fetch_user_info(top_n):
#     email = "kgutcce430@couldmail.com"
#     password = "6384u6q7"

#     try:
#         with open("companies.json", "r", encoding="utf-8") as file:
#             companies = json.load(file)
#     except Exception as e:
#         return []

#     data = []
#     n = 0

#     # for company in companies:
#     #     try:
#     #         # data.append(run_scraper_api(company, email, password))

#     with open('Untitled spreadsheet - Sheet1.csv', newline='', encoding='utf-8') as csvfile:
#         reader = csv.reader(csvfile)
#         for row in reader:

#             data.append({
#                 "company": row[1],
#                 "profile": {
#                     "company_name": row[1],
#                     "logo_url": row[6],
#                     "industry": row[4],
#                     "location": row[5],
#                     "followers": row[3],
#                     "employees": row[2],
#                 },
#                 "overview": row[7],
#             })

#     n += 1

#             # if n >= top_n:
#             #     break

#         # except Exception as e:
#         #     continue

#     return data


# async def update_db(top_n):
#     data = await fetch_user_info(top_n)
#     if not data:
#         return

#     batch_size = 100
#     total_batches = ceil(len(data) / batch_size)

#     try:
#         PINECONE_API_KEY = os.getenv('PINECONE_API_KEY')
#         pc = Pinecone(api_key=PINECONE_API_KEY)
#     except Exception as e:
#         return

#     embeddings = []
#     for i in range(total_batches):
#         batch = data[i * batch_size : (i + 1) * batch_size]
#         try:
#             batch_data = [d["overview"] for d in batch]
#             batch_embeddings = pc.inference.embed(
#                 model="llama-text-embed-v2",
#                 inputs=batch_data,
#                 parameters={
#                     "input_type": "passage",
#                     "truncate": "END"
#                 }
#             )
#             embeddings.extend(batch_embeddings)
#         except Exception as e:
#             continue
       
#     try:
#         records = []
#         for d, e in zip(data, embeddings):
#             records.append({
#                 "id": d["company"],
#                 "values": e["values"],
#                 "metadata": {
#                     "company_name": d['profile']['company_name'],
#                     "logo_url": d['profile']['logo_url'],
#                     "industry": d['profile']['industry'],
#                     "location": d['profile']['location'],
#                     "followers": d['profile']['followers'],
#                     "employees": d['profile']['employees'],
#                     "overview": d["overview"],
#                     "messaged": False
#                 }
#             })
#     except Exception as e:
#         return

#     try:
#         index = pc.Index(host=os.getenv('PINECONE_HOST'))
#         index.upsert(
#             vectors=records,
#             namespace="example-namespace"
#         )
#     except Exception as e:
#         return


# # async def schedule():
# #     scheduler = AsyncIOScheduler()
# #     scheduler.add_job(update_db, 'interval', minutes=60, args=[1], next_run_time=datetime.now())
# #     scheduler.start()
# #     await asyncio.Event().wait()

# asyncio.run(update_db(20))


