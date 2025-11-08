# Mongodb configuration here
# Some important links
# https://www.mongodb.com/docs/languages/python/pymongo-driver/current/get-started/
# https://docs.streamlit.io/develop/tutorials/databases/mongodb

# Basic Mongodb config with streamlit
# https://docs.streamlit.io/develop/tutorials/databases/mongodb
import streamlit as st
import pymongo

@st.cache_resource
def init_connection():
    return pymongo.MongoClient(st.secrets["mongo"])


client = init_connection()

# Pull data from the collection.
# Uses st.cache_data to only rerun when the query changes or after 10 min.
@st.cache_data(ttl=600)
def get_data():
    db = client.sample_mflix

    # You need to specify which collection to query
    items = db.movies.find().limit(10)
    return list(items)


items = get_data()

# Display the data
st.write(f"Found {len(items)} documents")
for item in items:
    st.write(f"Movie: {item.get('title', 'No title')}")