import streamlit as st
from pdftopng.logging import get_last_n_logs
# import time

def display_log(file_path):
    with open(file_path, "r") as file:
        log_contents = file.readlines()
        
    # # log_contents = "".join(log_contents[::-1])
    log_contents = "".join(log_contents)

    return log_contents

# Display file contents with live updates
st.title("Live Log Viewer")

# file_path = st.text_input("Enter the path to the log file:", "/path/to/your/logfile.log")
file_path = "debug.log"

# Display area for the log contents
log_area = st.empty()

if st.button("Show Log"):
    # st.text_area("Log Contents", display_log(file_path), height=300, disabled=True)
    # st.text("Most recent first")
    
    st.subheader("sql log")
    logs = get_last_n_logs(10)
    logs = [str(log) for log in logs]
    logs = "\n".join(logs)
    st.text(logs)
    
    st.subheader("text log")
    st.text(display_log(file_path))\

# # Optional: Auto-refresh to show live updates
# if st.checkbox("Auto-refresh log"):
#     refresh_rate = st.slider("Select refresh rate (seconds):", 1, 10, 3)
#     while True:
#         st.text_area("Log Contents", display_log(file_path), height=300)
#         time.sleep(refresh_rate)
#         st.experimental_rerun()
