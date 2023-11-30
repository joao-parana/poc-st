import threading
import time
from collections.abc import Callable

import streamlit as st
from streamlit.runtime.scriptrunner import add_script_run_ctx

if "last_progress" not in st.session_state.keys():
    st.session_state["last_progress"] = 0


def setup_tasks(funcs: list[Callable]):
    threads = [threading.Thread(target=func) for func in funcs]
    for thread in threads:
        add_script_run_ctx(thread)
        thread.start()

    for thread in threads:
        thread.join()


st.title("Download from external source")
msg = """
    Obtaining datasets from external source can be a time-consuming task.
    For such, you can use this function to download in the background while
    works on other important things.
    """
st.write(msg)

available_datasets = ["other_dataset", "x1_dataset", "x2_dataset", "x3_dataset"]


def other_code():
    with st.expander("Management"):
        tab1, tab2 = st.tabs(["**Delete dataset**", "**Others functions**"])
        # "**Remove dataset**"
        with tab1:
            with st.form("data_exclusion"):
                dataset_name = st.selectbox(
                    label="Dataset name",
                    options=available_datasets,
                    key="dataset_alias_to_delete",
                )

                submitted = st.form_submit_button(label="Delete")

                if submitted:
                    print("delete", dataset_name, "last_progress =", st.session_state["last_progress"])
                else:
                    pass
                    # st.warning("Selecione um dataset para excluir!")

        with tab2:
            st.write("Some code here")


setup_tasks([other_code])

# Code to get the data
with st.status("Downloading data...", expanded=True) as status:
    st.success("Contacting the server...")
    while True:
        i = st.session_state["last_progress"]
        time.sleep(0.125)
        pb_value = min(i + 1, 100)
        if i > 99:
            print("break while loop")
            break
        i += 1
        if i % 10 == 0:
            print("i =", i)
        st.session_state["last_progress"] = i
    st.success("Download complete!")
    status.update(label="Download complete!", state="complete", expanded=False)


def clear_session_state():
    st.session_state["last_progress"] = 0


st.button("Rerun", on_click=clear_session_state)

print("tasks finished")
