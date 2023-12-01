import datetime
import threading
import time
from collections.abc import Callable

import streamlit as st

# --------------------------------------------------------------------------------
from gamma_apr.endpoints.endpoints_model import DatasetMeta, GetDataSourceGroup

# --------------------------------------------------------------------------------
from streamlit.runtime.scriptrunner import add_script_run_ctx

from poc_streamlit.util import build_acquisition_form, datetime_input, request_check_acquisition_status_from_gamma

if "last_api_request" not in st.session_state.keys():
    st.session_state["last_api_request"] = {"uuid": None, "file_uri": None, "completed": None}


# --------------------------------------------------------------------------------
SOMA_SERVER = "127.0.0.1"  # Teste com SOMA em 'localhost', comente a linha abaixo
SOMA_SERVER = "34.71.114.51"
dsg_dict = {
    "uuid": "DataSourceGrouping_37c1d9e6-5659-479c-a927-50406823a55d",
    "name": "almost_all_data_mq_13",
    "title": "almost_all_data_mq_13",
    "description": "Almost all data for machine 13",
    "data_sources": [
        "TMA_UG13_GE_EST_ENR_TEMP_6421",
        "TMA_UG13_GE_EST_ENR_TEMP_6422",
        "TMA_UG13_GE_EST_ENR_TEMP_6423",
        "TMA_UG13_GE_EST_ENR_TEMP_6424",
        "TMA_UG13_GE_EST_ENR_TEMP_6425",
        "TMA_UG13_GE_EST_ENR_TEMP_6426",
        "TMA_UG13_TU_SKID_TEMP_6432",
        "TMA_UG13_TU_SKID_TEMP_6433",
        "TMA_UG13_GE_MAN_TEMP_6021",
        "TMA_UG13_GE_MAN_TEMP_6022",
        "TMA_UG13_GE_MAN_TEMP_6023",
        "TMA_UG13_GE_MAN_TEMP_6024",
        "TMA_UG13_GE_MAN_LA_VIB_Y",
        "TMA_UG13_GE_MAN_LA_VIB_X",
        "TMA_UG13_GE_MAN_LNA_VIB_Y",
        "TMA_UG13_GE_MAN_LNA_VIB_X",
    ],
    "testing": False,
}
dsg: GetDataSourceGroup = GetDataSourceGroup(**dsg_dict)
SLEEP_INTERVAL = 1  # seconds
# --------------------------------------------------------------------------------


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
    # Code to get the data

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
                    print("delete", dataset_name)
                else:
                    pass
                    # st.warning("Selecione um dataset para excluir!")

        with tab2:
            st.write("Some code here")


setup_tasks([other_code])

build_acquisition_form([dsg])

# Aguardamos a solicitação de aquisição de dados ser enviada pelo usuário
while True:
    completed = st.session_state["last_api_request"]["completed"]
    if completed is not None:
        break
    time.sleep(SLEEP_INTERVAL / 4)

# Monitorando o progresso da aquisição de dados
with st.status("Downloading data...", expanded=True) as status:
    print("last_api_request", st.session_state["last_api_request"])
    while True:
        completed = st.session_state["last_api_request"]["completed"]
        if completed is not None:
            break
        time.sleep(SLEEP_INTERVAL / 4)
    st.success("Contacting the server...")
    my_comment = """
    Neste ponto a App já recebeu a resposta do servidor e salvou na session_state
    Exemplo de resposta:
    st.session_state["last_api_request"] = {
        'uuid': '5640da17-a6cc-4cd3-8...0d1658d8d9',
        'file_uri': 'file:///Volumes/dev/...30.parquet',
        'completed': 0,
        'record_count': 0}
    """
    i = 0
    file_uri = st.session_state["last_api_request"]["file_uri"]
    while True:
        response_dict = request_check_acquisition_status_from_gamma(st.session_state["last_api_request"]["uuid"])
        completed = response_dict["completed"]
        st.session_state["last_api_request"]["completed"] = completed
        step = response_dict["step"]
        record_count = response_dict["record_count"]
        file_uri = response_dict["file_uri"]
        if completed >= 100:
            print("break while loop")
            break
        i += 1
        if i % 5 == 0:
            print("step =", step)

        status.update(label=f"{completed}% downloaded.")
        time.sleep(SLEEP_INTERVAL)

    st.success("Download complete!")
    status.update(label="Download complete!", state="complete", expanded=False)


def clear_session_state():
    st.session_state["last_api_request"] = {"uuid": None, "file_uri": None, "completed": None}


st.button("Rerun", on_click=clear_session_state)

print("tasks finished")
