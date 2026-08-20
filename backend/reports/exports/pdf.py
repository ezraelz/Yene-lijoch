from io import BytesIO
from django.http import FileResponse
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.platypus import (
    SimpleDocTemplate,
    Paragraph,
    Spacer,
    Table,
    TableStyle,
)


def generate_attendance_pdf(
    report,
    start_date,
    end_date,
):
    buffer = BytesIO()

    document = SimpleDocTemplate(
        buffer,
        pagesize=A4,
        title="Attendance Report",
    )

    styles = getSampleStyleSheet()

    elements = []

    elements.append(
        Paragraph(
            "Attendance Report",
            styles["Title"],
        )
    )

    elements.append(
        Paragraph(
            f"{start_date} - {end_date}",
            styles["Normal"],
        )
    )

    elements.append(Spacer(1, 20))

    data = [
        ["Status", "Count"],
        ["Present", report["present"]],
        ["Late", report["late"]],
        ["Absent", report["absent"]],
        ["Excused", report["excused"]],
        ["Total", report["total_records"]],
    ]

    table = Table(data)

    table.setStyle(
        TableStyle([
            ("BACKGROUND", (0, 0), (-1, 0), colors.grey),
            ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
            ("GRID", (0, 0), (-1, -1), 1, colors.black),
            ("PADDING", (0, 0), (-1, -1), 6),
        ])
    )

    elements.append(table)

    elements.append(Spacer(1, 20))

    elements.append(
        Paragraph(
            f"Attendance Rate: "
            f"{report['attendance_percentage']}%",
            styles["Heading2"],
        )
    )

    document.build(elements)

    buffer.seek(0)

    return FileResponse(
        buffer,
        as_attachment=True,
        filename=(
            f"attendance_report_"
            f"{start_date}_{end_date}.pdf"
        ),
        content_type="application/pdf",
    )

