#!/usr/bin/env python3
"""
Generative AI for Demystifying Legal Documents - Enhanced UI
A tool that simplifies complex legal documents into clear, accessible guidance.
"""

import streamlit as st
import PyPDF2
import docx
import re
import json
from datetime import datetime
from typing import Dict, List, Any, Optional
import textwrap
import base64

# Set page configuration
st.set_page_config(
    page_title="Legal Document Simplifier",
    page_icon="⚖️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for styling
st.markdown("""
<style>
    .main-header {
        font-size: 2.8rem;
        color: #1E3A8A;
        text-align: center;
        margin-bottom: 1.5rem;
        font-weight: 700;
    }
    .sub-header {
        font-size: 1.6rem;
        color: #1E3A8A;
        padding-bottom: 0.5rem;
        margin-top: 1.5rem;
        margin-bottom: 1rem;
        font-weight: 600;
    }
    .compact-section {
        background-color: #F8FAFC;
        border-radius: 0.75rem;
        padding: 1.25rem;
        margin-bottom: 1.25rem;
        border: 1px solid #E2E8F0;
        box-shadow: 0 2px 4px rgba(0,0,0,0.05);
    }
    .risk-high {
        border-left: 4px solid #DC2626;
    }
    .risk-medium {
        border-left: 4px solid #EA580C;
    }
    .risk-low {
        border-left: 4px solid #16A34A;
    }
    .legal-term {
        background-color: #EDE9FE;
        padding: 0.15rem 0.4rem;
        border-radius: 0.25rem;
        font-weight: 500;
        font-size: 0.9em;
        color: #5B21B6;
    }
    .summary-item {
        padding: 0.75rem;
        margin-bottom: 0.75rem;
        border-radius: 0.5rem;
        background-color: #F0F9FF;
        border-left: 3px solid #0EA5E9;
    }
    .section-card {
        background-color: white;
        border-radius: 0.5rem;
        padding: 1rem;
        margin-bottom: 1rem;
        border: 1px solid #E2E8F0;
        box-shadow: 0 1px 3px rgba(0,0,0,0.05);
        color: #000000 !important; /* Force black text */
    }
    .tag {
        display: inline-block;
        padding: 0.25rem 0.5rem;
        border-radius: 0.75rem;
        font-size: 0.75rem;
        font-weight: 600;
        margin-right: 0.5rem;
        margin-bottom: 0.5rem;
    }
    .tag-high {
        background-color: #FEE2E2;
        color: #B91C1C;
    }
    .tag-medium {
        background-color: #FFEDD5;
        color: #C2410C;
    }
    .tag-low {
        background-color: #DCFCE7;
        color: #166534;
    }
    .download-card {
        background: linear-gradient(135deg, #1E3A8A 0%, #3730A3 100%);
        color: white;
        border-radius: 0.75rem;
        padding: 1.5rem;
    }
    .icon-button {
        display: inline-flex;
        align-items: center;
        gap: 0.5rem;
        color: white !important;
    }
    .disclaimer-card {
        background-color: #FEF3C7;
        border-left: 4px solid #D97706;
        color: #000000 !important;
    }
</style>
""", unsafe_allow_html=True)

class LegalDocumentSimplifier:
    """Main class for simplifying legal documents"""
    
    def __init__(self):
        self.legal_terms = {
            "hereinafter": "from now on",
            "heretofore": "until now",
            "wherein": "in which",
            "whereby": "by which",
            "hereby": "by this",
            "herein": "in this document",
            "hereof": "of this",
            "hereto": "to this",
            "pursuant to": "according to",
            "notwithstanding": "despite",
            "indemnify": "compensate for harm or loss",
            "liable": "legally responsible",
            "obligation": "duty",
            "covenant": "formal agreement",
            "warranty": "promise or guarantee",
            "jurisdiction": "area of legal authority",
            "arbitration": "resolving disputes outside of court",
            "litigation": "taking legal action through court",
            "force majeure": "unavoidable circumstances",
            "confidentiality": "keeping information private"
        }
        
        self.common_clauses = {
            "confidentiality": "This section explains what information must be kept private and the consequences for sharing it.",
            "indemnification": "This section describes who is responsible for paying for damages or losses.",
            "limitation of liability": "This section limits how much one party can be held financially responsible.",
            "termination": "This section explains how and when the agreement can be ended.",
            "governing law": "This section states which state or country's laws will be used to interpret the agreement.",
            "dispute resolution": "This section explains how disagreements will be resolved, often through arbitration or mediation.",
            "force majeure": "This section excuses parties from fulfilling obligations due to extraordinary events beyond their control.",
            "representations and warranties": "This section contains promises about facts and conditions related to the agreement."
        }
    
    def extract_text_from_pdf(self, file) -> str:
        """Extract text from PDF files"""
        pdf_reader = PyPDF2.PdfReader(file)
        text = ""
        for page in pdf_reader.pages:
            text += page.extract_text() + "\n"
        return text
    
    def extract_text_from_docx(self, file) -> str:
        """Extract text from DOCX files"""
        doc = docx.Document(file)
        text = ""
        for paragraph in doc.paragraphs:
            text += paragraph.text + "\n"
        return text
    
    def extract_text_from_file(self, file) -> str:
        """Extract text from uploaded file based on file type"""
        file_type = file.name.split('.')[-1].lower()
        
        if file_type == 'pdf':
            return self.extract_text_from_pdf(file)
        elif file_type == 'docx':
            return self.extract_text_from_docx(file)
        elif file_type == 'txt':
            return str(file.read(), "utf-8")
        else:
            raise ValueError(f"Unsupported file type: {file_type}")
    
    def identify_document_type(self, text: str) -> str:
        """Identify the type of legal document"""
        text_lower = text.lower()
        
        if any(term in text_lower for term in ["lease", "rental", "tenant", "landlord"]):
            return "Rental Agreement"
        elif any(term in text_lower for term in ["loan", "borrower", "lender", "interest rate", "repayment"]):
            return "Loan Agreement"
        elif any(term in text_lower for term in ["terms of service", "terms and conditions", "user agreement"]):
            return "Terms of Service"
        elif any(term in text_lower for term in ["employment", "employee", "employer", "non-compete"]):
            return "Employment Contract"
        elif any(term in text_lower for term in ["nda", "non-disclosure", "confidentiality"]):
            return "Non-Disclosure Agreement"
        elif any(term in text_lower for term in ["purchase", "sale", "buyer", "seller"]):
            return "Purchase Agreement"
        else:
            return "Legal Document"
    
    def identify_key_sections(self, text: str) -> Dict[str, str]:
        """Identify key sections in the legal document"""
        sections = {}
        lines = text.split('\n')
        current_section = "Introduction"
        section_content = []
        
        # Common legal section headings
        section_headings = [
            "parties", "recitals", "terms", "definitions", "obligations",
            "payment", "confidentiality", "term and termination", "warranties",
            "limitation of liability", "indemnification", "governing law",
            "dispute resolution", "miscellaneous", "notices", "signatures"
        ]
        
        for line in lines:
            line_stripped = line.strip()
            if not line_stripped:
                continue
                
            # Create lowercase version for comparison
            line_lower = line_stripped.lower()
                
            # Check if line is a section heading
            is_heading = False
            for heading in section_headings:
                if heading in line_lower and len(line_stripped.split()) < 8:
                    is_heading = True
                    break
            
            if is_heading:
                if section_content and current_section:
                    sections[current_section] = "\n".join(section_content)
                current_section = line_stripped
                section_content = []
            else:
                section_content.append(line_stripped)
        
        if section_content and current_section:
            sections[current_section] = "\n".join(section_content)
            
        return sections
    
    def simplify_legal_text(self, text: str) -> str:
        """Simplify legal text using rule-based approach and patterns"""
        if not text.strip():
            return ""
            
        # Replace legal terms with simpler explanations
        simplified_text = text
        for term, explanation in self.legal_terms.items():
            simplified_text = re.sub(
                rf'\b{term}\b', 
                f'<span class="legal-term">{term}</span> ({explanation})', 
                simplified_text, 
                flags=re.IGNORECASE
            )
        
        # Identify and simplify common legal patterns
        patterns = [
            (r'notwithstanding anything to the contrary contained herein', 'despite anything else in this document'),
            (r'in the event that', 'if'),
            (r'for the purpose of', 'to'),
            (r'prior to', 'before'),
            (r'subsequent to', 'after'),
            (r'pursuant to', 'under'),
            (r'without limiting the generality of the foregoing', 'including but not limited to'),
            (r'set forth herein', 'described in this document'),
            (r'shall be deemed to be', 'will be considered'),
            (r'is hereby granted', 'is given'),
        ]
        
        for pattern, replacement in patterns:
            simplified_text = re.sub(pattern, replacement, simplified_text, flags=re.IGNORECASE)
        
        # Break down long sentences
        sentences = re.split(r'(?<=[.!?]) +', simplified_text)
        simplified_sentences = []
        
        for sentence in sentences:
            if len(sentence.split()) > 25:  # Long sentence
                # Simple approach to break down long sentences
                clauses = re.split(r', |; |: ', sentence)
                if len(clauses) > 1:
                    simplified_sentences.extend(clauses)
                else:
                    simplified_sentences.append(sentence)
            else:
                simplified_sentences.append(sentence)
        
        return ". ".join(simplified_sentences)
    
    def identify_risks(self, text: str) -> List[Dict[str, Any]]:
        """Identify potential risks in the legal document"""
        risks = []
        text_lower = text.lower()
        
        # Risk patterns to look for
        risk_patterns = [
            (r'indemnify|hold harmless', "You might be responsible for paying for damages or losses", "high"),
            (r'liability.*limit|limit.*liability', "There may be limits on how much you can claim if something goes wrong", "medium"),
            (r'confidentiality|non-disclosure', "You may be required to keep information secret", "medium"),
            (r'termination.*without cause|termination.*at will', "The agreement might be ended without a specific reason", "medium"),
            (r'arbitration.*dispute|dispute.*arbitration', "You might not be able to sue in court and must use arbitration instead", "medium"),
            (r'governing law.*jurisdiction', "Disputes might be handled in a location that's not convenient for you", "low"),
            (r'automatic renewal|evergreen', "The agreement might renew automatically unless you cancel it", "medium"),
            (r'non-compete|non-solicit', "You might be restricted from working with competitors or clients", "high"),
            (r'liquidated damages', "You might have to pay a predetermined amount if you breach the agreement", "high"),
            (r'assignment.*without consent', "The other party might transfer the agreement without your permission", "medium"),
        ]
        
        for pattern, description, risk_level in risk_patterns:
            if re.search(pattern, text_lower):
                risks.append({
                    "description": description,
                    "level": risk_level,
                    "examples": self.find_example_clauses(text, pattern)
                })
        
        return risks
    
    def find_example_clauses(self, text: str, pattern: str) -> List[str]:
        """Find example clauses that match a pattern"""
        examples = []
        sentences = re.split(r'(?<=[.!?]) +', text)
        
        for sentence in sentences:
            if re.search(pattern, sentence, re.IGNORECASE):
                examples.append(sentence.strip())
                if len(examples) >= 3:  # Limit to 3 examples
                    break
        
        return examples
    
    def generate_summary(self, document_type: str, sections: Dict[str, str]) -> str:
        """Generate a summary of the document"""
        summary = f"This is a {document_type} that includes the following key sections:\n\n"
        
        for section_name, section_content in sections.items():
            summary += f"• {section_name}: {textwrap.shorten(section_content, width=150, placeholder='...')}\n"
        
        summary += "\nKey things to pay attention to:\n"
        
        if document_type == "Rental Agreement":
            summary += "- Duration of the lease and renewal terms\n"
            summary += "- Rent amount, due date, and late fees\n"
            summary += "- Security deposit details and return conditions\n"
            summary += "- Maintenance responsibilities\n"
            summary += "- Rules about pets, guests, and property use\n"
        
        elif document_type == "Loan Agreement":
            summary += "- Principal amount and interest rate\n"
            summary += "- Repayment schedule and due dates\n"
            summary += "- Prepayment penalties or options\n"
            summary += "- Default conditions and consequences\n"
            summary += "- Collateral requirements if any\n"
        
        elif document_type == "Terms of Service":
            summary += "- Your rights and responsibilities as a user\n"
            summary += "- How your data is collected and used\n"
            summary += "- Content ownership and intellectual property\n"
            summary += "- Limitations of the service provider's liability\n"
            summary += "- Dispute resolution process\n"
        
        return summary
    
    def process_document(self, file) -> Dict[str, Any]:
        """Process the uploaded document and return analysis results"""
        try:
            # Extract text from the file
            text = self.extract_text_from_file(file)
            
            # Identify document type
            doc_type = self.identify_document_type(text)
            
            # Identify key sections
            sections = self.identify_key_sections(text)
            
            # Simplify the entire document
            simplified_text = self.simplify_legal_text(text)
            
            # Identify risks
            risks = self.identify_risks(text)
            
            # Generate summary
            summary = self.generate_summary(doc_type, sections)
            
            return {
                "success": True,
                "original_text": text,
                "simplified_text": simplified_text,
                "document_type": doc_type,
                "sections": sections,
                "risks": risks,
                "summary": summary,
                "file_name": file.name
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }

def create_download_link(content, filename, text):
    """Generate a download link for the content"""
    b64 = base64.b64encode(content.encode()).decode()
    href = f'<a href="data:file/txt;base64,{b64}" download="{filename}" class="icon-button">📥 {text}</a>'
    return href

def main():
    """Main application function"""
    st.markdown('<h1 class="main-header">⚖️ Legal Document Simplifier</h1>', unsafe_allow_html=True)
    st.markdown("""
    <div style='text-align: center; margin-bottom: 2rem; color: #64748B;'>
        Upload your legal document to get a simplified explanation of its terms and conditions.
        Identify potential risks and understand what you're agreeing to.
    </div>
    """, unsafe_allow_html=True)
    
    # Initialize the simplifier
    simplifier = LegalDocumentSimplifier()
    
    # File upload section
    uploaded_file = st.file_uploader(
        "Choose a legal document (PDF, DOCX, or TXT)",
        type=["pdf", "docx", "txt"],
        help="Upload rental agreements, loan contracts, terms of service, etc."
    )
    
    if uploaded_file is not None:
        with st.spinner("Analyzing your document..."):
            result = simplifier.process_document(uploaded_file)
        
        if result["success"]:
            # Display document information in a compact way
            col1, col2, col3, col4 = st.columns(4)
            with col1:
                st.metric("Document Type", result["document_type"])
            with col2:
                st.metric("Sections", len(result["sections"]))
            with col3:
                st.metric("Risks", len(result["risks"]))
            with col4:
                st.metric("File", result["file_name"])
            
            st.markdown("---")
            
            # Document Summary in a compact card
            st.markdown('<div class="sub-header">📋 Document Summary</div>', unsafe_allow_html=True)
            with st.container():
                st.markdown('<div class="compact-section">', unsafe_allow_html=True)
                
                # Summary items as compact cards
                summary_items = result["summary"].split('\n')
                for item in summary_items:
                    if item.strip() and not item.strip().startswith('This is a'):
                        st.markdown(f'<div class="summary-item">{item.strip()}</div>', unsafe_allow_html=True)
                
                st.markdown('</div>', unsafe_allow_html=True)
            
            # Display risks in a compact way
            if result["risks"]:
                st.markdown('<div class="sub-header">⚠️ Potential Risks</div>', unsafe_allow_html=True)
                
                risk_col1, risk_col2 = st.columns(2)
                
                with risk_col1:
                    for risk in result["risks"]:
                        if risk["level"] in ["high", "medium"]:
                            risk_class = f"risk-{risk['level']}"
                            tag_class = f"tag tag-{risk['level']}"
                            
                            st.markdown(f'<div class="section-card {risk_class}">', unsafe_allow_html=True)
                            st.markdown(f'<span class="{tag_class}">{risk["level"].upper()}</span>', unsafe_allow_html=True)
                            st.markdown(f"**{risk['description']}**")
                            
                            if risk["examples"]:
                                with st.expander("View relevant clauses"):
                                    for example in risk["examples"]:
                                        st.markdown(f'<div style="font-size: 0.9em; color: #64748B; margin: 0.5rem 0;">{example}</div>', unsafe_allow_html=True)
                            st.markdown('</div>', unsafe_allow_html=True)
                
                with risk_col2:
                    for risk in result["risks"]:
                        if risk["level"] == "low":
                            risk_class = f"risk-{risk['level']}"
                            tag_class = f"tag tag-{risk['level']}"
                            
                            st.markdown(f'<div class="section-card {risk_class}">', unsafe_allow_html=True)
                            st.markdown(f'<span class="{tag_class}">{risk["level"].upper()}</span>', unsafe_allow_html=True)
                            st.markdown(f"**{risk['description']}**")
                            
                            if risk["examples"]:
                                with st.expander("View relevant clauses"):
                                    for example in risk["examples"]:
                                        st.markdown(f'<div style="font-size: 0.9em; color: #64748B; margin: 0.5rem 0;">{example}</div>', unsafe_allow_html=True)
                            st.markdown('</div>', unsafe_allow_html=True)
            
            # Simplified explanation in an accordion style
            st.markdown('<div class="sub-header">📝 Simplified Explanation</div>', unsafe_allow_html=True)
            
            # Show section by section if we have sections
            if result["sections"]:
                # Create tabs for each section
                tab_list = list(result["sections"].keys())[:6]  # Limit to first 6 sections for compactness
                tabs = st.tabs(tab_list)
                
                for i, (section_name, section_content) in enumerate(result["sections"].items()):
                    if i < len(tabs):  # Only show first 6 sections in tabs
                        with tabs[i]:
                            st.markdown("**Original Text:**")
                            st.markdown(f'<div style="font-size: 0.9em; background-color: #F8FAFC; padding: 1rem; border-radius: 0.5rem; margin: 0.5rem 0;">{section_content[:500]}...</div>', unsafe_allow_html=True)
                            
                            st.markdown("**Simplified Explanation:**")
                            simplified_section = simplifier.simplify_legal_text(section_content)
                            st.markdown(f'<div style="font-size: 0.95em; background-color: #F0FDF4; padding: 1rem; border-radius: 0.5rem; margin: 0.5rem 0;">{simplified_section[:600]}...</div>', unsafe_allow_html=True)
                            
                            if st.button("View Full Section", key=f"btn_{i}"):
                                st.markdown("**Full Simplified Explanation:**")
                                st.markdown(f'<div style="font-size: 0.95em; background-color: #F0FDF4; padding: 1rem; border-radius: 0.5rem; margin: 0.5rem 0;">{simplified_section}</div>', unsafe_allow_html=True)
            else:
                # Fallback if sections weren't properly identified
                st.markdown("**Simplified Explanation:**")
                st.markdown(f'<div style="font-size: 0.95em; background-color: #F0FDF4; padding: 1rem; border-radius: 0.5rem; margin: 0.5rem 0;">{result["simplified_text"][:1000]}...</div>', unsafe_allow_html=True)
            
            # Download options in a stylish card
            st.markdown("---")
            st.markdown('<div class="sub-header">💾 Download Results</div>', unsafe_allow_html=True)
            
            # Create a simplified report
            report = f"Legal Document Analysis Report\n"
            report += f"Generated on: {datetime.now().strftime('%Y-%m-%d %H:%M')}\n"
            report += f"Document: {result['file_name']}\n"
            report += f"Type: {result['document_type']}\n\n"
            report += "SUMMARY:\n"
            report += result["summary"] + "\n\n"
            
            report += "RISKS IDENTIFIED:\n"
            for risk in result["risks"]:
                report += f"- {risk['description']} (Risk level: {risk['level'].upper()})\n"
            report += "\n"
            
            report += "SIMPLIFIED EXPLANATION:\n"
            report += result["simplified_text"]
            
            # Create a stylish download card
            st.markdown('<div class="download-card">', unsafe_allow_html=True)
            st.markdown("### 📄 Download Your Analysis")
            st.markdown("Get a complete report of the document analysis with all simplified explanations and risk assessments.")
            
            dl_col1, dl_col2, dl_col3 = st.columns(3)
            
            with dl_col1:
                st.markdown(create_download_link(report, "legal_analysis_report.txt", "Full Report"), unsafe_allow_html=True)
            
            with dl_col2:
                # Summary only download
                summary_report = f"Document Summary - {result['file_name']}\n\n"
                summary_report += result["summary"]
                st.markdown(create_download_link(summary_report, "document_summary.txt", "Summary Only"), unsafe_allow_html=True)
            
            with dl_col3:
                # Risks only download
                risks_report = f"Risk Assessment - {result['file_name']}\n\n"
                for risk in result["risks"]:
                    risks_report += f"- {risk['description']} (Risk level: {risk['level'].upper()})\n"
                st.markdown(create_download_link(risks_report, "risk_assessment.txt", "Risks Only"), unsafe_allow_html=True)
            
            st.markdown('</div>', unsafe_allow_html=True)
            
        else:
            st.error(f"Error processing document: {result['error']}")
    
    else:
        # Show instructions when no file is uploaded
        st.markdown("---")
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("### How it works:")
            st.markdown("""
            <div class="section-card">
            1. 📤 Upload a legal document (PDF, DOCX, or TXT)<br>
            2. 🔍 Our AI analyzes the document structure and content<br>
            3. ⚠️ We identify key sections and potential risks<br>
            4. 📝 You get a simplified explanation in plain language
            </div>
            """, unsafe_allow_html=True)
            
            st.markdown("### Supported documents:")
            st.markdown("""
            <div class="section-card">
            - 📃 Rental and lease agreements<br>
            - 💰 Loan contracts and agreements<br>
            - 🌐 Terms of service<br>
            - 👔 Employment contracts<br>
            - 🔒 Non-disclosure agreements (NDAs)<br>
            - 🛒 Purchase agreements
            </div>
            """, unsafe_allow_html=True)
        
        with col2:
            st.markdown("### Benefits:")
            st.markdown("""
            <div class="section-card">
            - ✅ Understand what you're signing<br>
            - ✅ Identify potential risks<br>
            - ✅ Save time on legal research<br>
            - ✅ Make informed decisions<br>
            - ✅ No legal jargon confusion
            </div>
            """, unsafe_allow_html=True)
            
            st.markdown("### Disclaimer:")
            st.markdown("""
            <div class="section-card disclaimer-card">
            *This tool provides simplified explanations for informational purposes only 
            and does not constitute legal advice. For important legal matters, 
            consult with a qualified attorney.*
            </div>
            """, unsafe_allow_html=True)

if __name__ == "__main__":
    main()