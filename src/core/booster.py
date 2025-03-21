from typing import Dict, List
from pydantic import BaseModel
from ..utils.sheets import SheetsClient
from ..llm.client import LLMClient
from ..config import settings
from ..utils.pdf import PDFGenerator
import json

class ResponseData(BaseModel):
    email: str
    sheet_data: Dict[str, List[Dict]]

class InterviewBooster:
    def __init__(self):
        self.sheets_client = SheetsClient(settings.CREDENTIALS_PATH)
        self.llm_client = LLMClient()
        self.pdf_gen = PDFGenerator()
        self.sheet_ids = [id.strip() for id in settings.SHEET_IDS.split(',')]

    def get_all_responses(self, email: str) -> ResponseData:
        """Fetch responses from all configured sheets"""
        all_data = {}
        for sheet_id in self.sheet_ids:
            records = self.sheets_client.get_sheet_data(sheet_id)
            all_data[sheet_id] = [{
                'timestamp': r['Timestamp'],
                'email': r['Email Address'],
                'responses': {k:v for k,v in r.items() 
                            if not k.startswith(('Timestamp', 'Email Address'))}
            } for r in records if r.get('Email Address', '').lower() == email.lower()]
        return ResponseData(email=email, sheet_data=all_data)

    def format_for_llm(self, data: ResponseData) -> str:
        """Structure data for LLM processing"""
        return f"User: {data.email}\nResponses:\n" + \
            '\n'.join(
                f'- {sheet_id}: {json.dumps(resp)}' 
                for sheet_id, responses in data.sheet_data.items()
                for resp in responses
            )

    def generate_report(self, data) -> str:
        """Generate personalized feedback report"""
        formatted_data = self.format_for_llm(data)
        return self.llm_client.generate_feedback(formatted_data)

    def generate_pdf_report(self, report_text: str, email: str) -> tuple[str, str]:
        """
        Generate a PDF report from the report text.
        
        Args:
            report_text: The text content of the report
            email: The email of the candidate
            
        Returns:
            Tuple containing the path to the PDF file and the markdown content
        """
        # Convert the report text to markdown format
        markdown_content = self._format_as_markdown(report_text)
        # Generate the PDF
        pdf_path = self.pdf_gen.create_report(markdown_content, email)
        return pdf_path, markdown_content

    def _format_as_markdown(self, report_text: str) -> str:
        """
        Format the report text as markdown.
        
        Args:
            report_text: The text content of the report
            
        Returns:
            The formatted markdown content
        """
        # The report text is already formatted by the LLM, just add a title
        markdown_content = "# Interview Feedback Report\n\n"
        markdown_content += report_text
        
        return markdown_content
