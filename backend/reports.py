from reportlab.lib.pagesizes import letter, A4
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.lib import colors
from datetime import datetime
import os

def generate_pdf_report(df, username):
    """Generate PDF report with experiment summary and insights"""
    filename = f'reports/composting_report_{username}_{datetime.now().strftime("%Y%m%d_%H%M%S")}.pdf'
    os.makedirs('reports', exist_ok=True)
    
    doc = SimpleDocTemplate(filename, pagesize=A4)
    styles = getSampleStyleSheet()
    story = []
    
    # Title
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontSize=24,
        spaceAfter=30,
        alignment=1  # Center alignment
    )
    story.append(Paragraph("Composting Efficiency Analysis Report", title_style))
    story.append(Spacer(1, 20))
    
    # Report Info
    info_style = styles['Normal']
    story.append(Paragraph(f"<b>Generated for:</b> {username}", info_style))
    story.append(Paragraph(f"<b>Generated on:</b> {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}", info_style))
    story.append(Paragraph(f"<b>Total Experiments:</b> {len(df)}", info_style))
    story.append(Spacer(1, 20))
    
    # Summary Statistics
    story.append(Paragraph("Summary Statistics", styles['Heading2']))
    
    summary_data = [
        ['Metric', 'Value'],
        ['Average Efficiency Score', f"{df['efficiency_score'].mean():.2f}"],
        ['Average Decomposition Time', f"{df['decomposition_days'].mean():.1f} days"],
        ['Best Performing Bin', df.loc[df['efficiency_score'].idxmax(), 'bin_id']],
        ['Highest Efficiency Score', f"{df['efficiency_score'].max():.2f}"],
        ['Average Final NPK Sum', f"{(df['final_n'] + df['final_p'] + df['final_k']).mean():.2f}"]
    ]
    
    summary_table = Table(summary_data)
    summary_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 14),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
        ('GRID', (0, 0), (-1, -1), 1, colors.black)
    ]))
    
    story.append(summary_table)
    story.append(Spacer(1, 20))
    
    # Top 3 Performing Bins
    story.append(Paragraph("Top 3 Performing Bins", styles['Heading2']))
    
    top_bins = df.nlargest(3, 'efficiency_score')
    top_data = [['Bin ID', 'Efficiency Score', 'Decomposition Days', 'C/N Ratio', 'Moisture %']]
    
    for _, row in top_bins.iterrows():
        top_data.append([
            row['bin_id'],
            f"{row['efficiency_score']:.2f}",
            f"{row['decomposition_days']}",
            f"{row['cn_ratio']:.1f}",
            f"{row['moisture_level']:.1f}"
        ])
    
    top_table = Table(top_data)
    top_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.green),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 12),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('BACKGROUND', (0, 1), (-1, -1), colors.lightgreen),
        ('GRID', (0, 0), (-1, -1), 1, colors.black)
    ]))
    
    story.append(top_table)
    story.append(Spacer(1, 20))
    
    # Best Practices Recommendations
    story.append(Paragraph("Optimal Configuration (Based on Top Performers)", styles['Heading2']))
    
    # Calculate optimal values from top 3
    optimal_cn = top_bins['cn_ratio'].mean()
    optimal_moisture = top_bins['moisture_level'].mean()
    optimal_aeration = top_bins['aeration_frequency'].mean()
    optimal_temp = top_bins['daily_temperature'].mean()
    
    recommendations = [
        f"• Maintain C/N ratio around {optimal_cn:.1f}",
        f"• Keep moisture level at {optimal_moisture:.1f}%",
        f"• Aerate approximately {optimal_aeration:.0f} times per week",
        f"• Target temperature around {optimal_temp:.1f}°C",
        f"• Monitor odor levels and keep below 3",
        f"• Expected decomposition time: {top_bins['decomposition_days'].mean():.0f} days"
    ]
    
    for rec in recommendations:
        story.append(Paragraph(rec, styles['Normal']))
    
    story.append(Spacer(1, 20))
    
    # All Experiments Data
    story.append(Paragraph("All Experiments Data", styles['Heading2']))
    
    # Create data table
    table_data = [['Bin ID', 'C/N', 'Moisture%', 'Temp°C', 'Days', 'Score']]
    
    for _, row in df.iterrows():
        table_data.append([
            row['bin_id'],
            f"{row['cn_ratio']:.1f}",
            f"{row['moisture_level']:.1f}",
            f"{row['daily_temperature']:.1f}",
            f"{row['decomposition_days']}",
            f"{row['efficiency_score']:.1f}"
        ])
    
    data_table = Table(table_data)
    data_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.blue),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 10),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('BACKGROUND', (0, 1), (-1, -1), colors.lightblue),
        ('GRID', (0, 0), (-1, -1), 1, colors.black),
        ('FONTSIZE', (0, 1), (-1, -1), 8)
    ]))
    
    story.append(data_table)
    
    # Build PDF
    doc.build(story)
    return filename
