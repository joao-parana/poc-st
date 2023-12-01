import datetime
import json
import time
from urllib.parse import urlencode

import pandas as pd
import streamlit as st

# --------------------------------------------------------------------------------
from gamma_apr.endpoints.endpoints_model import DatasetMeta
from gamma_apr.util import Util

SOMA_SERVER = "127.0.0.1"  # Teste com SOMA em 'localhost', comente a linha abaixo
SOMA_SERVER = "34.71.114.51"
REST_SERVER = "localhost"
REST_SERVER_PORT = 8970
# --------------------------------------------------------------------------------


def datetime_input(
    label: str,
    key_prefix: str,
    value: datetime.datetime | None = None,
    min_value: datetime.datetime | None = None,
    max_value: datetime.datetime | None = None,
) -> datetime.datetime:
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
        time_value = st.time_input(label=" ", value=datetime.time(0, 0), key=f"{key_prefix}_time")
    return datetime.datetime.combine(date_value, time_value)


def sampler(label: str = "Intervalo de amostragem", key_prefix: str = "") -> tuple[int, str]:
    col1, col2 = st.columns(2, gap="small")
    with col1:
        interval_value = st.number_input(
            label=label,
            value=1,
            min_value=1,
            max_value=3600,
            step=1,
            key=f"{key_prefix}_interval_value",
        )
    with col2:
        interval_units = st.selectbox(
            label=" ",
            options=["segundos", "minutos"],
            index=1,
            key=f"{key_prefix}_interval_units",
        )
    return (interval_value, interval_units)


# TODO: Fatorar o método aquire_dataset_from_gamma para fazer o request e
#  depois buscar o estado repetidas vezes


# Request dataset aquired by Gamma using /datasets/raw_by_meta route
def request_dataset_from_gamma(dataset_meta: DatasetMeta) -> dict:
    dataset_meta_dict = dataset_meta.model_dump()
    query_string = urlencode(dataset_meta_dict)
    # ATENÇÃO: O objeto DatasetMeta é passado como parâmetro na query string
    # usando o sufixo '/?{query_string}'

    uri = f"http://{REST_SERVER}:{REST_SERVER_PORT}/datasets/raw_by_meta/?{query_string}"
    err_msg = "Error getting the Gamma dataset using Rest API"
    result_dict = Util.get_request(uri, Exception, err_msg, timeout=1000)
    file_uri = result_dict["file_uri"]
    # dataset = pd.read_parquet(file_uri)
    # dataset.index = dataset.index.tz_localize(None)
    print(f"Dataset requested from Gamma: dataset_name = {dataset_meta.name} -> file_uri = {file_uri}, {result_dict}")
    return result_dict


def request_check_acquisition_status_from_gamma(uuid: str) -> dict:
    uri = f"http://{REST_SERVER}:{REST_SERVER_PORT}/datasets/check_completed_by_uuid/{uuid}"
    err_msg = "Error getting the Gamma dataset download status using Rest API"
    response_dict = Util.get_request(uri, Exception, err_msg, timeout=1000)
    print(
        "\n\n=========== response_dict ->\n",
        json.dumps(response_dict, indent=2),
        "\n\n",
    )
    return response_dict["result"]


# --------------------------------------------------------------------------------


# Get the dataset aquired by Gamma using /datasets/raw_by_meta route
def aquire_dataset_from_gamma(dataset_meta: DatasetMeta) -> pd.DataFrame:
    dataset_meta_dict = dataset_meta.model_dump()
    query_string = urlencode(dataset_meta_dict)
    # ATENÇÃO: O objeto DatasetMeta é passado como parâmetro na query string
    # usando o sufixo '/?{query_string}'
    uri = f"http://{REST_SERVER}:{REST_SERVER_PORT}/datasets/raw_by_meta/?{query_string}"
    err_msg = "Error getting the Gamma dataset using Rest API"
    result_dict = Util.get_request(uri, Exception, err_msg, timeout=10)
    file_uri = result_dict["file_uri"]
    # O arquivo pode não ter gerado neste momento pois o processo de acesso
    # ao servidor SOMA, se invocado, pode demorar muito para retornar
    # dependendo do tamanho do dataset. Por isso, é necessário esperar um
    # tempo para que o arquivo seja gerado.
    # TODO: retirar o hard-coded e tratar o erro de arquivo não encontrado
    time.sleep(5)
    dataset = pd.read_parquet(file_uri)
    dataset.index = dataset.index.tz_localize(None)
    # print(
    #    f'Dataset aquired from Gamma: dataset_name = {dataset_meta.name} -> '
    #    f'shape = {dataset.shape}, {dataset.columns}, file_uri = {file_uri}'
    # )
    return dataset


def check_acquisition_status() -> None:
    response: dict = request_check_acquisition_status_from_gamma(uuid)
    print("\n\nresponse", response, ", uuid", response["uuid"], ", completed", response["completed"])
    print("file_uri", response["file_uri"], "\n\n")
    st.session_state["last_api_request"] = {
        "uuid": response["uuid"],
        "file_uri": response["file_uri"],
        "completed": response["completed"],
        "record_count": response["record_count"],
    }


def request_acquisition(
    dsg_name: str,
    dataset_name: str,
    start_datetime: datetime.datetime,
    end_datetime: datetime.datetime,
    interval_value: int,
    interval_units: str,
    available_datasets: list[str],
) -> None:
    if not dsg_name:
        st.error("Indique um nome existente para o grupo de fontes de dados!")

    elif not dataset_name:
        st.error("Dê um nome para o dataset!")

    elif " " in dataset_name:
        st.error("O nome do dataset não pode conter espaços!")

    elif start_datetime > end_datetime:
        st.error("A data e hora de início não pode ser maior que a de fim!")

    elif dataset_name in available_datasets:
        st.error("Nome de dataset já existente! Digite um novo nome.")

    else:
        st.write("Aquisitando...")

        # dataset_meta: DatasetMeta = DatasetMeta.model_validate(meta)
        dataset_meta = DatasetMeta(
            name=dataset_name,
            data_source_group_name=dsg_name,
            start_datetime=str(start_datetime),
            end_datetime=str(end_datetime),
            interval=interval_value,
            interval_units=interval_units,
        )
        response: dict = request_dataset_from_gamma(dataset_meta)
        print("\n\nresponse", response, ", uuid", response["uuid"], ", completed", response["completed"])
        print("file_uri", response["file_uri"], "\n\n")
        st.session_state["last_api_request"] = {
            "uuid": response["uuid"],
            "file_uri": response["file_uri"],
            "completed": response["completed"],
            "record_count": response["record_count"],
        }
        # Salvando o dataset e o metadado adquirido em disco no formato parquet no diretório APR_DATASETS_DIR
        # success = register_dataset(acquired_dataset, meta, dataset_name)

        # if not success:
        #     st.error("Erro ao salvar o dataset!")
        #     st.stop()
        # st.success("Aquisição de dados concluída! Os dados estão disponíveis para modelagem.")
        # time.sleep(0.5)
        # st.rerun()


# Criando o formulário para aquisição de dados
def build_acquisition_form(dsg_list: list[dict]):
    with st.form("data_acquisition"):
        col1, col2 = st.columns(2, gap="medium")
        with col1:
            dataset_name = st.text_input(
                label="Nome do dataset",
                placeholder="Insira um nome para o dataset (sem espaços)",
                max_chars=50,
                key="dataset_name",
            )
            start_datetime = datetime_input(label="Início", key_prefix="acquire_start")
            interval_value, interval_units = sampler()

        with col2:
            # dsg_list = get_datasource_group_list()
            group_names = [group.name for group in dsg_list]

            st.session_state["data_source_group_list"] = dsg_list
            st.session_state["data_source_group_name"] = group_names[0]

            dsg_name = st.selectbox(
                label="Nome do grupo de fontes de dados registrado no GAMMA",
                options=group_names,
                key="data_source_group_name",
            )

            end_datetime = datetime_input(label="Fim", key_prefix="acquire_end")

        submitted = st.form_submit_button(label="Aquisitar")

        if submitted:
            request_acquisition(
                dsg_name,
                dataset_name,
                start_datetime,
                end_datetime,
                interval_value,
                interval_units,
                available_datasets=[],
            )
