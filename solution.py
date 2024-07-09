import pandas as pd
from sentence_transformers import SentenceTransformer
from pymilvus import Milvus,connections, FieldSchema, CollectionSchema, DataType, Collection, utility

df = pd.read_csv('./data/jobpostings.csv')

for col in df.select_dtypes(include=[object]):
    df[col] = df[col].str.lower()

fmt = "\n=== {:30} ===\n"
print(fmt.format("start connecting to Milvus"))
connections.connect("default", host="milvus-standalone", port="19530")
milvus_client = Milvus("milvus-standalone","19530")

# Define the schema of the collection
fields = [
    FieldSchema(name="id", dtype=DataType.VARCHAR, is_primary=True, auto_id=False,max_length=255),
    FieldSchema(name="embedding", dtype=DataType.FLOAT_VECTOR, dim=384)
]

schema = CollectionSchema(fields, description="Job Descriptions")
collection_name = "search_job_description_duplicate_id"

collection = Collection(name=collection_name, schema=schema, using='default', shards_num=2)
# Create an index for better search performance
collection.create_index(field_name="embedding", index_params={"index_type": "IVF_FLAT", "metric_type": "L2", "params": {"nlist": 100}})


grouped = df.groupby(['Company Name', 'City', 'State', 'Zipcode','Website Url'])
model = SentenceTransformer('all-MiniLM-L6-v2',force_download=True)

def insert_embeddings_with_tags(group,tags,ids):
    # Generate embeddings
    descriptions_to_embed=group['Job Description'].tolist()
    descriptions_to_embed=[str(element) for element in descriptions_to_embed]
    embeddings = model.encode(descriptions_to_embed,show_progress_bar=True)
    entities = [ids,embeddings]
    mr = collection.insert(entities, partition_name=None, tags=tags)
    milvus_client.flush([collection_name])
    return mr.primary_keys

# Iterate over groups and insert embeddings
count=0
ids_in_milvus = {}
for name, group in grouped:
    ids = group['Job Id'].tolist()
    count+=1
    print(count)
    str_list=[str(element) for element in name]
    tags='_'.join(str_list)
    ids_in_milvus[tags]=insert_embeddings_with_tags(group,tags,ids)

# assign cluster values
df['cluster']=-1

# find clusters
def find_similar_jobs_within_group(embedding, group_tag, threshold=0.9):
    search_params = {"metric_type": "L2", "params": {"nprobe": 10}}
    results = collection.search(
        data=embedding,
        anns_field="embedding",
        param=search_params,
        limit=10
    )
    similar_jobs = []
    for result in results[0]:
        if result.distance < (1 - threshold):
            similar_jobs.append(result.id)
    return similar_jobs


collection.load()
similar={}
for index, row in df.iterrows():
    if(row['cluster']==-1):
        df.loc[df['Job Id'] == row['Job Id'], 'cluster'] = index
        sample_embedding = model.encode([str(row['Job Description'])])
        group_tag = '_'.join([str(row['Company Name']),str(row['City']),str(row['State']),str(row['Zipcode']),str(row['Website Url'])])
        similar_ids = find_similar_jobs_within_group(sample_embedding, group_tag)
        for id in similar_ids:
            df.loc[df['Job Id'] == id, 'cluster'] = index
        similar[row['Job Id']]=similar_ids


final_cluster = df.groupby('cluster')
job_ids_by_cluster = final_cluster['Job Id'].agg(list).reset_index()

job_ids_by_cluster.to_csv('job_ids_by_cluster.csv', index=False)