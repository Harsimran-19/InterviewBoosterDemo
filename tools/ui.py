import os
import sys
import streamlit as st
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from src.core.booster import InterviewBooster
booster = InterviewBooster()
# Create reports directory
os.makedirs('reports', exist_ok=True)

def main():
    st.title('Interview Booster Report Generator')
    email = st.text_input('Enter candidate email:')
    
    if st.button('Generate Report'):
        if not email:
            st.warning('Please enter a valid email address')
            return
            
        with st.spinner('Generating report...'):
            # Get candidate data
            data = booster.get_all_responses(email)
            
            # Check if we have data for this email
            if not any(data.sheet_data.values()):
                st.warning('No responses found for this email')
                return
                
            # Generate the text report
            text_report = booster.generate_report(data)
            
            # Generate the PDF report
            try:
                pdf_path, markdown_content = booster.generate_pdf_report(text_report, email)
                
                # Store in session state for persistence
                st.session_state.pdf_path = pdf_path
                st.session_state.report_md = markdown_content
                
                st.success('Report generated successfully!')
                
                # Provide download button for the PDF
                with open(pdf_path, 'rb') as pdf_file:
                    pdf_data = pdf_file.read()
                    
                st.download_button(
                    label="Download PDF Report",
                    data=pdf_data,
                    file_name=os.path.basename(pdf_path),
                    mime='application/pdf',
                    key='pdf_download'
                )
                
                # Display the report content
                st.markdown("## Report Preview")
                st.markdown(markdown_content)
                
            except Exception as e:
                st.error(f"Error generating PDF report: {str(e)}")
    
    # Always show report if it exists in session state
    elif 'report_md' in st.session_state:
        st.markdown("## Previous Report")
        st.markdown(st.session_state.report_md)
        
        if 'pdf_path' in st.session_state and os.path.exists(st.session_state.pdf_path):
            with open(st.session_state.pdf_path, 'rb') as pdf_file:
                pdf_data = pdf_file.read()
                
            st.download_button(
                label="Download PDF Report",
                data=pdf_data,
                file_name=os.path.basename(st.session_state.pdf_path),
                mime='application/pdf',
                key='pdf_download_previous'
            )

if __name__ == '__main__':
    main()
