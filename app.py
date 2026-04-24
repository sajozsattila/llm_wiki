import streamlit as st
import numpy as np
import os
import json
import time
from typing import Any, Dict, List, Optional, Tuple, Annotated
import threading
from pathlib import Path
from backend import run_agent
import copy
from io import StringIO

from docx import Document

# --------------------------------------------------
# Constants
# --------------------------------------------------
AVAILABLE_MODELS: Dict[str, str] = {
    "Gemma4": "mlx-community/gemma-4-e4b-it-4bit",
    "Qwen3.5": "mlx-community/Qwen3.5-9B-MLX-4bit",
}
MAX_TOOL_CALLS = 5
DATA_DIR = "data"
ARCHIVE_DIR = "archive"
TEMP_DIR = "/tmp"
SUPPORTED_EXTENSIONS_TEXT = {".md", ".txt", ".json", ".py", ".js", ".ts", ".jsx", ".tsx", ".html", ".css", ".yaml", ".yml",
                        ".csv", ".xml", ".sql", ".sh", ".rb", ".go", ".rs", ".java", ".cpp", ".c", ".h", ".hpp", ".php",
                        ".swift", ".kt", ".scala", ".r", ".R", ".m", ".mm", ".dart", ".lua", ".pl", ".pm", ".clj",
                        ".cs", ".vb", ".fs", ".fsx", ".ex", ".exs", ".erl", ".hrl", ".elm", ".graphql", ".gql",
                        ".proto", ".toml", ".ini", ".cfg", ".conf", ".env", ".gitignore", ".dockerfile",
                        ".dockerignore", ".gitattributes", ".gitmodules", ".gitconfig", ".gitignore", ".prettierrc",
                        ".eslintrc", ".babelrc", ".jshintrc", ".editorconfig", ".gitlab-ci.yml", ".travis.yml",
                        ".circleci/config.yml", ".github/workflows/*.yml", ".azure-pipelines.yml", ".jenkinsfile",
                        ".gitlab-ci.yml", ".gitlab-ci.yml"}
SUPPORTED_EXTENSIONS_TABLE = {".csv"}
SUPPORTED_EXTENSIONS_DOC = {".docx"}

SUPPORTED_EXTENSIONS = SUPPORTED_EXTENSIONS_TEXT | SUPPORTED_EXTENSIONS_DOC | SUPPORTED_EXTENSIONS_TABLE

temperature = 0.1
top_p = 0.95

# --------------------------------------------------
# Initialize session state
# --------------------------------------------------
# Model selector
if "selected_model" not in st.session_state:
    st.session_state.selected_model = "Gemma4"
if "editing_index" not in st.session_state:
    st.session_state.editing_index = None

if "editing_text" not in st.session_state:
    st.session_state.editing_text = ""
# Top-p
if "top_p" not in st.session_state:
    st.session_state.top_p = top_p
# Temperature
if "temperature" not in st.session_state:
    st.session_state.temperature = temperature
if "messages" not in st.session_state:
    st.session_state.messages = []
if "session_id" not in st.session_state:
    st.session_state.session_id = (
        f"{int(time.time())}"
        f"{np.random.randint(1000)}"
    )
if "uploaded_files" not in st.session_state:
    st.session_state.uploaded_files = []

# --------------------------------------------------
# Ensure directories exist
# --------------------------------------------------
os.makedirs(DATA_DIR, exist_ok=True)
os.makedirs(ARCHIVE_DIR, exist_ok=True)
os.makedirs(TEMP_DIR, exist_ok=True)


# --------------------------------------------------
# Persistence Helpers
# --------------------------------------------------
def save_chat_history(
        session_id: str,
        messages: List[Dict[str, str]]
) -> None:
    """
    Persist a chat session to disk.

    Args:
      * session_id: Unique identifier for the chat session.
      * messages: Full conversation history.

    """
    file_path = os.path.join(DATA_DIR, f"{session_id}.json")
    payload = {
        "session_id": session_id,
        "timestamp": session_id,
        "messages": messages,
    }
    with open(file_path, "w", encoding="utf-8") as f:
        json.dump(payload, f, indent=2, ensure_ascii=False)


def save_chat_history_background(
        session_id: str,
        messages: List[Dict[str, str]]
) -> None:
    def _target():
        try:
            save_chat_history(session_id, messages)
        except Exception as e:
            print(f"[save_chat_history] failed for session: {session_id}: {e}", file=sys.stderr)
    thread = threading.Thread(target=_target)
    thread.start()


def load_chat_history(session_id: str) -> List[Dict[str, str]]:
    """
    Load a chat session from disk.

    Args:
      * session_id: Unique identifier for the chat session.

    Returns:
      * list: Conversation history. Returns an empty list if the session does not exist.

    """
    if str(st.session_state.session_id) != session_id:
        file_path = os.path.join(DATA_DIR, f"{session_id}.json")
        session_messages = []
        if os.path.exists(file_path):
            with open(file_path, "r", encoding="utf-8") as f:
                session_messages = json.load(f)["messages"]
        st.session_state.messages = session_messages
        st.session_state.session_id = session_id


def get_latest_session_id() -> Optional[str]:
    """
    Return the most recently modified chat session ID.

    Returns:
      str | None: Latest session ID, or ``None`` if no sessions exist.

    """

    sessions = list_chat_sessions()
    if not sessions:
        return None
    return int(sessions[0]["id"])  # already sorted newest-first


def list_chat_sessions() -> List[str]:
    """
    List all stored chat session IDs.

    Returns:
      list[str]: Sorted list of session IDs.

    """
    sessions = []

    for filename in os.listdir(DATA_DIR):
        if not filename.endswith(".json"):
            continue

        session_id = filename.replace(".json", "")
        file_path = os.path.join(DATA_DIR, filename)

        try:
            with open(file_path, "r", encoding="utf-8") as f:
                data = json.load(f)

            # Find first user message
            first_user_msg = next(
                (
                    msg["content"]
                    for msg in data.get("messages", [])
                    if msg.get("role") == "user"
                ),
                "New conversation",
            )

            # Truncate for UI cleanliness
            label = (
                first_user_msg[:50] + "…"
                if len(first_user_msg) > 50
                else first_user_msg
            )

        except Exception:
            label = "⚠️ Corrupted conversation"

        sessions.append(
            {
                "id": session_id,
                "label": label,
            }
        )

    # Sort newest first
    return sorted(
        sessions,
        key=lambda x: x["id"],
        reverse=True,
    )


def archive_chat_session(session_id: str) -> None:
    """
    Archive (delete) a chat session from disk.

    Args:
      * session_id: Unique identifier for the chat session.

    """

    src = os.path.join(DATA_DIR, f"{session_id}.json")
    dst = os.path.join(ARCHIVE_DIR, f"{session_id}.json")

    if os.path.exists(src):
        os.rename(src, dst)


def read_file_content(file_object: str) -> str:
    """
    Read the content of a file.

    Args:
        file_path: Path to the file.

    Returns:
        str: File content as string.
    """
    print(f"Reading file content: {file_object.name}")
    try:
        # To convert to a string based IO:
        stringio = StringIO(file_object.getvalue().decode("utf-8"))
        string_data = stringio.read()
        return string_data
    except Exception as e:
        st.error(f"Error reading file: {e}")
        return ""


def clean_temp_files() -> None:
    """
    Clean up temporary files older than 1 hour.
    """
    cutoff_time = time.time() - 3600  # 1 hour in seconds
    temp_files = []

    for filename in os.listdir(TEMP_DIR):
        file_path = os.path.join(TEMP_DIR, filename)
        if os.path.isfile(file_path):
            try:
                stat = os.stat(file_path)
                if stat.st_mtime < cutoff_time:
                    os.remove(file_path)
                    temp_files.append(filename)
            except Exception:
                pass

    for filename in temp_files:
        try:
            os.remove(os.path.join(TEMP_DIR, filename))
        except Exception:
            pass


def docx_to_markdown(docx_file_object) -> str:
    """
    Reads a DOCX file and converts its content to Markdown.
    """
    try:
        temp_path = os.path.join(TEMP_DIR, f"temp_{docx_file_object.name}")
        with open(temp_path, "wb") as f:
            f.write(docx_file_object.read())

        doc = Document(temp_path)
        md_lines = []
        list_counter = 0  # Initialize here

        for para in doc.paragraphs:
            text = para.text.strip()
            style = para.style.name.lower().replace(" ", "_")

            # Handle numbered lists
            if style.startswith("list_number"):
                list_counter += 1
                md_lines.append(f"{list_counter}. {text}")

            # Handle bullet lists
            elif style.startswith("list_bullet"):
                md_lines.append(f"- {text}")

            # Handle headings
            elif style.startswith("heading"):
                level = style.split()[1]  # Get the level number
                md_lines.append(f"{'#' * int(level)} {text}")

            # Handle bold/italic
            elif style.startswith("normal"):
                formatted_text = text
                for run in para.runs:
                    if run.font.bold:
                        formatted_text = f"**{formatted_text}**"
                    if run.font.italic:
                        formatted_text = f"*{formatted_text}*"
                md_lines.append(formatted_text)

        result = "\n".join(line for line in md_lines if line.strip())
        os.remove(temp_path)
        return result

    except Exception as e:
        return f"Error during DOCX parsing: {e}"


def generate_response(input_for_llm):

    with st.chat_message(
            "assistant",
    ):
        with st.spinner("Thinking..."):
            placeholder = st.empty()

            # Prepare messages with file attachments
            messages_with_files = copy.deepcopy(st.session_state.messages)

            # Add file contents to the user message
            if uploaded_files:
                file_contents = []
                for uploaded_file in uploaded_files:
                    ext = Path(uploaded_file.name).suffix.lower()

                    if ext in SUPPORTED_EXTENSIONS_DOC:
                        # Convert docx to markdown
                        file_content = docx_to_markdown(uploaded_file)
                        file_name = uploaded_file.name
                        file_contents.append(f"File: {file_name}\n\n```markdown\n{file_content}\n```\n")
                    elif ext in SUPPORTED_EXTENSIONS_TEXT:
                        file_content = read_file_content(uploaded_file)
                        file_name = uploaded_file.name
                        file_contents.append(f"File: {file_name}\n\n```{ext}\n{file_content}\n```\n")
                    elif ext in SUPPORTED_EXTENSIONS_TABLE:
                        file_content = read_file_content(uploaded_file)
                        file_name = uploaded_file.name
                        file_contents.append(f"File: {file_name}\n\n```csv\n{file_content}\n```\n")
                    else:
                        continue  # Skip unsupported formats

                # Combine user input with file contents
                combined_content = f"{input_for_llm}\n\n---\n\nAttached Files:\n\n" + "\n\n".join(file_contents)
                # replace the simple msg
                messages_with_files[-1]["content"] = combined_content

            response = run_agent(messages_with_files, MAX_TOOL_CALLS, AVAILABLE_MODELS)
            response = response.replace("</think>", "")
            placeholder.markdown(response)

    assistant_message = {
        "role": "assistant",
        "content": response
    }

    st.session_state.messages.append(assistant_message)

    # Persist updated conversation
    save_chat_history(
        st.session_state.session_id,
        copy.deepcopy(st.session_state.messages)
    )

    # Clean up temporary files after processing
    clean_temp_files()


def handle_edit_submit(index: int, new_text: str):
    st.session_state.messages[index]["content"] = new_text
    st.session_state.messages = st.session_state.messages[:index + 1]
    st.session_state.editing_index = None

    generate_response(new_text)
    st.rerun()



# --------------------------------------------------
# Streamlit Page Config
# --------------------------------------------------
st.set_page_config(
    page_title="Local HF Chat",
    page_icon="🤖",
    layout="centered",
)

st.title("🤖 Local HuggingFace Chat")

# --------------------------------------------------
# Sidebar – Chat Session Manager
# --------------------------------------------------
# custom CSS
st.markdown(
    """
<style>
section[data-testid="stSidebar"] [class*="st-key-active_session_"],
section[data-testid="stSidebar"] [class*="st-key-session_row_"] {
  display: flex !important;
  flex-direction: row !important;
  align-items: center;
  gap: 0.25rem;
  flex-wrap: nowrap !important;
  width: 100%;
}

section[data-testid="stSidebar"] [class*="st-key-active_session_"] > div:first-child,
section[data-testid="stSidebar"] [class*="st-key-session_row_"] > div:first-child {
  flex: 1 1 auto;
  min-width: 0;
}

section[data-testid="stSidebar"] [class*="st-key-active_session_"] > div:last-child,
section[data-testid="stSidebar"] [class*="st-key-session_row_"] > div:last-child {
  flex: 0 0 1em;
  min-width: 1em;
}

section[data-testid="stSidebar"] [class*="st-key-active_session_"] > div:first-child div.stButton > button,
section[data-testid="stSidebar"] [class*="st-key-session_row_"] > div:first-child div.stButton > button {
  width: 100%;
  justify-content: flex-start;
}

section[data-testid="stSidebar"] [class*="st-key-session_row_"] > div:first-child div.stButton > button > * {
  min-width: 0;
}

section[data-testid="stSidebar"] [class*="st-key-session_row_"] > div:first-child div.stButton > button span,
section[data-testid="stSidebar"] [class*="st-key-session_row_"] > div:first-child div.stButton > button div {
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

section[data-testid="stSidebar"] [class*="st-key-delwrap_"] {
  opacity: 0;
  pointer-events: none;
  transition: opacity .12s ease-in-out
}

/* style for active button */
section[data-testid="stSidebar"] [class*="st-key-active_session_"] div.stButton > button {
  border: 2px solid rgb(255, 75, 75) !important;
  box-shadow: 0 0 0 1px rgba(255, 75,75, 0.2);
}

div.stButton > button {
  border: 0px
}
div.stButton > button:hover {
  outline-offset: -2px
}
div.stButton > button > span,
div.stButton > button > div {
  justify-content: flex-start !important;
  text-align: left !important;
  display: inline-flex !important;
}

section[data-testid="stSidebar"] [class*="st-key-session_row_"]:hover [class*="st-key-delwrap_"] {
  opacity: 1;
  pointer-events: auto;
}

</style>
    """, unsafe_allow_html=True
)
with st.sidebar:
    if st.button("New Chat"):
        st.session_state.session_id = (
            f"{int(time.time())}"
            f"{np.random.randint(1000)}"
        )
        st.session_state.messages = []
        st.session_state.uploaded_files = []
        st.rerun()

    # --------------------------------------------------
    # File Attachment Section (Main Window)
    # --------------------------------------------------
    st.divider()

    uploaded_files = st.file_uploader(
        "Upload files to attach to your message",
        type=list(SUPPORTED_EXTENSIONS),
        accept_multiple_files=True,
        help="Supported formats: Markdown, JSON, Python, JavaScript, HTML, CSS, and many more text-based formats."
    )

    st.divider()
    with st.container(key="mywrite"):
        st.write("Conversations")

    sessions = list_chat_sessions()

    for session in sessions:
        # make a safe suffix for keys that balso becomes part of a CSS class
        raw_id = session["id"]
        safe_id = "-"+raw_id

        # check the current session is this button or not
        is_active = str(session["id"]) == str(st.session_state.get("session_id", ""))
        # use different row key if it is active
        row_key = f"active_session_{safe_id}" if is_active else f"session_row_{safe_id}"

        row = st.container(
            key=row_key,
            horizontal=True,
            horizontal_alignment="left",
            gap="xxsmall",
        )

        with row:
            st.button(
                session["label"],
                key=f"open_{safe_id}",
                on_click=load_chat_history,
                args=[session["id"]],
            )

            if not is_active:
                # delete icon
                with st.container(key=f"delwrap_{safe_id}"):
                    st.button(
                        "",
                        key=f"delete_{safe_id}",
                        icon=":material/delete:",
                        type="tertiary",
                        help="Delete",
                        on_click=archive_chat_session,
                        args=[session["id"]],
                        width="content"
                    )
            else:
                st.write("")

    st.divider()
    st.subheader("Model Settings")

    st.session_state.selected_model = st.selectbox(
        "Model",
        options=list(AVAILABLE_MODELS.keys()),
        # index=AVAILABLE_MODELS[st.session_state.selected_model],
    )

    st.session_state.temperature = st.slider(
        "Temperature",
        min_value=0.0,
        max_value=2.0,
        value=st.session_state.temperature,
        step=0.05,
    )

    st.session_state.top_p = st.slider(
        "Top-p",
        min_value=0.0,
        max_value=1.0,
        value=st.session_state.top_p,
        step=0.05,
    )


# --------------------------------------------------
# Render Messages
# --------------------------------------------------
for i, msg in enumerate(st.session_state.messages):
    with st.chat_message(msg["role"]):

        if msg["role"] == "user":
            if st.session_state.editing_index == i:
                new_text = st.text_area("Edit message", value=st.session_state.editing_text, key=f"edit_area_{i}")
                c1, c2 = st.columns(2)
                with c1:
                    if st.button("Save", key=f"save_{i}"):
                        handle_edit_submit(i, new_text)
                with c2:
                    if st.button("Cancel", key=f"cancel_{i}"):
                        st.session_state.editing_index = None
                        st.rerun()
            else:
                col1, col2 = st.columns([0.9, 0.1])
                with col1:
                    st.markdown(msg["content"])
                with col2:
                    if st.button("✏️", key=f"edit_{i}"):
                        st.session_state.editing_index = i
                        st.session_state.editing_text = msg["content"]
                        st.rerun()
        else:
            st.markdown(msg["content"])

# --------------------------------------------------
# Input
# --------------------------------------------------
if st.session_state.editing_index is None:
    user_input = st.chat_input("What's on your mind?")
else:
    user_input = None

if user_input:
    st.session_state.messages.append({"role": "user", "content": user_input})
    i = len(st.session_state.messages) - 1
    with st.chat_message("user"):
        col1, col2 = st.columns([0.9, 0.1])
        with col1:
            st.markdown(user_input)
        with col2:
            if st.button("✏️", key=f"edit_{i}"):
                st.session_state.editing_index = i
                st.session_state.editing_text = user_input
                st.rerun()

    generate_response(user_input)
