# Duplicate job ID detection

* Demo link -> click [here](https://youtu.be/cOa33jc0is8)

## setup
* make sure the `jobpostings.csv` is inside the `data` folder

* make sure you have `docker` installed.

* open a terminal on this folder and run `docker compose up -d`


## information regarding submission:

- I am using all-MiniLM-L6-v2 sentence transformer model

- Model Selection:
For generating embeddings from job descriptions, Sentence Transformers would be an optimal choice. This model framework is specifically designed for creating sentence-level embeddings and is fine-tuned on a range of NLP tasks, making it highly effective for semantic similarity tasks.

    Advantages:

    * High Semantic Accuracy: Sentence Transformers are trained on natural language inference data, which helps them capture semantic meaning effectively, crucial for detecting duplicates that may not be exact but convey the same meaning.
    * Speed and Scalability: These models are optimized for performance, allowing fast computation of embeddings even on large datasets.

- Choosing the Distance Metric
    * Euclidean Distance (L2): Measures the straight line distance between two points in Euclidean space. It's widely used when the magnitude of vectors is meaningful.
    * Cosine Similarity: Measures the cosine of the angle between two vectors, providing a value between -1 and 1. A value of 1 means the vectors are identical, 0 means orthogonal, and -1 indicates completely opposite. It’s particularly effective in text analysis because it focuses on the orientation rather than the magnitude of vectors.

- Setting the Threshold
    * With Cosine Similarity: A common threshold chosen is 0.9, suggesting that two job descriptions are considered duplicates if their cosine similarity score is 0.9 or above, indicating very high similarity.
    * With Euclidean Distance: Lower scores indicate closer proximity. A distance of 0.1 or lower would indicate duplicates.

- other use-cases
    * grouping similar job ids together: We can reduce the threshold and group the job descriptions together which are similar. This way, for example, we can get all job descriptions related to machine learning together
    * findind other job roles: If we find a job description on the web that we are interested in and put it in this application, it can also show us more similar job descriptions that can help in the job search.

- Handling realtime-data - as soon as we get more job postings, we can develop a pipeline to find similar job descriptions and add the new job description to the cluster as well. We can also add it to the pymilvus collection for future use.


## Next steps:

- use model `all-mpnet-base-v2`.
- use filtering to get better results.
- perform data cleaning on the job descriptions.
- Due to time constraints, I was able to insert 16000/21000 groups into the collection (Each dataframe is grouped by Company Name, City, State, Zipcode, Website Url). Next step would be to train all groups
- Due to time constraints, I could only cluster for the first 100K job ids. Next step would be to cluster the remaining ids.



## Interesting fact:
- I was able to find 72k clusters from the first 100k results. Meaning I could find around 25k duplicate job ids just by looking at the first 100k jobs.