# %%

import os
import sklearn
import streamlit as st
import pickle
import sys

# Get to the right directory: the streamlit one (not pages)
# Get to chapter0_fundamentals directory (or whatever the chapter dir is)

from pathlib import Path
from chatbot import answer_question, Embedding, EmbeddingGroup

if "./chapter0_fundamentals/instructions" not in sys.path:
    sys.path.append("./chapter0_fundamentals/instructions")
if os.getcwd().endswith("chapter0_fundamentals") and "./instructions" not in sys.path:
    sys.path.append("./instructions")
if os.getcwd().endswith("pages") and "../" not in sys.path:
    sys.path.append("../")

MAIN = __name__ == "__main__"

# if MAIN:
#     from IPython import get_ipython
#     ipython = get_ipython()
#     ipython.run_line_magic("load_ext", "autoreload")
#     ipython.run_line_magic("autoreload", "2")

for stem in [".", "instructions", "..", "chapter0_fundamentals"]:
    files = Path(f"{stem}/pages").glob("*.py")
    names = [f.stem for f in files if f.stem[0].isdigit() and "Chatbot" not in f.stem]
    names = [name.split("]")[1].replace("_", " ").strip() for name in names]
    if len(names) > 0:
        break

# names are ["Ray Tracing", "CNNs", "Backprop", "ResNets", "Optimization"]

# %%

if "my_embeddings" not in st.session_state:
    paths = ["my_embeddings.pkl", "instructions/my_embeddings.pkl", "chapter0_fundamentals/instructions/my_embeddings.pkl"]
    for path in paths:
        if os.path.exists(path):
            # st.session_state["my_embeddings"] = EmbeddingGroup.load(path=path)
            with open(path, "rb") as f:
                st.session_state["my_embeddings"] = pickle.load(f)
            break
if "history" not in st.session_state:
    st.session_state["history"] = []

# %%

st.markdown(r"""
## 🤖 Chatbot

This is a simple chatbot that uses the GPT-4 model to answer questions about the material.

You can configure the chatbot with the settings on the right hand side:

* **Exercise sets** controls which sections the chatbot reads context from. You should only select the ones which are relevant for answering this query.
* **Model** chooses which GPT model will answer your question.
* **Temperature** controls the temperature parameter of the chatbot's output, or how "creative" the chatbot is.
* **Include solutions in context?** controls whether solutions to exercises are included in the model's context. You should generally not do this, unless you're e.g. asking for hints about the solution.
""")

question = st.text_area(
    label = "Prompt:", 
    value = "", 
    key = "input",
    placeholder="Type your prompt here, then press Ctrl+Enter.\nThe prompt will be prepended with most of the page content (so you can ask questions about the material)."
)

with st.sidebar:
    
    exercises = st.multiselect(
        "Exercise sets",
        options = names,
    )

    model = st.radio(
        "Model",
        options = ["gpt-4", "gpt-3.5-turbo", "text-davinci-003"],
        index = 1
    )

    temp = st.slider(
        "Temperature",
        min_value = 0.0,
        max_value = 2.0,
        value = 0.5,
    )

    include_solns = st.checkbox(
        "Include solutions in context?",
        value = False,
    )

    st.markdown("---")

    clear_output_button = st.button("Clear output")
    if clear_output_button:
        st.session_state["history"] = []
        st.session_state["suppress_output"] = True
    else:
        st.session_state["suppress_output"] = False

    st.markdown("")
    st.markdown("*Note - chat history is not yet supported, so you should limit your prompts to single questions.*")


st.markdown("## Response:")
response_global_container = st.container()

# import streamlit_chat as sc

# %%

if question and (not st.session_state["suppress_output"]):
    with response_global_container:
        st.info(question)
        response_container = st.empty()
        for i, hist in enumerate(st.session_state["history"]):
            if i % 2 == 0:
                st.info(hist)
            else:
                st.markdown(hist)
        st.session_state["history"].append(question)
        # Get all the embeddings, by reading from file
        my_embeddings: EmbeddingGroup = st.session_state["my_embeddings"]
        # If we're not including solutions, then filter them out
        if not include_solns:
            my_embeddings=my_embeddings.filter(title_filter = lambda x: "(solution)" not in x)
        # Also filter out content to specific sets of exercises, if asked to
        if exercises:
            my_embeddings=my_embeddings.filter(title_filter = lambda x: any([ex.replace("_", " ") in x for ex in exercises]))
        if len(my_embeddings) == 0:
            st.error("Warning - your filters are excluding all content from the chatbot's context window.")
            # st.stop()
        response = answer_question(
            my_embeddings=st.session_state["my_embeddings"], 
            question=question, 
            prompt_template="SIMPLE", # "SOURCES", "COMPLEX"
            model=model,
            debug=False,
            temperature=temp,
            container=response_container,
            max_len=1500, # max content length
            max_tokens=1500,
        )
else:
    st.session_state["suppress_output"] = False

# sort chronologically after top-k
# block signature

# %%
