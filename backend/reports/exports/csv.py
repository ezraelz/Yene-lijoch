import csv

from django.http import HttpResponse


def generate_attendance_csv(
    report,
    start_date,
    end_date,
):
    response = HttpResponse(
        content_type="text/csv"
    )

    response[
        "Content-Disposition"
    ] = (
        "attachment; "
        f'filename="attendance_report_'
        f'{start_date}_{end_date}.csv"'
    )

    writer = csv.writer(response)

    writer.writerow([
        "Status",
        "Count",
    ])

    writer.writerow([
        "Present",
        report["present"],
    ])

    writer.writerow([
        "Late",
        report["late"],
    ])

    writer.writerow([
        "Absent",
        report["absent"],
    ])

    writer.writerow([
        "Excused",
        report["excused"],
    ])

    writer.writerow([
        "Total",
        report["total_records"],
    ])

    writer.writerow([])

    writer.writerow([
        "Attendance Rate",
        report["attendance_percentage"],
    ])

    return response