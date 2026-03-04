import streamlit as st
import pandas as pd
import xml.etree.ElementTree as ET
import os

# Page Configuration
st.set_page_config(layout="wide")

# Arabic Styling
st.markdown("""
<style>
.arabic-text {
    font-size: 34px;
    font-family: 'Amiri', 'Scheherazade', serif;
    direction: rtl;
    text-align: center;
    line-height: 2.3;
}
.next-ayah {
    font-size: 22px;
    font-family: 'Amiri', 'Scheherazade', serif;
    direction: rtl;
    text-align: center;
    color: gray;
}
</style>

<link href="https://fonts.googleapis.com/css2?family=Amiri&display=swap" rel="stylesheet">
""", unsafe_allow_html=True)

# Load Quran XML (Tanzil Uthmani)
@st.cache_data
def load_quran():
    tree = ET.parse("./Datasets/quran-uthmani.xml")
    root = tree.getroot()

    data = []
    global_index = 1  # 1-based indexing

    for sura in root.findall("sura"):
        surah_index = int(sura.attrib["index"])

        for aya in sura.findall("aya"):
            aya_index = int(aya.attrib["index"])
            text = aya.attrib["text"]

            data.append({
                "global_index": global_index,
                "surah_index": surah_index,
                "aya_index": aya_index,
                "text": text
            })

            global_index += 1

    return pd.DataFrame(data)

quran = load_quran()
TOTAL_AYAT = len(quran)

# Annotation File
ANNOTATION_FILE = "./Datasets/Aya_ends_PM_annotated.csv"

if os.path.exists(ANNOTATION_FILE):
    annotations_df = pd.read_csv(ANNOTATION_FILE)
else:
    annotations_df = pd.DataFrame(columns=[
        "global_index",
        "surah_index",
        "aya_index",
        "annotation",
        "text"
    ])
    annotations_df.to_csv(ANNOTATION_FILE, index=False)

# Session State Initialization
if "current_index" not in st.session_state:
    st.session_state.current_index = 1  # start from first ayah


# Sidebar Display Options
st.sidebar.title("Display Options")
is_mobile = st.sidebar.checkbox("Mobile Layout", value=False)

# Sidebar Navigation (Surah + Aya)
st.sidebar.write("---")
st.sidebar.title("Navigation")

surah_input = st.sidebar.number_input(
    "Surah Index",
    min_value=1,
    max_value=114,
    value=1
)

max_aya = int(quran[quran.surah_index == surah_input].aya_index.max())

aya_input = st.sidebar.number_input(
    "Aya Index",
    min_value=1,
    max_value=max_aya,
    value=1
)

if st.sidebar.button("Go To Aya"):
    row = quran[
        (quran.surah_index == surah_input) &
        (quran.aya_index == aya_input)
    ]
    if not row.empty:
        st.session_state.current_index = int(row.iloc[0].global_index)
        st.rerun()

# Display Current Ayah
current_index = st.session_state.current_index

if 1 <= current_index <= TOTAL_AYAT:

    ayah = quran.iloc[current_index - 1]

    st.title(f"Surah {ayah['surah_index']} - Aya {ayah['aya_index']}", text_alignment="center")
    
    # ---- Annotation Status Box ----
    is_annotated = ayah["global_index"] in annotations_df["global_index"].values
    if is_annotated:
        st.info("✅ This Ayah is already annotated.")
    else:
        st.warning("⚠️ This Ayah is NOT annotated yet.")

    # Current Ayah Preview
    st.write("---")
    st.markdown(
        f"<div class='arabic-text'>{ayah['text']} ({ayah['aya_index']})</div>",
        unsafe_allow_html=True
    )


    # Next Ayah Preview
    if current_index < TOTAL_AYAT:
        next_ayah = quran.iloc[current_index]
        st.write("---")
        st.markdown(
            f"<div class='next-ayah'>{next_ayah['text']}</div>",
            unsafe_allow_html=True
        )

    st.write("---")
    # st.subheader("Navigation")

    nav_col1, nav_col2 = st.columns(2)

    with nav_col1:
        if st.button("⬅ Previous", use_container_width=True):
            if st.session_state.current_index > 1:
                st.session_state.current_index -= 1
                st.rerun()

    with nav_col2:
        if st.button("Next ➡", use_container_width=True):
            if st.session_state.current_index < TOTAL_AYAT:
                st.session_state.current_index += 1
                st.rerun()

    st.write("---")
    st.subheader("Annotation")

    def annotate(label):

        global annotations_df

        # remove old annotation if exists
        annotations_df = annotations_df[
            annotations_df.global_index != ayah["global_index"]
        ]

        new_row = pd.DataFrame([{
            "global_index": ayah["global_index"],
            "surah_index": ayah["surah_index"],
            "aya_index": ayah["aya_index"],
            "annotation": label,
            "text": ayah["text"]
        }])

        annotations_df = pd.concat([annotations_df, new_row])
        annotations_df.to_csv(ANNOTATION_FILE, index=False)

        # move to next ayah
        st.session_state.current_index += 1
        st.rerun() # immediate refresh (fix first-click issue)

    labels = ['م', 'لا', 'ط', 'قلي', 'وقفة', 'ق', 'ز', 'ص',
              'تعانق', 'ج', 'صلي', 'س', 'ع', 'Nan']

    if is_mobile:
        cols_per_row = 3  # Mobile-friendly layout
    else:
        cols_per_row = 7   # PC default

    # ---- Render Buttons in Rows ----
    for i in range(0, len(labels), cols_per_row):
        row_labels = labels[i:i+cols_per_row]
        cols = st.columns(cols_per_row)

        for col, label in zip(cols, row_labels):
            if col.button(label, use_container_width=True):
                annotate(label)

    # Terminate Button

    st.write("---")
    if st.button("Terminate Session"):
        st.success("Session terminated. All progress saved.")
        st.stop()

else:
    st.success("شكرا جزيلا لكم، جعله الله في ميزان حسناتكم 🌿")

# Sidebar Progress
st.sidebar.write("---")
st.sidebar.title("Annotation Progress")
st.sidebar.write(f"Total Ayat: {TOTAL_AYAT}")
st.sidebar.write(f"Annotated: {len(annotations_df)}")
progress = len(annotations_df) / TOTAL_AYAT
st.sidebar.progress(progress)

# Sidebar Export
st.sidebar.write("---")
st.sidebar.title("Export Annotations")
if len(annotations_df) > 0:
    csv_data = annotations_df.to_csv(index=False).encode("utf-8")

    st.sidebar.download_button(
        label="⬇ Download Annotation CSV",
        data=csv_data,
        file_name="Aya_ends_PM_annotated.csv",
        mime="text/csv",
        use_container_width=True
    )
else:
    st.sidebar.info("No annotations yet to download.")

# # ---- Sidebar: Unannotated Ayahs ----
# st.sidebar.write("---")
# st.sidebar.title("Unannotated Ayahs")

# # Get list of unannotated ayahs
# unannotated_df = quran[~quran.global_index.isin(annotations_df.global_index)]

# if not unannotated_df.empty:
#     for _, row in unannotated_df.iterrows():
#         col1, col2 = st.sidebar.columns([2,1])

#         with col1:
#             st.markdown(f"Surah {row['surah_index']} - Aya {row['aya_index']}")

#         with col2:
#             if st.button("Show", key=f"show_{row['global_index']}"):
#                 st.session_state.current_index = int(row['global_index'])
#                 st.rerun()
#             if st.button("Clear", key=f"clear_{row['global_index']}"):
#                 # Just deselecting: could reset to first ayah or do nothing
#                 st.session_state.current_index = 1
#                 st.rerun()
# else:
#     st.sidebar.info("All ayahs are annotated ✅")

# ---- Sidebar: Show/Hide Unannotated Ayahs ----
st.sidebar.write("---")
st.sidebar.title("Unannotated Ayahs")

# Track show/hide state
if "show_unannotated" not in st.session_state:
    st.session_state.show_unannotated = False

# Number of ayahs to show
show_count = st.sidebar.number_input(
    "Number of Ayahs to Show",
    min_value=1,
    max_value=500,
    value=10
)

col_show, col_clear = st.sidebar.columns(2)
with col_show:
    if st.button("Show"):
        st.session_state.show_unannotated = True
        st.rerun()
with col_clear:
    if st.button("Clear"):
        st.session_state.show_unannotated = False
        st.rerun()

# ---- Display Unannotated Ayahs in Main Area ----
if st.session_state.show_unannotated:
    unannotated_df = quran[~quran.global_index.isin(annotations_df.global_index)]
    st.sidebar.subheader(f"📜 Unannotated Ayahs (Showing {min(len(unannotated_df), show_count)} of {len(unannotated_df)})")
    
    if not unannotated_df.empty:
        # Limit number of ayahs displayed
        for _, row in unannotated_df.head(show_count).iterrows():
            st.sidebar.markdown(
                f"Surah {row['surah_index']} - Aya {row['aya_index']}",
                text_alignment="center",
                unsafe_allow_html=True
            )
    else:
        st.info("All ayahs are annotated ✅")