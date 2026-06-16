import os
import streamlit as st
from scraper import CodelabScraper
from formatter import CodelabFormatter

# Page config
st.set_page_config(
    page_title="Codelab Extractor & Exporter",
    page_icon="📥",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom Premium Styling
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&family=JetBrains+Mono:wght@400;500&display=swap');
    
    /* Global styles */
    .main .block-container {
        padding-top: 2rem;
        max-width: 1400px;
    }
    
    * {
        font-family: 'Inter', sans-serif;
    }
    
    /* Header Gradient Banner */
    .header-banner {
        background: linear-gradient(135deg, #1a73e8 0%, #764ba2 100%);
        padding: 2.5rem 2rem;
        border-radius: 12px;
        color: white;
        margin-bottom: 2rem;
        box-shadow: 0 4px 20px rgba(26, 115, 232, 0.15);
    }
    
    .header-banner h1 {
        font-weight: 700;
        font-size: 2.5rem;
        margin-bottom: 0.5rem;
        color: white !important;
        border: none;
    }
    
    .header-banner p {
        font-size: 1.1rem;
        opacity: 0.9;
        margin: 0;
    }
    
    /* Card/Section Styles */
    .stCard {
        background-color: white;
        border-radius: 12px;
        padding: 1.5rem;
        border: 1px solid #e2e8f0;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.05);
        margin-bottom: 1.5rem;
    }
    
    /* Styled labels */
    .st-emotion-cache-1qgm9z1 {
        font-weight: 600;
        color: #1e293b;
    }
    
    /* Callout Style for Preview */
    .preview-callout {
        border-left: 4px solid #1a73e8;
        background-color: #f0f7ff;
        padding: 1rem;
        border-radius: 0 8px 8px 0;
        margin: 1rem 0;
    }
    
    /* Code styling in preview */
    code {
        font-family: 'JetBrains Mono', monospace !important;
        font-size: 0.9em;
        background-color: #f1f5f9;
        padding: 0.2rem 0.4rem;
        border-radius: 4px;
        color: #0f172a;
    }
    
    pre code {
        background-color: transparent;
        padding: 0;
    }
    
    /* Button Customizations */
    .stButton>button {
        border-radius: 8px;
        font-weight: 600;
        padding: 0.6rem 1.5rem;
        transition: all 0.2s;
    }
    
    .stButton>button:hover {
        transform: translateY(-1px);
        box-shadow: 0 4px 12px rgba(26, 115, 232, 0.2);
    }
    </style>
""", unsafe_allow_html=True)

# App Title
st.markdown("""
    <div class="header-banner">
        <h1>Codelab Extractor & Exporter</h1>
        <p>Scrape, preview, and convert any Google Codelab into highly styled HTML, clean Markdown, or a polished PDF document.</p>
    </div>
""", unsafe_allow_html=True)

# Initialize Session State
if "scraped_data" not in st.session_state:
    st.session_state.scraped_data = None
if "last_url" not in st.session_state:
    st.session_state.last_url = ""

# Sidebar for scraper controls
with st.sidebar:
    st.markdown("### Scraper Settings")
    st.markdown("Provide a Google Codelabs link below to scrape it.")
    
    codelab_url = st.text_input(
        "Codelab URL", 
        placeholder="https://codelabs.developers.google.com/...",
        value=st.session_state.last_url
    )
    
    # Export options
    st.markdown("---")
    st.markdown("### Export Configuration")
    
    export_format = st.radio(
        "Output Format",
        ["HTML", "Markdown", "PDF"],
        index=0,
        help="Select the file format to compile your Codelab into."
    )
    
    # Default output directory path
    default_dir = os.path.join(os.getcwd(), "outputs")
    output_dir = st.text_input(
        "Destination Directory",
        value=default_dir,
        help="The local folder path on your computer where the file will be saved."
    )
    
    col1, col2 = st.columns(2)
    with col1:
        fetch_btn = st.button("Fetch & Preview", type="primary", use_container_width=True)
    with col2:
        export_btn = st.button("Export File", type="secondary", use_container_width=True, disabled=(st.session_state.scraped_data is None))

# Main Logic Execution
if fetch_btn:
    if not codelab_url.strip():
        st.error("Please enter a valid Codelab URL.")
    else:
        with st.spinner("Scraping Codelab contents..."):
            try:
                scraper = CodelabScraper()
                data = scraper.scrape(codelab_url.strip())
                st.session_state.scraped_data = data
                st.session_state.last_url = codelab_url.strip()
                st.rerun()  # Refresh screen to enable export and load preview
            except Exception as e:
                st.error(f"Error scraping Codelab: {str(e)}")
                st.info("Make sure the URL is accessible and starts with https://")

# Export Logic Execution
if export_btn and st.session_state.scraped_data:
    data = st.session_state.scraped_data
    
    # Sanitize Codelab ID for filename
    safe_filename = "".join([c if c.isalnum() or c in ['-', '_'] else '_' for c in data["id"]])
    
    # Match extension
    if export_format == "HTML":
        ext = ".html"
        content_func = lambda: CodelabFormatter.to_html(data)
    elif export_format == "Markdown":
        ext = ".md"
        content_func = lambda: CodelabFormatter.to_markdown(data)
    else: # PDF
        ext = ".pdf"
        
    filename = f"{safe_filename}{ext}"
    output_filepath = os.path.join(output_dir, filename)
    
    with st.spinner(f"Generating and exporting {export_format}..."):
        try:
            # Ensure folder exists
            os.makedirs(output_dir, exist_ok=True)
            
            if export_format == "PDF":
                CodelabFormatter.to_pdf(data, output_filepath)
            else:
                content = content_func()
                with open(output_filepath, "w", encoding="utf-8") as f:
                    f.write(content)
                    
            st.success(f"🎉 Successfully saved as **{export_format}**!")
            st.info(f"📁 Path: `{output_filepath}`")
            
        except Exception as e:
            st.error(f"Failed to export file: {str(e)}")

# Display Preview Panel
if st.session_state.scraped_data:
    data = st.session_state.scraped_data
    
    # Metadata Overview Card
    st.markdown(f"""
        <div class="stCard">
            <h2 style='margin-top:0; color:#1e293b;'>{data['title']}</h2>
            <p style='color:#64748b; font-size: 0.95rem; margin-bottom: 0.5rem;'>
                <b>Duration:</b> {data['total_duration']} minutes | 
                <b>Authors:</b> {data['authors'] if data['authors'] else 'N/A'} | 
                <b>Last Updated:</b> {data['last_updated'] if data['last_updated'] else 'N/A'}
            </p>
            <p style='margin:0; font-size: 0.85rem;'><b>Source URL:</b> <a href="{data['source_url']}" target="_blank">{data['source_url']}</a></p>
        </div>
    """, unsafe_allow_html=True)
    
    st.markdown("### 🔍 Live Preview")
    
    # Create Tabs for Codelab Steps
    step_titles = [f"Step {s['index'] + 1}: {s['title']}" for s in data["steps"]]
    
    if step_titles:
        tabs = st.tabs(step_titles)
        for i, tab in enumerate(tabs):
            step = data["steps"][i]
            with tab:
                st.markdown(f"**Step Duration:** {step['duration']} mins")
                st.markdown("---")
                
                # Render content markdown
                st.markdown(step["content_md"])
    else:
        st.warning("No steps were found to preview.")

else:
    # Landing / Introduction Card
    st.markdown("""
        <div class="stCard" style="text-align: center; padding: 3rem 2rem; border-style: dashed; border-width: 2px;">
            <div style="font-size: 4rem; margin-bottom: 1rem;">📝</div>
            <h3 style="color: #1e293b; margin-bottom: 0.5rem;">No Codelab Scraped Yet</h3>
            <p style="color: #64748b; max-width: 600px; margin: 0 auto 1.5rem auto;">
                Enter a Google Codelabs URL in the sidebar settings and click <b>Fetch & Preview</b>. 
                Once fetched, you'll be able to read all steps in the interactive preview area and save them locally.
            </p>
            <div style="display: flex; justify-content: center; gap: 2rem; font-size: 0.9rem; color: #475569;">
                <div>⚡ <b>Fast Parsing</b></div>
                <div>🎨 <b>Beautiful Themes</b></div>
                <div>📄 <b>Multiple Formats</b></div>
            </div>
        </div>
    """, unsafe_allow_html=True)
