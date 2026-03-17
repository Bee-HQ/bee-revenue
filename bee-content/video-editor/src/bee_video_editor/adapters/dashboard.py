"""Streamlit dashboard for visual review of production projects."""

from __future__ import annotations

import sys
from pathlib import Path

import streamlit as st


def _cli_defaults() -> tuple[str, str]:
    """Parse --assembly-guide and --project-dir from CLI args passed after '--'."""
    guide = ""
    proj = "."
    args = sys.argv[1:]
    for i, arg in enumerate(args):
        if arg == "--assembly-guide" and i + 1 < len(args):
            guide = args[i + 1]
        elif arg == "--project-dir" and i + 1 < len(args):
            proj = args[i + 1]
    return guide, proj


def main():
    st.set_page_config(
        page_title="Bee Video Editor",
        page_icon="🎬",
        layout="wide",
    )

    st.title("Bee Video Editor")
    st.caption("AI-assisted video production from assembly guides")

    default_guide, default_proj = _cli_defaults()

    # Sidebar — project selection
    with st.sidebar:
        st.header("Project")
        assembly_guide_path = st.text_input(
            "Assembly Guide Path",
            value=default_guide,
            placeholder="/path/to/assembly-guide.md",
        )
        project_dir = st.text_input(
            "Project Directory",
            value=default_proj,
        )

        if st.button("Load Project") or (default_guide and "assembly_guide_path" not in st.session_state):
            st.session_state["assembly_guide_path"] = assembly_guide_path
            st.session_state["project_dir"] = project_dir

    if "assembly_guide_path" not in st.session_state or not st.session_state["assembly_guide_path"]:
        st.info("Enter an assembly guide path in the sidebar and click Load Project.")
        return

    # Load project
    from bee_video_editor.parsers.assembly_guide import parse_assembly_guide
    from bee_video_editor.services.production import ProductionConfig, ProductionState

    guide_path = st.session_state["assembly_guide_path"]
    proj_dir = Path(st.session_state["project_dir"])

    try:
        project = parse_assembly_guide(guide_path)
    except Exception as e:
        st.error(f"Failed to parse assembly guide: {e}")
        return

    summary = project.summary()

    # Overview tab
    tab_overview, tab_segments, tab_assets, tab_preview, tab_produce = st.tabs([
        "Overview", "Segments", "Assets", "Preview", "Produce",
    ])

    with tab_overview:
        _render_overview(project, summary, proj_dir)

    with tab_segments:
        _render_segments(project)

    with tab_assets:
        _render_assets(project, proj_dir)

    with tab_preview:
        _render_preview(proj_dir)

    with tab_produce:
        _render_produce(project, proj_dir)


def _render_overview(project, summary, proj_dir):
    st.header(project.title)

    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Total Segments", summary["total_segments"])
    col2.metric("Duration", project.total_duration)
    col3.metric("Resolution", project.resolution)
    col4.metric("Trim Sources", summary["trim_notes"])

    st.subheader("Segment Type Breakdown")
    col_types, col_sections = st.columns(2)

    with col_types:
        import pandas as pd
        type_data = []
        for seg_type, count in summary["segment_type_counts"].items():
            dur = summary["segment_type_durations_seconds"].get(seg_type, 0)
            type_data.append({
                "Type": seg_type,
                "Count": count,
                "Duration (s)": dur,
                "Duration": f"{dur // 60}m {dur % 60}s",
            })
        if type_data:
            st.dataframe(pd.DataFrame(type_data), use_container_width=True)

    with col_sections:
        st.write("**Sections:**")
        for section in summary["sections"]:
            seg_count = len(project.segments_in_section(section))
            st.write(f"- {section} ({seg_count} segments)")

    # Pre-production status
    st.subheader("Pre-Production Assets")
    pp_done = summary["pre_production_done"]
    pp_total = summary["pre_production_assets"]
    if pp_total > 0:
        st.progress(pp_done / pp_total, text=f"{pp_done}/{pp_total} ready")
    for asset in project.pre_production:
        icon = "✅" if asset.done else "⬜"
        st.write(f"{icon} [{asset.category}] {asset.description}")

    # Post checklist
    st.subheader("Post-Assembly Checklist")
    pc_done = summary["post_checklist_done"]
    pc_total = summary["post_checklist_items"]
    if pc_total > 0:
        st.progress(pc_done / pc_total, text=f"{pc_done}/{pc_total} done")
    for item in project.post_checklist:
        icon = "✅" if item.done else "⬜"
        st.write(f"{icon} {item.description}")


def _render_segments(project):
    st.header("Assembly Timeline")

    # Filters
    col1, col2 = st.columns(2)
    with col1:
        section_filter = st.selectbox(
            "Section",
            ["All"] + project.sections,
        )
    with col2:
        type_filter = st.selectbox(
            "Type",
            ["All", "NAR", "REAL", "GEN", "MIX", "SFX", "SPONSOR"],
        )

    segs = project.segments
    if section_filter != "All":
        segs = [s for s in segs if s.section == section_filter]
    if type_filter != "All":
        segs = [s for s in segs if s.segment_type.value == type_filter]

    # Color coding
    type_colors = {
        "NAR": "🟢", "REAL": "🟡", "GEN": "🔵", "MIX": "🟣", "SFX": "🔴", "SPONSOR": "⚪",
    }

    for seg in segs:
        icon = type_colors.get(seg.segment_type.value, "⚪")
        with st.expander(
            f"{icon} {seg.start}-{seg.end} | {seg.segment_type.value} | "
            f"{seg.subsection or seg.section} ({seg.duration_str})"
        ):
            col_v, col_a = st.columns(2)
            with col_v:
                st.write("**Visual:**")
                st.write(seg.visual)
            with col_a:
                st.write("**Audio:**")
                st.write(seg.audio)
            if seg.source_notes:
                st.write("**Source/Notes:**")
                st.code(seg.source_notes)


def _render_assets(project, proj_dir):
    st.header("Generated Assets")

    output_dir = proj_dir / "output"

    for subdir in ["graphics", "narration", "segments"]:
        d = output_dir / subdir
        if d.exists():
            files = sorted(d.glob("*"))
            if files:
                st.subheader(f"{subdir.title()} ({len(files)} files)")
                for f in files:
                    size_kb = f.stat().st_size / 1024
                    st.write(f"- `{f.name}` ({size_kb:.0f} KB)")

                    # Preview images
                    if f.suffix.lower() in (".png", ".jpg", ".jpeg"):
                        st.image(str(f), width=400)

                    # Preview audio
                    if f.suffix.lower() in (".mp3", ".wav", ".m4a"):
                        st.audio(str(f))

                    # Preview video
                    if f.suffix.lower() in (".mp4", ".mkv", ".webm"):
                        st.video(str(f))
        else:
            st.write(f"_{subdir}/_ — not yet generated")


def _render_preview(proj_dir):
    st.header("Preview")

    output_dir = proj_dir / "output"
    final_dir = output_dir / "final"

    if final_dir.exists():
        finals = list(final_dir.glob("*.mp4"))
        if finals:
            for f in finals:
                st.video(str(f))
        else:
            st.info("No final video yet. Run assembly first.")
    else:
        st.info("No output directory found. Initialize the project first.")

    # Show individual composited segments
    composited = output_dir / "composited"
    if composited.exists():
        files = sorted(composited.glob("*.mp4"))
        if files:
            st.subheader("Composited Segments")
            selected = st.selectbox("Select segment", [f.name for f in files])
            if selected:
                st.video(str(composited / selected))


def _render_produce(project, proj_dir):
    st.header("Production Controls")

    from bee_video_editor.services.production import ProductionConfig

    col1, col2 = st.columns(2)

    with col1:
        tts_engine = st.selectbox("TTS Engine", ["edge", "kokoro", "openai"])
        tts_voice = st.text_input("Voice (optional)", placeholder="en-US-GuyNeural")

    with col2:
        footage_dir = st.text_input("Footage Directory", value=str(proj_dir / "footage"))

    st.divider()

    config = ProductionConfig(
        project_dir=proj_dir,
        footage_dir=Path(footage_dir),
        tts_engine=tts_engine,
        tts_voice=tts_voice if tts_voice else None,
    )

    col_g, col_n, col_t, col_a = st.columns(4)

    with col_g:
        if st.button("Generate Graphics", use_container_width=True):
            from bee_video_editor.services.production import generate_graphics_for_project
            with st.spinner("Generating graphics..."):
                result = generate_graphics_for_project(project, config)
            st.success(f"Generated {len(result.succeeded)} graphics")
            if result.failed:
                st.error(f"Failed: {len(result.failed)} — {result.failed[0].error}")

    with col_n:
        if st.button("Generate Narration", use_container_width=True):
            from bee_video_editor.services.production import generate_narration_for_project
            with st.spinner("Generating narration..."):
                result = generate_narration_for_project(project, config)
            st.success(f"Generated {len(result.succeeded)} narration clips")
            if result.failed:
                st.error(f"Failed: {len(result.failed)} — {result.failed[0].error}")

    with col_t:
        if st.button("Trim Footage", use_container_width=True):
            from bee_video_editor.services.production import trim_source_footage
            with st.spinner("Trimming footage..."):
                result = trim_source_footage(project, config)
            st.success(f"Trimmed {len(result.succeeded)} clips")
            if result.failed:
                st.error(f"Failed: {len(result.failed)} — {result.failed[0].error}")

    with col_a:
        if st.button("Assemble Final", use_container_width=True):
            from bee_video_editor.services.production import assemble_final
            with st.spinner("Assembling final video..."):
                result = assemble_final(config)
            if result:
                st.success(f"Final video: {result}")
            else:
                st.error("No segments to assemble")


if __name__ == "__main__":
    main()
