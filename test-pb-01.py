import pickle
import threading
import time

import pandas as pd
import requests
import streamlit as st
from streamlit.runtime.scriptrunner import add_script_run_ctx

# Suponha que estas são as URLs dos seus endpoints
url1 = "http://localhost:8970/test/start"
url2 = "http://localhost:8970/test/status/c6f2-47f2-973c-865c5070de64"

# Variáveis de controle salvas no estado da sessão
if "progress" not in st.session_state:
    st.session_state.progress = 0
if "progress_bar" not in st.session_state:
    st.session_state.progress_bar = st.empty()
if 'thread_status' not in st.session_state.keys():
    st.session_state['thread_status'] = None


# Função para execução assincrona em outra thread
def fetch_data(uuid, update_progress_bar, update_my_data=None):
    # Não foi possível atualizar o objeto st.session_state à partir
    # da Thread que executa esta função. A opção foi receber duas
    # funções como parâmetro, uma para atualizar o progress bar e
    # outra para atualizar o objeto st.session_state.data
    while True:
        response = requests.get(url2, params={"uuid": uuid}, timeout=10)
        response.raise_for_status()
        data = response.json()
        step = data["step"]
        print(f'>>>>>>>> step = {step}, completed = {data["completed"]}')  # noqa T201
        # st.session_state.progress = data["completed"]
        update_progress_bar(data["completed"])
        if data["completed"] >= 100:  # noqa: PLR2004
            # st.session_state.data = data["my_object"]
            if update_my_data is not None:
                print(  # noqa T201
                    f'>>>>>>>> atualizando my_object = {data["my_object"]}'
                )
                update_my_data(data["my_object"])
            break
        time.sleep(1)  # Wait for a second before checking again


def update_progress_bar(completed):
    st.session_state.progress = completed
    print(  # T201
        f'>>>> update_progress_bar with completed = {completed}, '
        f'st.session_state.progress = {st.session_state.progress}'
    )
    if completed < 100:  # noqa PLR2004
        progress_text = "Operation in progress. Please wait."
        # st.progress(completed / 100, progress_text)
        st.session_state.progress_bar.progress(completed, progress_text)
    else:
        # st.progress(completed/100)
        st.session_state.progress_bar.progress(completed)


def update_my_data(my_data):
    st.session_state.data = my_data


for key in st.session_state.keys():
    print(f'* >> key = {key} -> value = {st.session_state[key]}')  # noqa T201


if "data" not in st.session_state:
    if st.session_state.thread_status is None:
        st.session_state.data = None

        response = requests.get(url1, timeout=10)
        response.raise_for_status()
        uuid = response.json()["uuid"]

        thread = threading.Thread(
            target=fetch_data,
            args=(
                uuid,
                update_progress_bar,
                update_my_data,
            ),
        )
        add_script_run_ctx(thread)
        print(f'>>> Starting Thread, progress={st.session_state.progress}')  # noqa T201
        st.session_state.thread_status = 'running'
        thread.start()


if st.session_state.data is not None:
    st.write('O dado chegou do SOMA')
    st.write(st.session_state.data)
    # Abrindo o pickel_file
    my_data = st.session_state.data
    if my_data['format'] == 'pickel':
        st.write('Conteúdo do pickel_file (ou arquivo Parquet)')
        my_obj = pickle.load(open(my_data['pickel_file'], 'rb'))  # noqa S301
    else:
        # formt == 'parquet'
        my_obj = pd.read_parquet(my_data['parquet_file'])
    st.write(my_obj)
else:
    time.sleep(2)
    # Enquanto o dado não chega do SOMA vamos mostrar o progresso
    print(  # noqa T201
        f'>>>>>> Calling st.rerun(), my_data={st.session_state.data}, '
        f'progress={st.session_state.progress}'
    )
    # st.rerun()
