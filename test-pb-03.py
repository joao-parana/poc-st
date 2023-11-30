import io
import sys
import threading
import time
from collections.abc import Callable
from datetime import datetime
from datetime import time as dt_time

import pandas as pd
import streamlit as st
from streamlit.runtime.scriptrunner import add_script_run_ctx

if "last_progress" not in st.session_state.keys():
    st.session_state["last_progress"] = 0

if "task_started" not in st.session_state.keys():
    st.session_state["task_started"] = False


def download_large_file():
    print("download_large_file() status")
    progress = st.progress(st.session_state["last_progress"])
    while True:
        i = st.session_state["last_progress"]
        time.sleep(1)
        pb_value = min(i + 1, 100)
        progress.progress(pb_value)
        if i > 99:
            print("break while loop")
            break
        i += 1
        if i % 10 == 0:
            print("i =", i)
        st.session_state["last_progress"] = i
    st.success("Download complete!")


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


# if not st.session_state["task_started"]:
setup_tasks([other_code])
# if not st.session_state["task_started"]:
st.session_state["task_started"] = True
setup_tasks([download_large_file])
print("tasks finished")


# ------------------------------------------------------------------------------------


def df_info_as_string(df: pd.DataFrame) -> str:
    buffer = io.StringIO()
    sys.stdout = buffer
    df.info()
    sys.stdout = sys.__stdout__
    return buffer.getvalue()


def datetime_input(
    label: str,
    key_prefix: str,
    value: datetime | None = None,
    min_value: datetime | None = None,
    max_value: datetime | None = None,
) -> datetime:
    col1, col2 = st.columns(2, gap="small")
    with col1:
        date_value = st.date_input(
            label=label,
            value=value or datetime.date.today(),
            key=f"{key_prefix}_date",
            min_value=min_value,
            max_value=max_value or datetime.date.today(),
        )
    with col2:
        time_value = st.time_input(label=" ", value=dt_time(0, 0), key=f"{key_prefix}_time")
    return datetime.combine(date_value, time_value)
