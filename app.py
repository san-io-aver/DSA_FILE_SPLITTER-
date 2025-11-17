import streamlit as st
import io
from docx import Document
from docx.shared import Pt, RGBColor

def hex_to_rgb(hex_color):
    hex_color = hex_color.lstrip('#')
    return tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))

def create_docx(programs_list, font_name, font_size, font_color_hex):
    doc = Document()
    
    try:
        rgb = hex_to_rgb(font_color_hex)
        font_color = RGBColor(rgb[0], rgb[1], rgb[2])
    except Exception:
        font_color = RGBColor(0, 0, 0)

    for i, program in enumerate(programs_list):
        if i > 0:
            doc.add_page_break()
        
        program_number = i + 1
        full_title = f"Program {program_number}: {program['title']}"
        code = program['code']

        doc.add_heading(full_title, level=1)

        lines = code.split("\n")
        mid = len(lines) // 2
        left_code = "\n".join(lines[:mid])
        right_code = "\n".join(lines[mid:])

        table = doc.add_table(rows=1, cols=2)
        table.style = 'Table Grid'
        table.columns[0].width = Pt(240)
        table.columns[1].width = Pt(240)

        cell1 = table.rows[0].cells[0]
        p1 = cell1.paragraphs[0]
        run1 = p1.add_run(left_code)
        run1.font.name = font_name
        run1.font.size = Pt(font_size)
        run1.font.color.rgb = font_color

        cell2 = table.rows[0].cells[1]
        p2 = cell2.paragraphs[0]
        run2 = p2.add_run(right_code)
        run2.font.name = font_name
        run2.font.size = Pt(font_size)
        run2.font.color.rgb = font_color

        doc.add_paragraph("Output:")

    buffer = io.BytesIO()
    doc.save(buffer)
    buffer.seek(0)
    return buffer

st.set_page_config(page_title="Code to DOCX", layout="centered")
st.title("Code to DOCX Splitter 📄")
st.markdown("Add one or more code snippets. The app will number them and place each one in a two-column layout in a DOCX file for you to download.")

if 'programs' not in st.session_state:
    st.session_state.programs = []

st.header("1. Add a Program")
with st.form("add_program_form", clear_on_submit=True):
    program_title = st.text_input("Program Title (e.g., 'Linear Search')")
    program_code = st.text_area("Paste Your Code Here", height=250)
    submitted = st.form_submit_button("Add Program to List")

if submitted and program_title and program_code:
    st.session_state.programs.append({"title": program_title, "code": program_code})
    st.success(f"Added 'Program {len(st.session_state.programs)}: {program_title}'")
elif submitted:
    st.error("Please provide both a title and code.")

if st.session_state.programs:
    st.header("2. Set Styles & Download")

    st.subheader("Formatting Options")
    
    col1, col2 = st.columns(2)
    with col1:
        font_name = st.selectbox(
            "Select Font",
            ("Consolas", "Courier New", "Menlo", "Arial", "Calibri", "Times New Roman"),
            index=0
        )
        font_color = st.color_picker("Font Color", "#000000")
        
    with col2:
        font_size = st.number_input("Font Size", min_value=6, max_value=20, value=9)

    st.subheader("Document Overview")
    with st.expander("Click to see an overview of added programs"):
        for i, program in enumerate(st.session_state.programs):
            st.markdown(f"**Program {i+1}: {program['title']}**")
            st.code(program['code'][:200] + "...", language=None)

    st.subheader("Download")
    try:
        docx_buffer = create_docx(st.session_state.programs, font_name, font_size, font_color)
        st.download_button(
            label="Download All Programs as .docx",
            data=docx_buffer,
            file_name="Split_Code_Programs.docx",
            mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
            use_container_width=True
        )
    except Exception as e:
        st.error(f"Failed to generate DOCX file: {e}")

    if st.button("Clear All Programs", type="secondary"):
        st.session_state.programs = []
        st.rerun()

else:
    st.info("Add a program using the form above to get started.")
