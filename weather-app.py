import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext
import requests
from datetime import datetime, timedelta
import json
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure
import matplotlib.dates as mdates
from PIL import Image, ImageTk
import io
import time

class WeatherApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Weather Forecast App")
        self.root.geometry("900x700")
        self.root.configure(bg="#f0f0f0")
        
        # API key for OpenWeatherMap (you need to get your own free key from https://openweathermap.org/api)
        self.api_key = "replace this with openwathermap API key"  # Replace with your actual API key
        
        # Default city
        self.current_city = "London"
        
        # Units (metric for Celsius, imperial for Fahrenheit)
        self.units = "metric"
        
        # Create GUI
        self.create_widgets()
        
        # Load last searched city if available
        self.load_last_city()
        
        # Get initial weather data
        self.get_weather_data()
    
    def create_widgets(self):
        # Main frame
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Configure grid weights
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(1, weight=1)
        
        # Title
        title_label = ttk.Label(main_frame, text="Weather Forecast", font=("Arial", 16, "bold"))
        title_label.grid(row=0, column=0, columnspan=3, pady=10)
        
        # Search frame
        search_frame = ttk.Frame(main_frame)
        search_frame.grid(row=1, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=5)
        search_frame.columnconfigure(1, weight=1)
        
        ttk.Label(search_frame, text="City:").grid(row=0, column=0, padx=5)
        self.city_var = tk.StringVar()
        self.city_entry = ttk.Entry(search_frame, textvariable=self.city_var, width=20)
        self.city_entry.grid(row=0, column=1, padx=5, sticky=(tk.W, tk.E))
        self.city_entry.bind('<Return>', lambda e: self.get_weather_data())
        
        ttk.Button(search_frame, text="Search", command=self.get_weather_data).grid(row=0, column=2, padx=5)
        
        # Units frame
        units_frame = ttk.Frame(main_frame)
        units_frame.grid(row=2, column=0, columnspan=3, pady=5)
        
        ttk.Label(units_frame, text="Units:").grid(row=0, column=0, padx=5)
        self.unit_var = tk.StringVar(value="metric")
        ttk.Radiobutton(units_frame, text="Celsius", variable=self.unit_var, 
                       value="metric", command=self.change_units).grid(row=0, column=1, padx=5)
        ttk.Radiobutton(units_frame, text="Fahrenheit", variable=self.unit_var, 
                       value="imperial", command=self.change_units).grid(row=0, column=2, padx=5)
        
        # Current weather frame
        current_frame = ttk.LabelFrame(main_frame, text="Current Weather", padding="10")
        current_frame.grid(row=3, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=10)
        current_frame.columnconfigure(1, weight=1)
        
        # Current weather elements
        self.location_label = ttk.Label(current_frame, text="", font=("Arial", 14, "bold"))
        self.location_label.grid(row=0, column=0, columnspan=2, pady=5)
        
        self.temp_label = ttk.Label(current_frame, text="", font=("Arial", 24))
        self.temp_label.grid(row=1, column=0, columnspan=2, pady=5)
        
        self.weather_icon_label = ttk.Label(current_frame, text="")
        self.weather_icon_label.grid(row=2, column=0, rowspan=3, padx=10)
        
        self.desc_label = ttk.Label(current_frame, text="", font=("Arial", 12))
        self.desc_label.grid(row=2, column=1, sticky=tk.W)
        
        self.feels_like_label = ttk.Label(current_frame, text="")
        self.feels_like_label.grid(row=3, column=1, sticky=tk.W)
        
        self.humidity_label = ttk.Label(current_frame, text="")
        self.humidity_label.grid(row=4, column=1, sticky=tk.W)
        
        self.wind_label = ttk.Label(current_frame, text="")
        self.wind_label.grid(row=5, column=1, sticky=tk.W)
        
        self.pressure_label = ttk.Label(current_frame, text="")
        self.pressure_label.grid(row=6, column=1, sticky=tk.W)
        
        self.visibility_label = ttk.Label(current_frame, text="")
        self.visibility_label.grid(row=7, column=1, sticky=tk.W)
        
        # Forecast frame
        forecast_frame = ttk.LabelFrame(main_frame, text="5-Day Forecast", padding="10")
        forecast_frame.grid(row=4, column=0, columnspan=3, sticky=(tk.W, tk.E, tk.N, tk.S), pady=10)
        forecast_frame.columnconfigure(0, weight=1)
        forecast_frame.rowconfigure(0, weight=1)
        
        # Create a canvas and scrollbar for the forecast
        self.canvas = tk.Canvas(forecast_frame, height=200)
        self.scrollbar = ttk.Scrollbar(forecast_frame, orient="horizontal", command=self.canvas.xview)
        self.scrollable_frame = ttk.Frame(self.canvas)
        
        self.scrollable_frame.bind(
            "<Configure>",
            lambda e: self.canvas.configure(scrollregion=self.canvas.bbox("all"))
        )
        
        self.canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw")
        self.canvas.configure(xscrollcommand=self.scrollbar.set)
        
        self.canvas.grid(row=0, column=0, sticky="nsew")
        self.scrollbar.grid(row=1, column=0, sticky="ew")
        
        # Chart frame
        chart_frame = ttk.LabelFrame(main_frame, text="Temperature Forecast", padding="10")
        chart_frame.grid(row=5, column=0, columnspan=3, sticky=(tk.W, tk.E, tk.N, tk.S), pady=10)
        chart_frame.columnconfigure(0, weight=1)
        chart_frame.rowconfigure(0, weight=1)
        
        # Create matplotlib figure
        self.fig = Figure(figsize=(8, 4), dpi=100)
        self.ax = self.fig.add_subplot(111)
        self.canvas_chart = FigureCanvasTkAgg(self.fig, chart_frame)
        self.canvas_chart.get_tk_widget().grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Status bar
        self.status_var = tk.StringVar()
        self.status_var.set("Ready")
        status_bar = ttk.Label(main_frame, textvariable=self.status_var, relief=tk.SUNKEN, anchor=tk.W)
        status_bar.grid(row=6, column=0, columnspan=3, sticky=(tk.W, tk.E))
        
    def change_units(self):
        self.units = self.unit_var.get()
        self.get_weather_data()
    
    def get_weather_data(self):
        city = self.city_var.get().strip()
        if not city:
            city = self.current_city
        else:
            self.current_city = city
            self.save_last_city()
        
        self.status_var.set(f"Fetching weather data for {city}...")
        self.root.update()
        
        try:
            # Get current weather
            current_url = f"http://api.openweathermap.org/data/2.5/weather?q={city}&appid={self.api_key}&units={self.units}"
            response = requests.get(current_url)
            response.raise_for_status()
            current_data = response.json()
            
            # Get 5-day forecast
            forecast_url = f"http://api.openweathermap.org/data/2.5/forecast?q={city}&appid={self.api_key}&units={self.units}"
            response = requests.get(forecast_url)
            response.raise_for_status()
            forecast_data = response.json()
            
            # Update UI with current weather
            self.update_current_weather(current_data)
            
            # Update forecast
            self.update_forecast(forecast_data)
            
            # Update chart
            self.update_chart(forecast_data)
            
            self.status_var.set(f"Weather data for {city} loaded successfully")
            
        except requests.exceptions.RequestException as e:
            messagebox.showerror("Error", f"Failed to fetch weather data: {e}")
            self.status_var.set("Error fetching weather data")
        except KeyError as e:
            messagebox.showerror("Error", f"Unexpected data format: {e}")
            self.status_var.set("Error parsing weather data")
    
    def update_current_weather(self, data):
        # Extract data
        city = data['name']
        country = data['sys']['country']
        temp = data['main']['temp']
        feels_like = data['main']['feels_like']
        humidity = data['main']['humidity']
        pressure = data['main']['pressure']
        wind_speed = data['wind']['speed']
        description = data['weather'][0]['description'].title()
        visibility = data.get('visibility', 'N/A')
        icon_code = data['weather'][0]['icon']
        
        # Update labels
        self.location_label.config(text=f"{city}, {country}")
        unit_symbol = "°C" if self.units == "metric" else "°F"
        self.temp_label.config(text=f"{temp:.1f}{unit_symbol}")
        self.desc_label.config(text=description)
        self.feels_like_label.config(text=f"Feels like: {feels_like:.1f}{unit_symbol}")
        self.humidity_label.config(text=f"Humidity: {humidity}%")
        self.wind_label.config(text=f"Wind: {wind_speed} m/s")
        self.pressure_label.config(text=f"Pressure: {pressure} hPa")
        
        if visibility != 'N/A':
            visibility_km = visibility / 1000
            self.visibility_label.config(text=f"Visibility: {visibility_km:.1f} km")
        else:
            self.visibility_label.config(text="Visibility: N/A")
        
        # Load weather icon
        self.load_weather_icon(icon_code)
    
    def load_weather_icon(self, icon_code):
        try:
            # Try to load icon from URL
            icon_url = f"http://openweathermap.org/img/wn/{icon_code}@2x.png"
            response = requests.get(icon_url)
            image_data = response.content
            image = Image.open(io.BytesIO(image_data))
            photo = ImageTk.PhotoImage(image)
            self.weather_icon_label.configure(image=photo)
            self.weather_icon_label.image = photo
        except:
            # If loading fails, just show the icon code
            self.weather_icon_label.configure(text=icon_code)
    
    def update_forecast(self, data):
        # Clear previous forecast
        for widget in self.scrollable_frame.winfo_children():
            widget.destroy()
        
        # Group forecasts by day
        forecasts_by_day = {}
        for forecast in data['list']:
            date = forecast['dt_txt'].split(' ')[0]
            if date not in forecasts_by_day:
                forecasts_by_day[date] = []
            forecasts_by_day[date].append(forecast)
        
        # Display forecast for each day
        for i, (date, day_forecasts) in enumerate(forecasts_by_day.items()):
            if i >= 5:  # Limit to 5 days
                break
                
            # Get min and max temp for the day
            temps = [f['main']['temp'] for f in day_forecasts]
            min_temp = min(temps)
            max_temp = max(temps)
            
            # Get most common weather condition
            weather_counts = {}
            for f in day_forecasts:
                condition = f['weather'][0]['main']
                weather_counts[condition] = weather_counts.get(condition, 0) + 1
            common_weather = max(weather_counts, key=weather_counts.get)
            
            # Format date
            date_obj = datetime.strptime(date, '%Y-%m-%d')
            formatted_date = date_obj.strftime('%a, %b %d')
            
            # Create day frame
            day_frame = ttk.Frame(self.scrollable_frame, relief="solid", padding="5")
            day_frame.grid(row=0, column=i, padx=5, pady=5, sticky="nsew")
            
            # Add day information
            ttk.Label(day_frame, text=formatted_date, font=("Arial", 10, "bold")).grid(row=0, column=0, pady=5)
            ttk.Label(day_frame, text=common_weather).grid(row=1, column=0)
            
            unit_symbol = "°C" if self.units == "metric" else "°F"
            ttk.Label(day_frame, text=f"High: {max_temp:.1f}{unit_symbol}").grid(row=2, column=0)
            ttk.Label(day_frame, text=f"Low: {min_temp:.1f}{unit_symbol}").grid(row=3, column=0)
    
    def update_chart(self, data):
        # Clear previous chart
        self.ax.clear()
        
        # Extract data for chart
        times = []
        temps = []
        
        for forecast in data['list']:
            # Convert string to datetime
            dt = datetime.strptime(forecast['dt_txt'], '%Y-%m-%d %H:%M:%S')
            times.append(dt)
            temps.append(forecast['main']['temp'])
        
        # Plot data
        self.ax.plot(times, temps, marker='o', linestyle='-', linewidth=2, markersize=4)
        
        # Format x-axis to show dates nicely
        self.ax.xaxis.set_major_formatter(mdates.DateFormatter('%a %H:%M'))
        self.ax.xaxis.set_major_locator(mdates.HourLocator(interval=6))
        self.fig.autofmt_xdate()
        
        # Set labels and title
        unit_symbol = "°C" if self.units == "metric" else "°F"
        self.ax.set_ylabel(f'Temperature ({unit_symbol})')
        self.ax.set_title('Temperature Forecast')
        self.ax.grid(True, linestyle='--', alpha=0.7)
        
        # Update canvas
        self.canvas_chart.draw()
    
    def save_last_city(self):
        try:
            with open("weather_app_settings.json", "w") as f:
                json.dump({"last_city": self.current_city, "units": self.units}, f)
        except:
            pass  # Silently fail if we can't save settings
    
    def load_last_city(self):
        try:
            with open("weather_app_settings.json", "r") as f:
                settings = json.load(f)
                self.current_city = settings.get("last_city", "London")
                self.units = settings.get("units", "metric")
                self.unit_var.set(self.units)
                self.city_var.set(self.current_city)
        except:
            pass  # Silently fail if we can't load settings

def main():
    root = tk.Tk()
    app = WeatherApp(root)
    root.mainloop()

if __name__ == "__main__":
    main()
