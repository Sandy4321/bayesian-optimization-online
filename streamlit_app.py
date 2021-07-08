import streamlit as st
import collections
import pandas as pd
from skopt import Optimizer

import SessionState
from slider import Slider

session_state = SessionState.get(
    hidden=False, sliders=[], labels=collections.Counter(), history=[]
)

_, title = st.beta_columns([1, 7])

title.title("Bayesian optimization online")

edit = st.empty()

_, generate = st.beta_columns([2, 3])


def show_sidebar():
    with st.sidebar:
        slider_label = st.text_input("slider name", "slider")
        slider_min_value = st.text_input("slider min", "0")
        slider_max_value = st.text_input("slider max", "100")

        if st.button("add slider"):
            session_state.labels[slider_label] += 1
            slider_label += (
                (" " + str(session_state.labels[slider_label] - 1))
                if session_state.labels[slider_label] != 1
                else ""
            )
            session_state.sliders.append(
                Slider(
                    slider_label,
                    slider_min_value,
                    slider_max_value,
                )
            )
            session_state.history = []


def show_sliders(previous_config, current_config, view, first_time):
    to_remove = -1
    for i, slider in enumerate(session_state.sliders):

        if first_time or previous_config[i] != current_config[i]:
            view[i][0].empty()
            slider.value = current_config[i]
            current_config[i] = view[i][0].slider(**vars(slider), key="slider" + str(i))

        if (
            first_time
            and session_state.hidden == False
            and view[i][1].button("delete", key="button" + str(i))
        ):
            to_remove = i

    if to_remove != -1:
        session_state.sliders.pop(to_remove)
        view[to_remove][0].empty()
        view[to_remove][1].empty()
        previous_config.pop(to_remove)
        current_config.pop(to_remove)
        session_state.history = []


if edit.button("edit"):
    session_state.hidden = not session_state.hidden

if not session_state.hidden:
    show_sidebar()


previous_config = [slider.value for slider in session_state.sliders]
current_config = previous_config.copy()
sliders_view = [(st.empty(), st.empty()) for _ in range(len(previous_config))]

show_sliders(previous_config, current_config, sliders_view, True)


if generate.button("generate") and session_state.sliders:
    bayesian_optimizer = Optimizer(
        [(slider.min_value, slider.max_value) for slider in session_state.sliders]
    )
    if session_state.history:
        X = [x for x, _ in session_state.history]
        Y = [-y for _, y in session_state.history]
        bayesian_optimizer.tell(X, Y)

    new_config = [int(v) for v in bayesian_optimizer.ask()]
    current_config = [
        curr if prev != curr else new
        for prev, curr, new in zip(previous_config, current_config, new_config)
    ]

if previous_config != current_config:
    show_sliders(previous_config, current_config, sliders_view, False)

score = st.text_input("score", "")
if st.button("confirm"):
    try:
        score = int(score)
    except:
        score = None
    if score is not None:
        session_state.history.append((current_config, int(score)))

if session_state.history:
    df = pd.DataFrame(
        [config + [score] for config, score in session_state.history],
        columns=[slider.label for slider in session_state.sliders] + ["score"],
    )
    df
