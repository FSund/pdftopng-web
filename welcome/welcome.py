import logging
import streamlit as st
import subprocess
import tempfile
import os
import zipfile
import io

logger = logging.getLogger(__name__)

st.title('PDF to PNG Converter')

uploaded_file = st.file_uploader("Choose a PDF file", type="pdf")

if uploaded_file is not None:
    # Save the uploaded PDF to a temporary file
    with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as temp_pdf_file:
        temp_pdf_file.write(uploaded_file.read())
        temp_pdf_file_path = temp_pdf_file.name

    # Create a temporary directory to store the PNG files
    temp_output_dir = tempfile.mkdtemp()

    # Construct the command to call pdftocairo
    output_prefix = os.path.join(temp_output_dir, "page")
    cmd = ['pdftocairo', '-png', temp_pdf_file_path, output_prefix]

    # Run the command
    try:
        subprocess.run(cmd, check=True)
    except subprocess.CalledProcessError as e:
        st.error(f"Error converting PDF to PNG: {e}")
        os.remove(temp_pdf_file_path)
        os.rmdir(temp_output_dir)
        st.stop()

    # List the generated PNG files
    png_files = sorted(f for f in os.listdir(temp_output_dir) if f.endswith('.png'))

    if not png_files:
        st.error("No PNG files were generated.")
        os.remove(temp_pdf_file_path)
        os.rmdir(temp_output_dir)
        st.stop()

    # Read images into memory
    images = []
    for png_file in png_files:
        png_path = os.path.join(temp_output_dir, png_file)
        with open(png_path, "rb") as f:
            images.append({'name': png_file, 'data': f.read()})

    # Clean up temporary files
    os.remove(temp_pdf_file_path)
    for png_file in png_files:
        os.remove(os.path.join(temp_output_dir, png_file))
    os.rmdir(temp_output_dir)

    # Display images and provide download buttons
    for img in images:
        st.image(img['data'], caption=img['name'])
        st.download_button(
            label=f"Download {img['name']}",
            data=img['data'],
            file_name=img['name'],
            mime="image/png"
        )

    # Create an in-memory ZIP file
    zip_buffer = io.BytesIO()
    with zipfile.ZipFile(zip_buffer, "w") as zip_file:
        for img in images:
            zip_file.writestr(img['name'], img['data'])
    zip_buffer.seek(0)

    # Provide download button for the ZIP file
    st.download_button(
        label="Download all images as ZIP",
        data=zip_buffer,
        file_name="images.zip",
        mime="application/zip"
    )
