from io import BytesIO

from django.http import FileResponse

from openpyxl import Workbook
from openpyxl.styles import Font


def generate_attendance_excel(
    report,
    start_date,
    end_date,
):
    workbook = Workbook()

    worksheet = workbook.active
    worksheet.title = "Attendance"

    worksheet["A1"] = "Attendance Report"
    worksheet["A1"].font = Font(
        bold=True,
        size=16,
    )

    worksheet["A2"] = "Period"
    worksheet["B2"] = (
        f"{start_date} - {end_date}"
    )

    worksheet["A4"] = "Status"
    worksheet["B4"] = "Count"

    worksheet["A5"] = "Present"
    worksheet["B5"] = report["present"]

    worksheet["A6"] = "Late"
    worksheet["B6"] = report["late"]

    worksheet["A7"] = "Absent"
    worksheet["B7"] = report["absent"]

    worksheet["A8"] = "Excused"
    worksheet["B8"] = report["excused"]

    worksheet["A9"] = "Total"
    worksheet["B9"] = report["total_records"]

    worksheet["A11"] = "Attendance Rate"
    worksheet["B11"] = (
        report["attendance_percentage"]
    )

    buffer = BytesIO()

    workbook.save(buffer)

    buffer.seek(0)

    return FileResponse(
        buffer,
        as_attachment=True,
        filename=(
            f"attendance_report_"
            f"{start_date}_{end_date}.xlsx"
        ),
        content_type=(
            "application/vnd.openxmlformats-officedocument."
            "spreadsheetml.sheet"
        ),
    )