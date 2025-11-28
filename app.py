import streamlit as st
import asyncio
import pandas as pd
import matplotlib.pyplot as plt
from simulation import run_simulation

st.set_page_config(page_title="CrowdSim AI", layout="wide")

# Display Header Image
st.image("dashboard_header.png", use_container_width=True)

st.title("🤖 CrowdSim AI")
st.markdown("Simulate a crowd with comprehensive, 360-degree feedback from diverse agents.")

# --- Input Section ---
st.sidebar.header("Configuration")


st.sidebar.subheader("Product Pitch / Questions")
pitch_inputs = []
for i in range(7):
    # Default value only for the first one to guide the user
    default_val = "What do you think of a subscription service for coffee beans?" if i == 0 else ""
    val = st.sidebar.text_input(f"Input {i+1}", value=default_val, key=f"pitch_{i}")
    if val.strip():
        pitch_inputs.append(val.strip())

# Combine inputs into a single question string (Legacy) or list (New)
# We pass the list 'pitch_inputs' directly to simulation
if not pitch_inputs:
    pitch_inputs = ["No questions provided."]

uploaded_file = st.sidebar.file_uploader("Upload Context Document (txt)", type=["txt"])
document_content = ""
if uploaded_file is not None:
    document_content = uploaded_file.read().decode("utf-8")
    st.sidebar.success("Document loaded!")

additional_context = st.sidebar.text_area("Additional Context (Max 500 chars)", 
    max_chars=500, 
    help="Provide extra details for the agents.")

# Agent Configuration
st.sidebar.divider()
st.sidebar.subheader("Agent Configuration")
num_agents = st.sidebar.slider("Number of Agents", min_value=3, max_value=25, value=5)
age_range = st.sidebar.slider("Age Range", min_value=19, max_value=60, value=(19, 60))

# Combine document and text area context
full_context = f"{document_content}\n\n{additional_context}".strip()

if st.sidebar.button("Run Simulation"):
    with st.spinner("Running simulation... This may take a moment."):
        # Run the async simulation loop
        try:
            results = asyncio.run(run_simulation(
                pitch_inputs, 
                full_context, 
                num_agents=num_agents, 
                min_age=age_range[0], 
                max_age=age_range[1]
            ))
            
            if "error" in results:
                st.error(f"Simulation failed: {results['error']}")
            else:
                st.session_state['results'] = results
                st.success("Simulation Complete!")
        except Exception as e:
            st.error(f"An error occurred: {e}")

# --- Dashboard Section ---
if 'results' in st.session_state:
    results = st.session_state['results']
    
    st.divider()
    st.header("📊 Analysis Dashboard")

    # Metrics Row
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Agents", len(results.get("agents", [])))
    with col2:
        st.metric("Overall Sentiment", f"{results.get('overall_sentiment', 0)}/10")
    with col3:
        st.metric("Questions Analyzed", len(results.get("question_details", [])))
        
    # Quality Metrics Row
    if "quality_metrics" in results:
        st.subheader("🏆 Quality Assurance Scores")
        q_col1, q_col2, q_col3 = st.columns(3)
        metrics = results["quality_metrics"]
        with q_col1:
            st.metric("Relevance", f"{metrics.get('relevance', 0)}/5")
        with q_col2:
            st.metric("Coherence", f"{metrics.get('coherence', 0)}/5")
        with q_col3:
            st.metric("Persona Fidelity", f"{metrics.get('fidelity', 0)}/5")

    # Charts
    st.subheader("Sentiment Trend")
    q_details = results.get("question_details", [])
    if q_details:
        df = pd.DataFrame(q_details)
        df['Question Num'] = range(1, len(df) + 1)
        
        # Bar chart of scores
        fig, ax = plt.subplots()
        colors = ['red' if s < 5 else 'grey' if s == 5 else 'green' for s in df['score']]
        ax.bar(df['Question Num'], df['score'], color=colors)
        ax.set_xlabel("Question Number")
        ax.set_ylabel("Sentiment Score (1-10)")
        ax.set_ylim(0, 10)
        st.pyplot(fig)
        
        # Detailed Table
        st.subheader("Detailed Breakdown")
        st.table(df[['question', 'score', 'label', 'summary']])

    # Report & Logs
    col_left, col_right = st.columns(2)
    
    with col_left:
        st.subheader("📝 Final Report")
        st.markdown(results.get("report", "No report generated."))

        # PDF Generation
        from fpdf import FPDF
        import tempfile

        def create_pdf(results_data):
            pdf = FPDF()
            pdf.add_page()
            pdf.set_font("Arial", size=12)
            
            # Title
            pdf.set_font("Arial", 'B', 16)
            pdf.cell(200, 10, txt="CrowdSim AI Report", ln=1, align='C')
            pdf.ln(10)
            
            # Overall Sentiment
            pdf.set_font("Arial", 'B', 12)
            pdf.cell(200, 10, txt=f"Overall Sentiment Score: {results_data.get('overall_sentiment', 'N/A')}/10", ln=1)
            pdf.ln(5)
            
            # Question Details
            pdf.set_font("Arial", 'B', 12)
            pdf.cell(200, 10, txt="Detailed Analysis:", ln=1)
            pdf.set_font("Arial", size=10)
            
            for i, qd in enumerate(results_data.get("question_details", [])):
                pdf.ln(2)
                # Handle unicode characters by replacing or encoding
                q_text = f"Q{i+1}: {qd['question']}".encode('latin-1', 'replace').decode('latin-1')
                pdf.multi_cell(0, 5, q_text)
                pdf.cell(0, 5, txt=f"Score: {qd['score']}/10 ({qd['label']})", ln=1)
                summary = f"Summary: {qd['summary']}".encode('latin-1', 'replace').decode('latin-1')
                pdf.multi_cell(0, 5, summary)
                pdf.ln(3)
            
            pdf.ln(5)
            # Full Report Text
            pdf.set_font("Arial", 'B', 12)
            pdf.cell(200, 10, txt="Full Report:", ln=1)
            pdf.set_font("Arial", size=10)
            report_text = results_data.get("report", "").encode('latin-1', 'replace').decode('latin-1')
            pdf.multi_cell(0, 5, report_text)
            
            return pdf

        if st.button("Generate PDF Report"):
            pdf = create_pdf(results)
            with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp_file:
                pdf.output(tmp_file.name)
                with open(tmp_file.name, "rb") as f:
                    st.download_button(
                        label="Download PDF",
                        data=f,
                        file_name="focus_group_report.pdf",
                        mime="application/pdf"
                    )

    with col_right:
        st.subheader("💬 Conversation Logs")
        with st.expander("View Full Logs", expanded=True):
            st.text(results.get("full_logs", "No logs available."))

else:
    st.info("Configure the simulation in the sidebar and click 'Run Simulation' to see results.")
