import datetime

import streamlit as st


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
