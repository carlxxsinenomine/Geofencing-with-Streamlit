[Link for the demo](https://carlxxsinenomine.streamlit.app/)


So change of plans, since Streamlit is not yet capable of handling real-time data streams and Python Streamlit and JavaScript direct communication isn't possible.
Instead of doing the Geofencing Alert algorithm in Python, we'll instead just store the Drawn shape into a database,
and retrieve the data from the database using JavaScript and use it to manipulate geometry type objects for the Geofencing Alert algorithm.
