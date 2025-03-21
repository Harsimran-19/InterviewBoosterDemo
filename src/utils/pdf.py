from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors
import markdown2
import os
import re

class PDFGenerator:
    def __init__(self):
        self.styles = getSampleStyleSheet()
        
        # Add custom styles for better formatting with unique names to avoid conflicts
        # Use custom style names to avoid conflicts with built-in styles
        self._add_style(ParagraphStyle(
            name='CustomBodyText',
            fontName='Helvetica',
            encoding='UTF-8',
            fontSize=12,
            leading=14,
            textColor=colors.black
        ))
        
        self._add_style(ParagraphStyle(
            name='CustomHeading2',
            fontName='Helvetica-Bold',
            fontSize=14,
            leading=16,
            textColor=colors.black,
            spaceAfter=10
        ))
        
        self._add_style(ParagraphStyle(
            name='CustomHeading3',
            fontName='Helvetica-Bold',
            fontSize=12,
            leading=14,
            textColor=colors.black,
            spaceAfter=8
        ))
    
    def _add_style(self, style):
        """Safely add a style to the stylesheet, avoiding duplicates"""
        if style.name not in self.styles:
            self.styles.add(style)

    def create_report(self, markdown_content: str, email: str) -> str:
        """
        Create a PDF report from markdown content.
        
        Args:
            markdown_content: The markdown content to convert to PDF
            email: The email of the candidate for the filename
            
        Returns:
            The path to the generated PDF file
        """
        # Ensure reports directory exists
        os.makedirs('reports', exist_ok=True)
        
        # Create a sanitized filename from the email
        safe_email = re.sub(r'[^\w\-_\.]', '_', email)
        pdf_path = f'reports/{safe_email}_report.pdf'
        
        # Create the PDF document
        doc = SimpleDocTemplate(
            pdf_path, 
            pagesize=letter,
            rightMargin=72, 
            leftMargin=72,
            topMargin=72, 
            bottomMargin=72
        )
        
        # Convert markdown to HTML
        try:
            html = markdown2.markdown(
                markdown_content,
                extras=['tables', 'fenced-code-blocks']
            )
        except Exception as e:
            # Fallback to plain text if markdown conversion fails
            html = f"<p>{markdown_content}</p>"
        
        # Build the PDF content
        story = []
        
        # Add header
        story.append(Paragraph(f"<b>Interview Report for {email}</b>", self.styles['Heading1']))
        story.append(Spacer(1, 20))
        
        # Process content with proper handling of markdown elements
        sections = html.split('<h2>')
        
        # Process the first section (if any)
        if sections:
            first_section = sections[0].replace('<p>', '').replace('</p>', '')
            for paragraph in first_section.split('<br />'):
                if paragraph.strip():
                    story.append(Paragraph(paragraph, self.styles['CustomBodyText']))
                    story.append(Spacer(1, 8))
        
        # Process any h2 sections
        for i in range(1, len(sections)):
            section = sections[i]
            if section.strip():
                # Extract the heading
                if '</h2>' in section:
                    heading, content = section.split('</h2>', 1)
                    story.append(Paragraph(heading, self.styles['CustomHeading2']))
                    story.append(Spacer(1, 10))
                    
                    # Process the content
                    content = content.replace('<p>', '').replace('</p>', '')
                    for paragraph in content.split('<br />'):
                        if paragraph.strip():
                            story.append(Paragraph(paragraph, self.styles['CustomBodyText']))
                            story.append(Spacer(1, 8))
                else:
                    # No heading found, just process the content
                    for paragraph in section.split('<br />'):
                        if paragraph.strip():
                            story.append(Paragraph(paragraph, self.styles['CustomBodyText']))
                            story.append(Spacer(1, 8))
        
        # Build the PDF
        try:
            doc.build(story)
            return pdf_path
        except Exception as e:
            # If there's an error building the PDF, create a simple version
            doc = SimpleDocTemplate(pdf_path, pagesize=letter)
            story = [
                Paragraph(f"<b>Interview Report for {email}</b>", self.styles['Heading1']),
                Spacer(1, 20),
                Paragraph("Error creating formatted report. Displaying plain text:", self.styles['CustomBodyText']),
                Spacer(1, 10),
                Paragraph(markdown_content, self.styles['CustomBodyText'])
            ]
            doc.build(story)
            return pdf_path
