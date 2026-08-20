from datetime import date, timedelta


def get_report_period(period, start_date=None, end_date=None):
    today = date.today()

    if period == "week":
        start = today - timedelta(days=today.weekday())
        end = start + timedelta(days=6)

    elif period == "month":
        start = today.replace(day=1)

        if today.month == 12:
            next_month = today.replace(
                year=today.year + 1,
                month=1,
                day=1,
            )
        else:
            next_month = today.replace(
                month=today.month + 1,
                day=1,
            )

        end = next_month - timedelta(days=1)

    elif period == "quarter":
        quarter = ((today.month - 1) // 3) + 1

        start_month = (quarter - 1) * 3 + 1
        start = today.replace(
            month=start_month,
            day=1,
        )

        if start_month == 10:
            next_quarter = today.replace(
                year=today.year + 1,
                month=1,
                day=1,
            )
        else:
            next_quarter = today.replace(
                month=start_month + 3,
                day=1,
            )

        end = next_quarter - timedelta(days=1)

    elif period == "year":
        start = today.replace(
            month=1,
            day=1,
        )

        end = today.replace(
            month=12,
            day=31,
        )

    elif period == "custom":
        if not start_date or not end_date:
            raise ValueError(
                "Custom reports require start_date and end_date."
            )

        start = start_date
        end = end_date

    else:
        raise ValueError(
            "Invalid report period."
        )

    return start, end