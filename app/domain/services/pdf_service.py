"""PDF Generation Service for Timetables.

Generates print-optimized PDF exports of timetables using ReportLab.
"""

from io import BytesIO
from datetime import datetime
from sqlalchemy.orm import Session

from reportlab.lib import colors
from reportlab.lib.pagesizes import A4, landscape
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import cm
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, PageBreak
from reportlab.lib.enums import TA_CENTER, TA_LEFT

from app.domain.services.timetable_service import TimetableService
from app.domain.models import Venue

class PDFService:
    """Service for generating timetable PDFs."""
    
    # Department color mapping (light colors for printing)
    DEPT_COLORS = {
        0: colors.HexColor('#cfe2ff'),  # primary
        1: colors.HexColor('#d1e7dd'),  # success
        2: colors.HexColor('#cff4fc'),  # info
        3: colors.HexColor('#fff3cd'),  # warning
        4: colors.HexColor('#f8d7da'),  # danger
        5: colors.HexColor('#e2e3e5'),  # dark
    }
    
    @staticmethod
    def generate_timetable_pdf(db: Session, timetable_id: str, department: str = "All", level: str = "All") -> bytes:
        """Generate a print-optimized PDF of the timetable.
        
        Args:
            db: Database session
            timetable_id: ID of the timetable to export
            department: Department filter
            level: Level filter
            
        Returns:
            PDF file as bytes
        """
        # Get timetable data
        data = TimetableService.get_timetable_grid(db, timetable_id, department, level)
        timetable = data.get('timetable')
        
        if not timetable:
            raise ValueError("Timetable not found")
        
        # Get all venues for legend
        venues = db.query(Venue).order_by(Venue.name).all()
        
        # Create PDF
        buffer = BytesIO()
        doc = SimpleDocTemplate(
            buffer,
            pagesize=landscape(A4),
            rightMargin=1*cm,
            leftMargin=1*cm,
            topMargin=1*cm,
            bottomMargin=1*cm
        )
        
        # Build PDF content
        story = []
        styles = getSampleStyleSheet()
        
        # Title
        title_style = ParagraphStyle(
            'CustomTitle',
            parent=styles['Heading1'],
            fontSize=16,
            textColor=colors.HexColor('#0056b3'),
            alignment=TA_CENTER,
            spaceAfter=6
        )
        story.append(Paragraph("University of Ilorin - Timetable", title_style))
        
        # Subtitle
        subtitle_style = ParagraphStyle(
            'Subtitle',
            parent=styles['Normal'],
            fontSize=10,
            alignment=TA_CENTER,
            textColor=colors.grey,
            spaceAfter=12
        )
        subtitle_text = f"Session: {timetable.academic_session} | Semester: {timetable.semester}"
        if department != "All":
            subtitle_text += f" | Department: {department}"
        if level != "All":
            subtitle_text += f" | Level: {level}"
        story.append(Paragraph(subtitle_text, subtitle_style))
        
        story.append(Spacer(1, 0.3*cm))
        
        # Build table data
        table_data = PDFService._build_table_data(data)
        
        # Create table
        col_widths = [2*cm] + [3.5*cm] * len(data['days'])
        table = Table(table_data, colWidths=col_widths, repeatRows=1)
        
        # Table style
        table.setStyle(TableStyle([
            # Header row
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#0056b3')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, 0), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 9),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 6),
            
            # Time column
            ('BACKGROUND', (0, 1), (0, -1), colors.HexColor('#f8f9fa')),
            ('FONTNAME', (0, 1), (0, -1), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 1), (0, -1), 8),
            ('ALIGN', (0, 1), (0, -1), 'CENTER'),
            
            # All cells
            ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
            ('VALIGN', (0, 0), (-1, -1), 'TOP'),
            ('FONTSIZE', (1, 1), (-1, -1), 7),
            ('LEFTPADDING', (0, 0), (-1, -1), 3),
            ('RIGHTPADDING', (0, 0), (-1, -1), 3),
            ('TOPPADDING', (0, 0), (-1, -1), 3),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 3),
        ]))
        
        story.append(table)
        story.append(Spacer(1, 0.5*cm))
        
        # Venue legend
        legend_style = ParagraphStyle(
            'Legend',
            parent=styles['Normal'],
            fontSize=7,
            textColor=colors.grey
        )
        
        venue_text = "<b>VENUE KEY:</b> "
        if venues:
            venue_items = [f"{v.name} ({v.capacity} capacity)" for v in venues]
            venue_text += " | ".join(venue_items)
        else:
            venue_text += "No venues assigned yet"
        
        story.append(Paragraph(venue_text, legend_style))
        
        # Footer
        footer_style = ParagraphStyle(
            'Footer',
            parent=styles['Normal'],
            fontSize=7,
            textColor=colors.lightgrey,
            alignment=TA_CENTER
        )
        footer_text = f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M')} | University of Ilorin Automated Timetable System"
        story.append(Spacer(1, 0.2*cm))
        story.append(Paragraph(footer_text, footer_style))
        
        # Build PDF
        doc.build(story)
        buffer.seek(0)
        
        return buffer.getvalue()
    
    @staticmethod
    def _build_table_data(data: dict) -> list:
        """Build table data for ReportLab Table.
        
        Args:
            data: Timetable grid data
            
        Returns:
            List of lists for table rows
        """
        # Header row
        header = ['Time'] + data['days']
        table_data = [header]
        
        # Data rows
        for time_slot in data['times']:
            row = [time_slot]
            
            for day in data['days']:
                entries = data['grid'].get(time_slot, {}).get(day, [])
                
                if entries:
                    # Format entries as text
                    cell_lines = []
                    for entry in entries:
                        venue_text = entry.venue.name if entry.venue else "TBA"
                        lecturer_text = entry.course.lecturer.name if entry.course.lecturer else "TBA"
                        
                        cell_text = f"{entry.course.code}\n{venue_text}\n{lecturer_text}"
                        cell_lines.append(cell_text)
                    
                    row.append("\n\n".join(cell_lines))
                else:
                    row.append("")
            
            table_data.append(row)
        
        return table_data
