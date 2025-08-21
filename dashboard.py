import streamlit as st
import subprocess
import sys
import os
from pathlib import Path
import time
import webbrowser
import json
from datetime import datetime
import threading

# Page configuration
st.set_page_config(
    page_title="HR Attrition Intelligence Dashboard",
    page_icon="📊",  # keeps only for browser tab
    layout="wide",
    initial_sidebar_state="expanded"
)

# Professional CSS Styling
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');

    /* Global Styles */
    .main-header {
        font-family: 'Inter', sans-serif;
        text-align: center;
        color: #2c3e50;
        font-size: 2.5rem;
        font-weight: 700;
        margin-bottom: 2rem;
    }

/* Script Card Text Styling */
.script-card, .pipeline-card, .dashboard-card {
    color: #2c3e50 !important;  /* dark text */
}

.script-card h3, .pipeline-card h3, .dashboard-card h3 {
    font-size: 1.2rem;
    font-weight: 600;
    margin-bottom: 0.5rem;
    color: #2c3e50 !important;
}

.script-card p, .pipeline-card p, .dashboard-card p {
    font-size: 0.9rem;
    color: #555 !important;
    margin: 0.2rem 0;
}


    /* Button Styles */
    .stButton > button {
        background: #2c3e50;
        color: white;
        border: none;
        border-radius: 8px;
        padding: 0.6rem 1.5rem;
        font-weight: 500;
        font-size: 0.95rem;
        transition: all 0.2s ease;
        box-shadow: 0 3px 8px rgba(0,0,0,0.1);
        width: 100%;
    }

    .stButton > button:hover {
        transform: translateY(-1px);
        background: #34495e;
    }

    /* Alerts */
    .success-alert {
        background: #eafaf1;
        color: #2d7a46;
        padding: 1rem;
        border-radius: 8px;
        margin: 0.5rem 0;
        border: 1px solid #b8e0c2;
    }

    .error-alert {
        background: #fdecea;
        color: #a94442;
        padding: 1rem;
        border-radius: 8px;
        margin: 0.5rem 0;
        border: 1px solid #f5c6cb;
    }

    .info-alert {
        background: #e8f4fd;
        color: #31708f;
        padding: 1rem;
        border-radius: 8px;
        margin: 0.5rem 0;
        border: 1px solid #bcdff1;
    }

    /* Metric Cards */
    .metric-card {
        background: white;
        padding: 1.2rem;
        border-radius: 12px;
        text-align: center;
        box-shadow: 0 4px 20px rgba(0,0,0,0.08);
        margin: 0.5rem 0;
    }

    .metric-number {
        font-size: 2rem;
        font-weight: 600;
        color: #2c3e50;
        margin: 0;
    }

    .metric-label {
        font-size: 0.85rem;
        color: #6c757d;
        margin-top: 0.3rem;
    }

    /* Sidebar */
    .css-1d391kg {
        background: #f8f9fa;
    }

    /* Hide Branding */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
</style>
""", unsafe_allow_html=True)

# Initialize session state
if 'execution_history' not in st.session_state:
    st.session_state.execution_history = []

def log_execution(script_name, success, duration, output=None, error=None):
    """Log script execution results"""
    execution_record = {
        'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
        'script': script_name,
        'success': success,
        'duration': duration,
        'output': output,
        'error': error
    }
    st.session_state.execution_history.insert(0, execution_record)
    if len(st.session_state.execution_history) > 10:
        st.session_state.execution_history = st.session_state.execution_history[:10]

def run_script_with_progress(script_path, script_name):
    """Run a Python script with simulated progress"""
    start_time = time.time()
    try:
        project_root = Path(__file__).resolve().parent
        env = dict(os.environ)
        env['PYTHONPATH'] = str(project_root)

        progress_container = st.empty()
        with progress_container.container():
            st.markdown("Running script...")
            progress_bar = st.progress(0)
            status_text = st.empty()

        for i in range(100):
            progress_bar.progress((i + 1) / 100)
            if i < 30:
                status_text.text("Initializing...")
            elif i < 60:
                status_text.text("Processing...")
            elif i < 90:
                status_text.text("Analyzing...")
            else:
                status_text.text("Finalizing...")
            time.sleep(0.02)

        result = subprocess.run(
            [sys.executable, str(script_path)],
            capture_output=True,
            text=True,
            timeout=300,
            env=env,
            cwd=str(project_root)
        )

        progress_container.empty()
        duration = time.time() - start_time
        success = result.returncode == 0
        log_execution(script_name, success, duration, result.stdout, result.stderr)
        return success, result.stdout, result.stderr, duration

    except Exception as e:
        duration = time.time() - start_time
        log_execution(script_name, False, duration, None, str(e))
        return False, "", str(e), duration

def display_execution_metrics():
    if not st.session_state.execution_history:
        return
    st.markdown("### Execution Metrics")

    col1, col2, col3, col4 = st.columns(4)
    total_executions = len(st.session_state.execution_history)
    successful_executions = sum(1 for exec in st.session_state.execution_history if exec['success'])
    avg_duration = sum(exec['duration'] for exec in st.session_state.execution_history) / total_executions
    success_rate = (successful_executions / total_executions) * 100

    with col1:
        st.markdown(f"""<div class="metric-card"><div class="metric-number">{total_executions}</div><div class="metric-label">Total Runs</div></div>""", unsafe_allow_html=True)
    with col2:
        st.markdown(f"""<div class="metric-card"><div class="metric-number">{successful_executions}</div><div class="metric-label">Successful</div></div>""", unsafe_allow_html=True)
    with col3:
        st.markdown(f"""<div class="metric-card"><div class="metric-number">{avg_duration:.1f}s</div><div class="metric-label">Avg Duration</div></div>""", unsafe_allow_html=True)
    with col4:
        st.markdown(f"""<div class="metric-card"><div class="metric-number">{success_rate:.0f}%</div><div class="metric-label">Success Rate</div></div>""", unsafe_allow_html=True)

def run_report_generation(send_email=False):
    """Run report generation with optional email sending"""
    start_time = time.time()
    try:
        project_root = Path(__file__).resolve().parent
        env = dict(os.environ)
        env['PYTHONPATH'] = str(project_root)

        # Create a modified version of Email_Report.py that optionally skips email
        report_script = project_root / "etl" / "Email_Report.py"

        if not report_script.exists():
            return False, "", "Email_Report.py not found", 0

        # If we don't want to send email, we'll modify the environment to skip email
        if not send_email:
            env['SKIP_EMAIL'] = 'true'

        result = subprocess.run(
            [sys.executable, str(report_script)],
            capture_output=True,
            text=True,
            timeout=300,
            env=env,
            cwd=str(project_root)
        )

        duration = time.time() - start_time
        success = result.returncode == 0
        script_name = "Report Generation" + (" + Email" if send_email else "")
        log_execution(script_name, success, duration, result.stdout, result.stderr)
        return success, result.stdout, result.stderr, duration

    except Exception as e:
        duration = time.time() - start_time
        script_name = "Report Generation" + (" + Email" if send_email else "")
        log_execution(script_name, False, duration, None, str(e))
        return False, "", str(e), duration

def display_execution_history():
    if not st.session_state.execution_history:
        return
    st.markdown("### Recent Executions")
    for exec in st.session_state.execution_history[:5]:
        status_icon = "Success" if exec['success'] else "Failed"
        status_class = "success-alert" if exec['success'] else "error-alert"
        with st.expander(f"{status_icon} - {exec['script']} - {exec['timestamp']} ({exec['duration']:.1f}s)"):
            if exec['output']:
                st.code(exec['output'], language='text')
            if exec['error']:
                st.error(exec['error'])

def main():
    st.markdown('<h1 class="main-header">HR Attrition Intelligence Dashboard</h1>', unsafe_allow_html=True)

    project_root = Path(__file__).resolve().parent
    etl_dir = project_root / "etl"

    scripts_info = {
        "reviews_scraper.py": {"display_name": "Reviews Scraper", "description": "Scrapes employee reviews from external sources.", "category": "Data Collection", "estimated_time": "2-3 minutes"},
        "internal_hrms_data_generator.py": {"display_name": "HRMS Data Generator", "description": "Generates synthetic HRMS data with realistic patterns.", "category": "Data Generation", "estimated_time": "1-2 minutes"},
        "data_merger.py": {"display_name": "Data Merger", "description": "Merges scraped reviews with HRMS data.", "category": "Data Processing", "estimated_time": "3-4 minutes"},
        "push.py": {"display_name": "Data Push", "description": "Pushes processed data to the database with validation.", "category": "Data Storage", "estimated_time": "1-2 minutes"}
    }

    # Sidebar
    with st.sidebar:
        st.markdown("## Control Panel")
        if st.button("Refresh Status"):
            st.rerun()
        if st.button("Clear History"):
            st.session_state.execution_history = []
            st.success("History cleared")
            time.sleep(1)
            st.rerun()
        st.markdown("---")
        st.markdown("### System Status")
        all_scripts_exist = True
        for script_file in scripts_info.keys():
            script_path = etl_dir / script_file
            status = "Available" if script_path.exists() else "Missing"
            st.markdown(f"{script_file}: {status}")
            if not script_path.exists():
                all_scripts_exist = False
        main_script = project_root / "main.py"
        st.markdown(f"main.py: {'Available' if main_script.exists() else 'Missing'}")
        st.success("All systems operational" if all_scripts_exist else "Some components missing")

    # Tabs
    tab1, tab2, tab3, tab4, tab5 = st.tabs(["Scripts", "Pipeline", "Reports", "Analytics", "Monitoring"])

    with tab1:
        st.markdown("## Individual Script Execution")
        cols = st.columns(2)
        for i, (script_file, info) in enumerate(scripts_info.items()):
            with cols[i % 2]:
                script_path = etl_dir / script_file
                st.markdown(f"""<div class="script-card"><h3>{info['display_name']}</h3><p><strong>Category:</strong> {info['category']}</p><p><strong>Duration:</strong> ~{info['estimated_time']}</p><p>{info['description']}</p></div>""", unsafe_allow_html=True)
                if st.button(f"Run {info['display_name']}", key=f"run_{script_file}"):
                    if script_path.exists():
                        success, stdout, stderr, duration = run_script_with_progress(script_path, info['display_name'])
                        if success:
                            st.markdown(f'<div class="success-alert">{info["display_name"]} completed successfully in {duration:.1f}s.</div>', unsafe_allow_html=True)
                            if stdout: st.expander("View Output").code(stdout, language='text')
                        else:
                            st.markdown(f'<div class="error-alert">{info["display_name"]} failed after {duration:.1f}s.</div>', unsafe_allow_html=True)
                            if stderr: st.expander("Error Details").code(stderr, language='text')

    with tab2:
        st.markdown("## Complete ETL Pipeline")
        st.markdown("""<div class="pipeline-card"><h3>Full Data Pipeline</h3><p>Executes all ETL steps in sequence: Reviews Scraper → HRMS Generator → Data Merger → Data Push</p><p><strong>Estimated Time:</strong> 7-11 minutes</p></div>""", unsafe_allow_html=True)
        if st.button("Execute Complete Pipeline", key="full_pipeline"):
            main_script = project_root / "main.py"
            if main_script.exists():
                success, stdout, stderr, duration = run_script_with_progress(main_script, "Complete Pipeline")
                if success:
                    st.markdown(f'<div class="success-alert">Pipeline executed successfully in {duration:.1f}s.</div>', unsafe_allow_html=True)
                    if stdout: st.expander("View Complete Output").code(stdout, language='text')
                else:
                    st.markdown(f'<div class="error-alert">Pipeline execution failed after {duration:.1f}s.</div>', unsafe_allow_html=True)
                    if stderr: st.expander("Error Details").code(stderr, language='text')
            else:
                st.error("main.py not found")

    with tab3:
        st.markdown("## HR Analytics Reports")
        st.markdown("Generate comprehensive HR analytics reports with charts and insights.")

        col1, col2 = st.columns(2)

        with col1:
            st.markdown("""
            <div class="script-card">
                <h3>📊 Generate Report Only</h3>
                <p><strong>Function:</strong> Creates PDF report with analytics</p>
                <p><strong>Output:</strong> HR_Analytics_Report.pdf</p>
                <p><strong>Duration:</strong> ~30-60 seconds</p>
                <p>Generates a comprehensive analytics report with charts, KPIs, and department insights without sending email.</p>
            </div>
            """, unsafe_allow_html=True)

            if st.button("📊 Generate Report", key="generate_report_only"):
                with st.spinner("Generating HR Analytics Report..."):
                    success, stdout, stderr, duration = run_report_generation(send_email=False)
                    if success:
                        st.markdown(f'<div class="success-alert">📊 Report generated successfully in {duration:.1f}s! Check for HR_Analytics_Report.pdf in the project directory.</div>', unsafe_allow_html=True)
                        if stdout:
                            st.expander("View Generation Log").code(stdout, language='text')

                        # Check if PDF was created and offer download
                        pdf_path = Path(__file__).resolve().parent / "HR_Analytics_Report.pdf"
                        if pdf_path.exists():
                            with open(pdf_path, "rb") as pdf_file:
                                st.download_button(
                                    label="📥 Download Report",
                                    data=pdf_file.read(),
                                    file_name="HR_Analytics_Report.pdf",
                                    mime="application/pdf",
                                    key="download_report"
                                )
                    else:
                        st.markdown(f'<div class="error-alert">❌ Report generation failed after {duration:.1f}s.</div>', unsafe_allow_html=True)
                        if stderr:
                            st.expander("Error Details").code(stderr, language='text')

        with col2:
            st.markdown("""
            <div class="script-card">
                <h3>📧 Generate Report + Send Email</h3>
                <p><strong>Function:</strong> Creates PDF report and emails it</p>
                <p><strong>Output:</strong> PDF report sent via email</p>
                <p><strong>Duration:</strong> ~30-90 seconds</p>
                <p>Generates the analytics report and automatically sends it to the configured email recipient.</p>
            </div>
            """, unsafe_allow_html=True)

            if st.button("📧 Generate & Email Report", key="generate_and_email_report"):
                with st.spinner("Generating and emailing HR Analytics Report..."):
                    success, stdout, stderr, duration = run_report_generation(send_email=True)
                    if success:
                        st.markdown(f'<div class="success-alert">📧 Report generated and emailed successfully in {duration:.1f}s!</div>', unsafe_allow_html=True)
                        if stdout:
                            st.expander("View Generation & Email Log").code(stdout, language='text')
                    else:
                        st.markdown(f'<div class="error-alert">❌ Report generation/email failed after {duration:.1f}s.</div>', unsafe_allow_html=True)
                        if stderr:
                            st.expander("Error Details").code(stderr, language='text')

        st.markdown("---")
        st.markdown("### Report Configuration")
        st.info("""
        **Email Configuration**: Reports are sent using the email settings in your `.env` file:
        - `EMAIL_SENDER`: Your Gmail address
        - `EMAIL_PASSWORD`: Your Gmail app password
        - `EMAIL_RECEIVER`: Recipient email address

        **Report Contents**: The generated report includes:
        - Executive summary with key KPIs
        - Department-wise analysis and attrition rates
        - Performance and engagement metrics
        - Workforce demographics and trends
        - Visual charts and graphs
        """)

    with tab4:
        st.markdown("## Analytics Dashboard")
        st.markdown("""<div class="dashboard-card"><h3>Looker Studio Dashboard</h3><p>Access the HR attrition analytics dashboard with interactive visualizations, key metrics, and predictive insights.</p></div>""", unsafe_allow_html=True)
        looker_url = "https://lookerstudio.google.com/reporting/5c455533-2a58-4ada-9b71-edcb282d6fed/page/Da6UF/edit"
        if st.button("Open Analytics Dashboard"):
            webbrowser.open(looker_url)
            st.markdown(f"[Open Dashboard]({looker_url})")

    with tab5:
        st.markdown("## Monitoring & History")
        display_execution_metrics()
        st.markdown("---")
        display_execution_history()
        if st.session_state.execution_history:
            if st.button("Export Execution Log"):
                log_data = json.dumps(st.session_state.execution_history, indent=2)
                st.download_button("Download Log JSON", log_data, file_name=f"execution_log_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json", mime="application/json")
        else:
            st.markdown('<div class="info-alert">No execution history available. Run scripts to see monitoring data.</div>', unsafe_allow_html=True)

    st.markdown("---")
    st.markdown("""<div style="text-align:center; color:#64748b; font-size:0.9rem; margin-top:2rem;"><p>HR Attrition Intelligence Dashboard v2.0 | Built with Streamlit</p></div>""", unsafe_allow_html=True)

if __name__ == "__main__":
    main()
