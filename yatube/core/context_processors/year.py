import datetime


def year(request):
    year = datetime.date.today().year
    return {
        'year': year
    }
