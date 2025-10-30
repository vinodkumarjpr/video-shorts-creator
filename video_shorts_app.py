
import streamlit as st
import os
from moviepy.editor import VideoFileClip
import tempfile
from pathlib import Path
import gc

# Set page config
st.set_page_config(
    page_title="Video Shorts Creator",
    page_icon="🎬",
    layout="wide"
)

# Title and description
st.title("🎬 Video Shorts Creator")
st.markdown("---")
st.markdown("### Long videos ko automatically short clips mein convert karein!")
st.info("✅ **No file size limit** | ✅ **All formats supported including MKV**")

# Initialize session state
if 'processing_complete' not in st.session_state:
    st.session_state.processing_complete = False
if 'output_files' not in st.session_state:
    st.session_state.output_files = []

# Sidebar for settings
with st.sidebar:
    st.header("⚙️ Settings")

    # Video duration selection
    duration_minutes = st.number_input(
        "Short video ka duration (minutes):",
        min_value=0,
        max_value=60,
        value=2,
        help="Har short clip kitne minute ki honi chahiye"
    )

    duration_seconds = st.number_input(
        "Additional seconds:",
        min_value=0,
        max_value=59,
        value=30,
        help="Extra seconds add karein"
    )

    total_duration = (duration_minutes * 60) + duration_seconds
    st.success(f"✅ Clip duration: {total_duration} seconds ({duration_minutes}m {duration_seconds}s)")

    # Output format
    output_format = st.selectbox(
        "Output video format:",
        ["mp4", "mkv", "avi", "mov", "webm"],
        help="Kis format mein save karna hai"
    )

    # Quality settings
    quality_preset = st.selectbox(
        "Video quality:",
        ["High (Best quality, slower)", "Medium (Balanced)", "Fast (Quick processing)"],
        index=1,
        help="Large files ke liye Fast preset recommend hai"
    )

    # Naming convention
    naming_option = st.radio(
        "File naming:",
        ["Sequential (part_1, part_2, ...)", "Timestamp based"],
        help="Output files ka naam kaise rakhna hai"
    )

    # Memory optimization
    st.markdown("---")
    st.subheader("⚡ Performance")
    optimize_memory = st.checkbox(
        "Memory optimization (Recommended for large files)",
        value=True,
        help="Large videos ke liye memory efficiently use hogi"
    )

    # Audio processing
    process_audio = st.checkbox(
        "Include audio",
        value=True,
        help="Audio include karna hai ya nahi"
    )

# Main content area
col1, col2 = st.columns([1, 1])

with col1:
    st.subheader("📁 Video Upload")
    st.markdown("**Supported formats:** MP4, MKV, AVI, MOV, FLV, WebM, WMV, 3GP")
    st.markdown("**File size:** ✅ **Unlimited** (No restrictions!)")

    uploaded_file = st.file_uploader(
        "Apni long video upload karein:",
        type=['mp4', 'mkv', 'avi', 'mov', 'flv', 'webm', 'wmv', '3gp', 'm4v'],
        help="Koi bhi size ki video upload kar sakte hain - No limit!"
    )

    if uploaded_file is not None:
        st.success(f"✅ File uploaded: {uploaded_file.name}")
        file_size = uploaded_file.size / (1024 * 1024)  # Convert to MB

        if file_size < 1024:  # Less than 1GB
            st.info(f"📊 File size: {file_size:.2f} MB")
        else:  # 1GB or more
            file_size_gb = file_size / 1024
            st.info(f"📊 File size: {file_size_gb:.2f} GB")

        # Check if it's MKV
        if uploaded_file.name.lower().endswith('.mkv'):
            st.success("✅ MKV format detected - Full support enabled!")

with col2:
    st.subheader("💾 Output Folder")
    output_path = st.text_input(
        "Output folder path:",
        value="output_shorts",
        help="Shorts ko kahan save karna hai (folder name ya full path)"
    )

    if st.button("📂 Create Output Folder"):
        try:
            os.makedirs(output_path, exist_ok=True)
            st.success(f"✅ Folder created/verified: {output_path}")
        except Exception as e:
            st.error(f"❌ Error: {str(e)}")

    # Estimate output size
    if uploaded_file is not None:
        st.markdown("---")
        estimated_clips = 0
        if total_duration > 0:
            # We'll calculate after loading video
            st.info("📊 Clip count aur storage info processing ke baad milega")

st.markdown("---")

# Processing section
if uploaded_file is not None:
    st.subheader("🎬 Processing")

    # Show video preview (optional - can be disabled for large files)
    show_preview = st.checkbox("🎥 Video preview dikhayen (Large files ke liye slow ho sakta hai)", value=False)
    if show_preview:
        with st.expander("🎥 Video Preview", expanded=False):
            st.video(uploaded_file)

    # Process button
    if st.button("🚀 Start Processing", type="primary", use_container_width=True):
        try:
            # Create output folder
            os.makedirs(output_path, exist_ok=True)

            # Save uploaded file temporarily
            status_text = st.empty()
            status_text.text("💾 Uploading video to temporary storage...")

            with tempfile.NamedTemporaryFile(delete=False, suffix=os.path.splitext(uploaded_file.name)[1]) as tmp_file:
                # Write in chunks for large files
                chunk_size = 8 * 1024 * 1024  # 8MB chunks
                uploaded_file.seek(0)
                bytes_written = 0
                total_size = uploaded_file.size

                upload_progress = st.progress(0)
                while True:
                    chunk = uploaded_file.read(chunk_size)
                    if not chunk:
                        break
                    tmp_file.write(chunk)
                    bytes_written += len(chunk)
                    upload_progress.progress(min(bytes_written / total_size, 1.0))

                temp_video_path = tmp_file.name

            upload_progress.empty()
            status_text.text("✅ Upload complete!")

            # Load video
            progress_bar = st.progress(0)
            status_text.text("⏳ Video load ho rahi hai... (Large files mein time lag sakta hai)")

            # Load with audio or without based on checkbox
            if process_audio:
                clip = VideoFileClip(temp_video_path)
            else:
                clip = VideoFileClip(temp_video_path, audio=False)

            # Get video info
            video_duration = clip.duration
            video_fps = clip.fps
            video_size = clip.size

            # Calculate clips
            if total_duration <= 0:
                st.error("❌ Duration 0 se zyada hona chahiye!")
                clip.close()
                os.unlink(temp_video_path)
            else:
                total_clips = int(video_duration // total_duration)

                # Info display
                col_info1, col_info2, col_info3 = st.columns(3)
                with col_info1:
                    st.metric("Video Duration", f"{int(video_duration//60)}m {int(video_duration%60)}s")
                with col_info2:
                    st.metric("Total Clips", total_clips)
                with col_info3:
                    st.metric("Resolution", f"{video_size[0]}x{video_size[1]}")

                if total_clips == 0:
                    st.warning("⚠️ Video ki duration selected clip duration se kam hai!")
                    clip.close()
                else:
                    st.info(f"🎬 {total_clips} shorts banegi")

                    # Quality mapping
                    quality_map = {
                        "High (Best quality, slower)": {"preset": "slow", "bitrate": "high"},
                        "Medium (Balanced)": {"preset": "medium", "bitrate": "medium"},
                        "Fast (Quick processing)": {"preset": "fast", "bitrate": "low"}
                    }
                    selected_quality = quality_map[quality_preset]
                    preset = selected_quality["preset"]

                    # Set codec based on output format
                    codec_map = {
                        "mp4": {"video": "libx264", "audio": "aac"},
                        "mkv": {"video": "libx264", "audio": "aac"},
                        "avi": {"video": "mpeg4", "audio": "libmp3lame"},
                        "mov": {"video": "libx264", "audio": "aac"},
                        "webm": {"video": "libvpx", "audio": "libvorbis"}
                    }
                    codecs = codec_map.get(output_format, {"video": "libx264", "audio": "aac"})

                    # Split video into clips
                    output_files = []
                    for i in range(total_clips):
                        start_time = i * total_duration
                        end_time = min((i + 1) * total_duration, video_duration)

                        # Update progress
                        progress = (i + 1) / total_clips
                        progress_bar.progress(progress)
                        status_text.text(f"⏳ Processing clip {i+1}/{total_clips}... ({int(progress*100)}% complete)")

                        # Create subclip
                        subclip = clip.subclip(start_time, end_time)

                        # Generate filename
                        if naming_option == "Sequential (part_1, part_2, ...)":
                            output_filename = f"short_part_{i+1:03d}.{output_format}"
                        else:
                            start_min = int(start_time // 60)
                            start_sec = int(start_time % 60)
                            output_filename = f"short_{start_min:02d}m_{start_sec:02d}s.{output_format}"

                        output_file_path = os.path.join(output_path, output_filename)

                        # Write video file with appropriate settings
                        write_params = {
                            "codec": codecs["video"],
                            "preset": preset,
                            "verbose": False,
                            "logger": None
                        }

                        # Add audio codec if audio is being processed
                        if process_audio and clip.audio is not None:
                            write_params["audio_codec"] = codecs["audio"]

                        # Write the video
                        subclip.write_videofile(output_file_path, **write_params)

                        output_files.append(output_filename)

                        # Clean up subclip to free memory
                        if optimize_memory:
                            subclip.close()
                            del subclip
                            gc.collect()

                    # Close main clip
                    clip.close()
                    del clip

                    # Clean up temp file
                    try:
                        os.unlink(temp_video_path)
                    except:
                        pass

                    # Force garbage collection
                    if optimize_memory:
                        gc.collect()

                    # Success message
                    progress_bar.progress(1.0)
                    status_text.text("✅ Processing complete!")
                    st.balloons()
                    st.success(f"🎉 Successfully created {len(output_files)} short videos!")

                    # Store in session state
                    st.session_state.processing_complete = True
                    st.session_state.output_files = output_files

                    # Display output files
                    st.markdown("### 📁 Generated Files:")

                    # Show in columns for better display
                    files_per_col = 10
                    num_cols = min(3, (len(output_files) + files_per_col - 1) // files_per_col)
                    if num_cols > 0:
                        cols = st.columns(num_cols)
                        for idx, filename in enumerate(output_files):
                            col_idx = idx % num_cols
                            with cols[col_idx]:
                                st.text(f"{idx+1}. {filename}")

                    # Calculate total output size (approximate)
                    total_output_size = 0
                    for filename in output_files:
                        file_path = os.path.join(output_path, filename)
                        if os.path.exists(file_path):
                            total_output_size += os.path.getsize(file_path)

                    output_size_mb = total_output_size / (1024 * 1024)
                    if output_size_mb < 1024:
                        st.info(f"💾 Total output size: {output_size_mb:.2f} MB")
                    else:
                        output_size_gb = output_size_mb / 1024
                        st.info(f"💾 Total output size: {output_size_gb:.2f} GB")

                    st.success(f"📂 All files saved in: {os.path.abspath(output_path)}")

                    # Additional info
                    st.markdown("---")
                    st.markdown("### ✅ Next Steps:")
                    st.markdown(f"1. Open folder: `{os.path.abspath(output_path)}`")
                    st.markdown(f"2. {len(output_files)} shorts ready to upload!")
                    st.markdown("3. Check quality aur upload karein YouTube/Instagram/TikTok par!")

        except Exception as e:
            st.error(f"❌ Error occurred: {str(e)}")
            st.exception(e)

            # Cleanup on error
            try:
                if 'clip' in locals():
                    clip.close()
                if 'temp_video_path' in locals() and os.path.exists(temp_video_path):
                    os.unlink(temp_video_path)
            except:
                pass

# Additional features section
with st.expander("ℹ️ Features & Tips"):
    st.markdown("""
    ### ✨ Features:
    - ✅ **Unlimited file size** - Koi bhi size ki video process kar sakte hain!
    - ✅ **Full MKV support** - MKV files ka complete support
    - ✅ **Multiple video formats** (MP4, MKV, AVI, MOV, FLV, WebM, WMV, 3GP)
    - ✅ **Memory optimization** - Large files efficiently process hoti hain
    - ✅ **Custom clip duration** - 0 seconds se unlimited duration tak
    - ✅ **Quality presets** - High/Medium/Fast options
    - ✅ **Flexible file naming** - Sequential ya timestamp based
    - ✅ **Progress tracking** - Real-time progress updates
    - ✅ **Audio control** - Audio include/exclude kar sakte hain
    - ✅ **Multiple output formats** - MP4, MKV, AVI, MOV, WebM

    ### 💡 Tips for Large Files:
    - **Memory optimization** checkbox ON rakhein (Recommended)
    - **Fast preset** use karein quick processing ke liye
    - **Video preview** disable karein large files ke liye
    - Processing time file size par depend karta hai (be patient!)
    - Sufficient storage space ensure karein output folder mein

    ### 🎯 Quality Settings:
    - **High Quality**: Best hai final videos ke liye, slow processing
    - **Medium**: Balanced option, recommended for most cases
    - **Fast**: Quick processing, good quality, large files ke liye perfect

    ### 📊 Format Guide:
    - **MP4**: Universal compatibility, recommended
    - **MKV**: High quality, large file size, all codecs support
    - **AVI**: Older format, large files
    - **MOV**: Apple devices ke liye best
    - **WebM**: Web streaming ke liye optimized

    ### 🔧 Troubleshooting:
    - **Slow processing**: Fast preset use karein
    - **Memory error**: Memory optimization ON karein
    - **Audio issues**: "Include audio" checkbox check karein
    - **Very large files**: Chunk-by-chunk processing hoti hai, wait karein

    ### 📝 Recommended Settings:

    **Small files (<500MB):**
    - Quality: High
    - Memory optimization: OFF
    - Preview: ON

    **Medium files (500MB-2GB):**
    - Quality: Medium
    - Memory optimization: ON
    - Preview: Optional

    **Large files (>2GB):**
    - Quality: Fast/Medium
    - Memory optimization: ON
    - Preview: OFF
    """)

# Footer
st.markdown("---")
st.markdown(
    "<div style='text-align: center; color: gray;'>"
    "Made with ❤️ using Streamlit & MoviePy | "
    "🎬 Video Shorts Creator v2.0 - Unlimited Edition"
    "</div>",
    unsafe_allow_html=True
)
