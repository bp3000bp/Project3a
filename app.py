from flask import Flask, render_template, request, redirect, url_for
import requests
import pygal
from pygal.style import DarkStyle
import csv
from datetime import datetime

app = Flask(__name__)
api_key = "1M1XTV42PNTYEAEU" 

def fetch_stock_data(symbol, function="TIME_SERIES_DAILY"):
    url = f"https://www.alphavantage.co/query"
    params = {
        "function": function,
        "symbol": symbol,
        "apikey": api_key,
        "outputsize": "full",
    }
    response = requests.get(url, params=params)
    if response.status_code == 200:
        data = response.json()
        if "Time Series (Daily)" in data:
            return data
    return None

def parse_stock_data(data):
    daily_data = data.get("Time Series (Daily)", {})
    parsed_data = []
    for date, values in daily_data.items():
        parsed_data.append({
            "date": date,
            "close": float(values["4. close"]),
        })
    return parsed_data

def filter_by_date_range(parsed_data, start_date, end_date):
    start = datetime.strptime(start_date, "%Y-%m-%d")
    end = datetime.strptime(end_date, "%Y-%m-%d")
    return [entry for entry in parsed_data if start <= datetime.strptime(entry["date"], "%Y-%m-%d") <= end]

def generate_chart_html(filtered_data, stock_symbol, chart_type):
    filtered_data = sorted(filtered_data, key=lambda x: datetime.strptime(x["date"], "%Y-%m-%d"))
    dates = [entry["date"] for entry in filtered_data]
    closing_prices = [entry["close"] for entry in filtered_data]

    if chart_type == "line":
        chart = pygal.Line(style=DarkStyle)
        chart.x_labels = dates
        chart.add('Close Price', closing_prices)
    elif chart_type == "bar":
        chart = pygal.Bar(style=DarkStyle)
        chart.x_labels = dates
        chart.add('Close Price', closing_prices)

    return chart.render_data_uri()  # Returns data URI for embedding in HTML

def load_stock_symbols():
    with open('stocks.csv', newline='') as csvfile:
        reader = csv.reader(csvfile)
        return [row[0] for row in reader]

@app.route("/", methods=["GET", "POST"])
def index():
    symbols = load_stock_symbols()
    chart_data = None

    if request.method == "POST":
        symbol = request.form.get("symbol")
        chart_type = request.form.get("chart_type")
        start_date = request.form.get("start_date")
        end_date = request.form.get("end_date")

        stock_data = fetch_stock_data(symbol)
        if stock_data:
            parsed_data = parse_stock_data(stock_data)
            filtered_data = filter_by_date_range(parsed_data, start_date, end_date)
            if filtered_data:
                chart_data = generate_chart_html(filtered_data, symbol, chart_type)
            else:
                chart_data = "No data found for the specified date range."
        else:
            chart_data = "Invalid ticker symbol or no data found."

    return render_template("index.html", symbols=symbols, chart_data=chart_data)

if __name__ == "__main__":
    app.run(host="0.0.0.0")