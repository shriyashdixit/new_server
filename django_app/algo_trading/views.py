from django.shortcuts import render, redirect
from .forms import CSVImportForm
from .models import HistoricalData
import csv
from django.contrib.auth.decorators import login_required
from .stratergies import Stratergy


@login_required
def import_csv(request):
    if request.method == 'POST':
        form = CSVImportForm(request.POST, request.FILES)
        if form.is_valid():
            csv_file = request.FILES['csv_file'].read().decode('utf-8').splitlines()
            csv_reader = csv.DictReader(csv_file)

            for row in csv_reader:
                HistoricalData.objects.create(
                    date=row['date'],
                    open=row['open'],
                    high=row['high'],
                    low=row['low'],
                    close=row['close'],
                )

            return render(request, 'success.html')
    else:
        form = CSVImportForm()

    return render(request, 'import.html', {'form': form})


@login_required
def success_page(request):
    return render(request, 'success.html')


def prediction_model(request):
    historical_data = HistoricalData.objects.all()
    data_1 = {}

    date_array = []
    open_array = []
    high_array = []
    low_array = []
    close_array = []
    for elem in historical_data:
        date_array.append(elem.date)
        open_array.append(elem.open)
        high_array.append(elem.high)
        low_array.append(elem.low)
        close_array.append(elem.close)

    data_1 = {
        'date': date_array,
        'open': open_array,
        'high': high_array,
        'low': low_array,
        'close': close_array,
    }
    context = []
    context = Stratergy(historical_data=data_1).stratergy_1()
    return render(request, 'output.html', {'context': context})
