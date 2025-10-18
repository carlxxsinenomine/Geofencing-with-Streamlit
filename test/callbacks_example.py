import streamlit as st

st.title(' Counter Example using Callbacks')
if 'count' not in st.session_state:
    st.session_state.count = 0
# callback with kwargs
def increment_counter(increment_value=0):
    st.session_state.count += increment_value

def decrement_counter(decrement_value=0):
    st.session_state.count -= decrement_value

st.button('Increment', on_click=increment_counter, kwargs=dict(increment_value=5))
st.button('Decrement', on_click=decrement_counter, kwargs=dict(decrement_value=1))


# callback with args
# increment_value = st.number_input('Enter a value', value=0, step=1)
#
# increment = st.button('Increment', on_click=increment_counter, args=(increment_value, ))

# simple callback
# def increment_counter():
#     st.session_state.count += 1
#
# st.button('Increment', on_click=increment_counter)


st.write('Count = ', st.session_state.count)