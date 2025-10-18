import streamlit as st


 # Streamlit reruns your script from top
 # to bottom every time you interact with your app.
 #
 # Session State is a way to share variables between reruns, for each user session.
 #
 # In addition to the ability to store and persist state, Streamlit also
 # exposes the ability to manipulate state using Callbacks.
 #
 # Session state also persists across pages inside a multipage app.
 # - Docs [https://docs.streamlit.io/develop/concepts/architecture/session-state]

 # tangina bawal magmulti-line comment kasi nadidisplay sya sa app
st.title('Counter')
count =  0

# if 'key' not in st.session_state:
#     st.session_state.key = 'value'
#
# # Read the value from session state
# output = st.session_state.key
# st.write(output)

increment = st.button('Increment')
# if nde present sa st.session_state then gawa new
if 'count' not in st.session_state:
    st.session_state.count = 0

if increment:
    st.session_state.count += 1

st.write('Count = ', st.session_state.count)

