import streamlit as st

from generate import load_tokenizer_and_model, generate, CACHE_DIR


def initialize() -> None:
    """Initialize session state and set page config"""

    st.set_page_config(
        page_title="Autoplot AI",
        page_icon="🤖",
        layout="wide",
        initial_sidebar_state="collapsed"
    )

    if "model" not in st.session_state or "tokenizer" not in st.session_state:
        with st.spinner("Loading model"):
            tokenizer, model = load_tokenizer_and_model(CACHE_DIR)
            st.session_state["tokenizer"] = tokenizer
            st.session_state["model"] = model

    if "text_versions" not in st.session_state:
        st.session_state["text_versions"] = [""]


def main() -> None:
    """User interface logic"""

    text_versions = st.session_state["text_versions"]
    tokenizer = st.session_state["tokenizer"]
    model = st.session_state["model"]

    button_cols = st.columns(3)
    with button_cols[0]:
        continue_btn = st.button("Дополнить")
    
    with button_cols[1]:
        undo_btn = st.button("Отменить")

    with button_cols[2]:
        st.download_button("Скачать результат", text_versions[-1], "result.txt")

    text_container = st.empty()
    text_area_attrs = {"label": "Текст", "height": 500}

    with text_container:
        working_text = st.text_area(value=text_versions[-1], **text_area_attrs)

    if continue_btn:
        if len(working_text) == 0:
            working_text = "Место действия -- "

        working_text = working_text[:-100] + generate(model, tokenizer, working_text[-100:])[0]

        with text_container:
            st.text_area(value=working_text, **text_area_attrs)
    
    if text_versions[-1] != working_text:
        text_versions.append(working_text)
        st.experimental_rerun()
    
    if undo_btn and len(text_versions) > 1:
        text_versions.pop()
        working_text = text_versions[-1]
        with text_container:
            st.text_area(value=working_text, **text_area_attrs)


if __name__ == "__main__":
    initialize()
    main()
