from flask import Flask, render_template, request, redirect, url_for
import requests
from bs4 import BeautifulSoup
import pandas as pd
import os

app = Flask(__name__)

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        mood = request.form['mood']
        constipated = request.form['constipated']
        gastric_acid = request.form['gastric_acid']
        sleep_time = request.form['sleep_time']
        wake_time = request.form['wake_time']
        location = request.form['location']
        allergic_reaction = request.form['allergic_reaction']

        user_input = {
            "Mood": mood,
            "Constipated": constipated,
            "Gastric Acid": gastric_acid,
            "Sleep Time": sleep_time,
            "Wake Time": wake_time,
            "Location": location,
            "Allergic Reaction": allergic_reaction
        }

        moon_phase_url = "https://www.timeanddate.com/moon/india/ajmer"
        moon_data_url = "https://www.timeanddate.com/moon/india/ajmer"

        try:
            moon_phase_data = scrape_moon_phase_data(moon_phase_url)
            moon_data = scrape_moon_data(moon_data_url)

            combined_data = {
                **moon_data,
                "Moon Percentage": moon_phase_data[0],
                "Moon Description": moon_phase_data[1],
                **user_input
            }

            combined_csv_file = "combined_data.csv"

            if not os.path.exists(combined_csv_file):
                df = pd.DataFrame([combined_data])
                df.to_csv(combined_csv_file, index=False)
            else:
                existing_data = pd.read_csv(combined_csv_file)
                df = pd.concat([existing_data, pd.DataFrame([combined_data])], ignore_index=True)
                df.to_csv(combined_csv_file, index=False)

            return redirect(url_for('show_data'))
        except Exception as e:
            return f"An error occurred: {str(e)}"

    return render_template('index.html')

@app.route('/show_data')
def show_data():
    data = pd.read_csv('combined_data.csv')
    return render_template('show_data.html', data=data)

def scrape_moon_phase_data(url):
    response = requests.get(url)
    response.raise_for_status()

    soup = BeautifulSoup(response.text, 'html.parser')
    qlook_div = soup.find("div", {"id": "qlook"})

    if not qlook_div:
        raise Exception("Element with id 'qlook' not found on the webpage.")

    moon_percent = qlook_div.find("span", {"id": "cur-moon-percent"}).get_text()
    moon_description = qlook_div.find("a", title=True).get_text()

    return moon_percent, moon_description

def scrape_moon_data(url):
    response = requests.get(url)
    response.raise_for_status()

    soup = BeautifulSoup(response.content, 'html.parser')
    section = soup.find("section", class_="bk-focus")

    data = {}
    for row in section.find_all("tr"):
        header = row.th.get_text(strip=True)
        value = row.td.get_text(strip=True)
        data[header] = value

    return data

if __name__ == "__main__":
    app.run(debug=True)
