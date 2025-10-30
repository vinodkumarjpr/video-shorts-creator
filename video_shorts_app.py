import streamlit as st

# Page config
st.set_page_config(
    page_title="Video Shorts Creator",
    page_icon="🎬",
    layout="wide"
)

# Title
st.title("🎬 Video Shorts Creator")
st.markdown("---")

# Info message
st.info("✅ App successfully deployed on Streamlit Cloud!")

# Sidebar
with st.sidebar:
    st.header("⚙️ Settings")
    
    duration_minutes = st.number_input(
        "Clip Duration (minutes):",
        min_value=0,
        max_value=10,
        value=2
    )
    
    duration_seconds = st.number_input(
        "Additional seconds:",
        min_value=0,
        max_value=59,
        value=30
    )
    
    total_duration = (duration_minutes * 60) + duration_seconds
    st.success(f"✅ Clip duration: {total_duration} seconds")
    
    output_format = st.selectbox(
        "Output format:",
        ["mp4", "mkv", "avi", "mov"]
    )
    
    quality_preset = st.selectbox(
        "Quality:",
        ["High", "Medium", "Fast"],
        index=1
    )

# Main content
st.markdown("### 📁 Video Upload")
st.warning("⚠️ **Important:** Streamlit Cloud has 200MB file upload limit.")

uploaded_file = st.file_uploader(
    "Upload your video:",
    type=['mp4', 'avi', 'mov', 'mkv'],
    help="Max file size: 200MB on cloud deployment"
)

if uploaded_file:
    st.success(f"✅ File uploaded: {uploaded_file.name}")
    file_size = uploaded_file.size / (1024 * 1024)
    st.info(f"📊 File size: {file_size:.2f} MB")
    
    if file_size > 200:
        st.error("❌ File too large for cloud deployment. Use local deployment for large files.")
    else:
        st.warning("🚧 Video processing feature requires local deployment.")
        st.markdown("""
        **For full functionality:**
        1. Download the app files from GitHub
        2. Install locally: `pip install streamlit moviepy`
        3. Run: `streamlit run video_shorts_app.py`
        4. Process unlimited file sizes!
        """)

# Features section
with st.expander("✨ Features (Local Deployment)"):
    st.markdown("""
    - ✅ **Unlimited file size** support
    - ✅ **Full MKV support**
    - ✅ **Custom clip duration**
    - ✅ **Multiple output formats**
    - ✅ **Quality presets**
    - ✅ **Memory optimized**
    
    ### ⚠️ Cloud Limitations:
    - 200MB file size limit
    - No video processing (resource intensive)
    - Demo/UI preview only
    
    ### ✅ Local Deployment:
    - No file size limits
    - Full video processing
    - All features available
    """)

# Footer
st.markdown("---")
st.markdown(
    "<div style='text-align: center; color: gray;'>"
    "🎬 Video Shorts Creator | Demo Version for Cloud"
    "</div>",
    unsafe_allow_html=True
)
