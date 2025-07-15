from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from datetime import datetime
from PyPDF2 import PdfReader, PdfWriter
import os

class PDFService:
    def __init__(self):
        self.styles = getSampleStyleSheet()
        self.styles.add(ParagraphStyle(
            name='CustomTitle',
            parent=self.styles['Heading1'],
            fontSize=16,
            spaceAfter=30
        ))
        self.styles.add(ParagraphStyle(
            name='CustomHeading',
            parent=self.styles['Heading2'],
            fontSize=12,
            spaceAfter=12
        ))
        self.styles.add(ParagraphStyle(
            name='CustomBody',
            parent=self.styles['Normal'],
            fontSize=10,
            spaceAfter=6
        ))
        self.template_path = os.path.join("app", "static", "pdfs", "interview_report_form.pdf")

    def create_interview_report(self, feedback_data, output_path):
        doc = SimpleDocTemplate(output_path, pagesize=letter)
        elements = []

        # Title
        elements.append(Paragraph("Cambridge CS Interview Report", self.styles['CustomTitle']))
        elements.append(Paragraph(f"Generated on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}", self.styles['CustomBody']))
        elements.append(Spacer(1, 20))

        # Assessment Scores
        elements.append(Paragraph("Assessment Scores", self.styles['CustomHeading']))
        
        # Create table for scores
        data = [
            ['Category', 'Score (1-10)', 'Details'],
            ['Logical Thinking', feedback_data.get('logical_thinking', {}).get('score', 'N/A'), 
             feedback_data.get('logical_thinking', {}).get('details', '')],
            ['Pattern Recognition', feedback_data.get('pattern_recognition', {}).get('score', 'N/A'),
             feedback_data.get('pattern_recognition', {}).get('details', '')],
            ['Problem-Solving Approach', feedback_data.get('problem_solving', {}).get('score', 'N/A'),
             feedback_data.get('problem_solving', {}).get('details', '')],
            ['Communication', feedback_data.get('communication', {}).get('score', 'N/A'),
             feedback_data.get('communication', {}).get('details', '')],
            ['Overall Potential', feedback_data.get('overall_potential', {}).get('score', 'N/A'),
             feedback_data.get('overall_potential', {}).get('details', '')]
        ]

        table = Table(data, colWidths=[2*inch, 1*inch, 3*inch])
        table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 12),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
            ('TEXTCOLOR', (0, 1), (-1, -1), colors.black),
            ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 1), (-1, -1), 10),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('GRID', (0, 0), (-1, -1), 1, colors.black)
        ]))

        elements.append(table)
        elements.append(Spacer(1, 20))

        # Progression Analysis
        elements.append(Paragraph("Progression Analysis", self.styles['CustomHeading']))
        elements.append(Paragraph(feedback_data.get('progression', {}).get('analysis', ''), self.styles['CustomBody']))
        elements.append(Spacer(1, 20))

        # Recommendations
        elements.append(Paragraph("Recommendations", self.styles['CustomHeading']))
        elements.append(Paragraph(feedback_data.get('recommendations', {}).get('text', ''), self.styles['CustomBody']))

        # Build PDF
        doc.build(elements)

    def fill_interview_report(self, feedback_data, output_path):
        # Read the template PDF
        reader = PdfReader(self.template_path)
        writer = PdfWriter()

        # Get the first page
        page = reader.pages[0]
        fields = reader.get_fields()

        # Create a new page with the same content
        writer.add_page(page)

        # Fill in the form fields
        writer.update_page_form_field_values(
            writer.pages[0],
            {
                "Candidate Name": feedback_data.get("candidate_name", ""),
                "Date": datetime.now().strftime("%Y-%m-%d"),
                "Topic": feedback_data.get("topic", ""),
                "Logical Thinking Score": str(feedback_data.get("logical_thinking", {}).get("score", "")),
                "Logical Thinking Comments": feedback_data.get("logical_thinking", {}).get("details", ""),
                "Pattern Recognition Score": str(feedback_data.get("pattern_recognition", {}).get("score", "")),
                "Pattern Recognition Comments": feedback_data.get("pattern_recognition", {}).get("details", ""),
                "Problem Solving Score": str(feedback_data.get("problem_solving", {}).get("score", "")),
                "Problem Solving Comments": feedback_data.get("problem_solving", {}).get("details", ""),
                "Communication Score": str(feedback_data.get("communication", {}).get("score", "")),
                "Communication Comments": feedback_data.get("communication", {}).get("details", ""),
                "Overall Potential Score": str(feedback_data.get("overall_potential", {}).get("score", "")),
                "Progression Analysis": feedback_data.get("progression", {}).get("analysis", ""),
                "Recommendations": feedback_data.get("recommendations", {}).get("text", ""),
                "Supervisor Name": "AI Interview System",
                "Supervisor Signature": "AI Interview System"
            }
        )

        # Write the filled form to the output file
        with open(output_path, "wb") as output_file:
            writer.write(output_file)

    def parse_feedback_text(self, feedback_text):
        """Parse the feedback text into structured data for the form"""
        data = {
            "candidate_name": "Candidate",  # This should be provided by the user
            "topic": "",  # This should be provided by the session
            "logical_thinking": {"score": "", "details": ""},
            "pattern_recognition": {"score": "", "details": ""},
            "problem_solving": {"score": "", "details": ""},
            "communication": {"score": "", "details": ""},
            "overall_potential": {"score": "", "details": ""},
            "progression": {"analysis": ""},
            "recommendations": {"text": ""}
        }

        # Split the feedback into sections
        sections = feedback_text.split("\n\n")
        
        for section in sections:
            if "Logical Thinking" in section:
                score = self._extract_score(section)
                details = self._extract_details(section)
                data["logical_thinking"] = {"score": score, "details": details}
            elif "Pattern Recognition" in section:
                score = self._extract_score(section)
                details = self._extract_details(section)
                data["pattern_recognition"] = {"score": score, "details": details}
            elif "Problem-Solving Approach" in section:
                score = self._extract_score(section)
                details = self._extract_details(section)
                data["problem_solving"] = {"score": score, "details": details}
            elif "Communication" in section:
                score = self._extract_score(section)
                details = self._extract_details(section)
                data["communication"] = {"score": score, "details": details}
            elif "Overall Potential" in section:
                score = self._extract_score(section)
                details = self._extract_details(section)
                data["overall_potential"] = {"score": score, "details": details}
            elif "Progression" in section:
                data["progression"]["analysis"] = section
            elif "Recommendation" in section:
                data["recommendations"]["text"] = section

        return data

    def _extract_score(self, text):
        """Extract score from text (e.g., 'Logical Thinking (8)' -> '8')"""
        import re
        match = re.search(r'\((\d+)\)', text)
        return match.group(1) if match else ""

    def _extract_details(self, text):
        """Extract details from text, removing the score"""
        import re
        # Remove the score part and any leading/trailing whitespace
        return re.sub(r'\(\d+\)', '', text).strip() 