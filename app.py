from flask import Flask, render_template, jsonify
import feedparser
import urllib.request
import urllib.parse
import json
from datetime import datetime

app = Flask(__name__)

# --- 天気 ---
def get_weather(city="Tokyo", lang="ja"):
    """
    Open-Meteo (無料・APIキー不要) + Geocoding APIで天気取得
    """
    try:
        # Geocoding
        geo_url = f"https://geocoding-api.open-meteo.com/v1/search?name={urllib.parse.quote(city)}&count=1&language={lang}&format=json"
        req = urllib.request.Request(geo_url, headers={"User-Agent": "RaspberryPiDashboard/1.0"})
        with urllib.request.urlopen(req, timeout=5) as r:
            geo = json.loads(r.read())
        result = geo["results"][0]
        lat, lon = result["latitude"], result["longitude"]
        city_name = result.get("name", city)

        # 天気取得
        weather_url = (
            f"https://api.open-meteo.com/v1/forecast"
            f"?latitude={lat}&longitude={lon}"
            f"&current=temperature_2m,relative_humidity_2m,weather_code,wind_speed_10m"
            f"&daily=temperature_2m_max,temperature_2m_min,weather_code"
            f"&timezone=Asia%2FTokyo&forecast_days=3"
        )
        weather_req = urllib.request.Request(weather_url, headers={"User-Agent": "RaspberryPiDashboard/1.0"})
        with urllib.request.urlopen(weather_req, timeout=5) as r:
            weather = json.loads(r.read())

        wmo_desc = {
            0: ("晴れ", "☀️"), 1: ("ほぼ晴れ", "🌤️"), 2: ("一部曇り", "⛅"), 3: ("曇り", "☁️"),
            45: ("霧", "🌫️"), 48: ("霧氷", "🌫️"),
            51: ("霧雨(弱)", "🌦️"), 53: ("霧雨", "🌦️"), 55: ("霧雨(強)", "🌧️"),
            61: ("小雨", "🌧️"), 63: ("雨", "🌧️"), 65: ("大雨", "🌧️"),
            71: ("小雪", "🌨️"), 73: ("雪", "❄️"), 75: ("大雪", "❄️"),
            80: ("にわか雨(弱)", "🌦️"), 81: ("にわか雨", "🌦️"), 82: ("にわか雨(強)", "⛈️"),
            95: ("雷雨", "⛈️"), 96: ("雷雨+霰", "⛈️"), 99: ("雷雨+大霰", "⛈️"),
        }

        cur = weather["current"]
        daily = weather["daily"]
        code = cur["weather_code"]
        desc, icon = wmo_desc.get(code, ("不明", "❓"))

        forecast = []
        for i in range(3):
            d_code = daily["weather_code"][i]
            d_desc, d_icon = wmo_desc.get(d_code, ("不明", "❓"))
            date_str = daily["time"][i]
            dt = datetime.strptime(date_str, "%Y-%m-%d")
            weekdays = ["月", "火", "水", "木", "金", "土", "日"]
            label = "今日" if i == 0 else ("明日" if i == 1 else f"{weekdays[dt.weekday()]}曜")
            forecast.append({
                "label": label,
                "icon": d_icon,
                "desc": d_desc,
                "max": round(daily["temperature_2m_max"][i], 1),
                "min": round(daily["temperature_2m_min"][i], 1),
            })

        return {
            "city": city_name,
            "temp": round(cur["temperature_2m"], 1),
            "humidity": cur["relative_humidity_2m"],
            "wind": round(cur["wind_speed_10m"], 1),
            "desc": desc,
            "icon": icon,
            "forecast": forecast,
        }
    except Exception as e:
        return {"error": str(e)}


# --- ニュース ---
def get_news(feed_url="https://www3.nhk.or.jp/rss/news/cat0.xml", limit=8):
    try:
        feed = feedparser.parse(feed_url)
        items = []
        for entry in feed.entries[:limit]:
            items.append({
                "title": entry.get("title", ""),
                "link": entry.get("link", "#"),
                "published": entry.get("published", ""),
            })
        return {"source": feed.feed.get("title", "ニュース"), "items": items}
    except Exception as e:
        return {"error": str(e)}


# --- ルート ---
@app.route("/")
def index():
    return render_template("index.html")

@app.route("/api/weather")
def api_weather():
    return jsonify(get_weather("Tokyo"))

@app.route("/api/news")
def api_news():
    return jsonify(get_news())

@app.route("/api/time")
def api_time():
    now = datetime.now()
    weekdays = ["月", "火", "水", "木", "金", "土", "日"]
    return jsonify({
        "time": now.strftime("%H:%M:%S"),
        "date": now.strftime("%Y年%-m月%-d日"),
        "weekday": weekdays[now.weekday()] + "曜日",
    })


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
