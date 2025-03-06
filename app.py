from flask import Flask, render_template, jsonify
import pandas as pd
import json
import plotly
import plotly.express as px
import os

app = Flask(__name__)

def load_data():
    """
    Load the CSV data, handling semicolon separators.
    """
    try:
        print("Looking for CSV at: openaq.csv")
        if os.path.exists('openaq.csv'):
            df = pd.read_csv('openaq.csv', sep=';', on_bad_lines='skip')
            
            if len(df.columns) > 1:
                print(f"CSV loaded successfully with semicolon separator. Shape: {df.shape}")
            else:
                for separator in [',', '\t', '|']:
                    try:
                        df = pd.read_csv('openaq.csv', sep=separator, on_bad_lines='skip')
                        if len(df.columns) > 1:
                            print(f"CSV loaded successfully with '{separator}' separator. Shape: {df.shape}")
                            break
                    except:
                        continue
                
                if len(df.columns) == 1:
                    print("Could not automatically detect separator. Creating demo data.")
                    return create_demo_data()
            
            print(f"Columns: {df.columns.tolist()}")
            
            if 'Value' in df.columns:
                df = df[df['Value'] >= 0]
            else:
                print(f"Column 'Value' not found in CSV. Available columns: {df.columns.tolist()}")
                return create_demo_data()
                
            if 'Country Label' not in df.columns or 'Pollutant' not in df.columns:
                print("Missing required columns. Creating demo data.")
                return create_demo_data()
            return df
        else:
            print("CSV file not found. Creating demo data.")
            return create_demo_data()
    except Exception as e:
        print(f"Error loading data: {e}")
        return create_demo_data()

def create_demo_data():
    """Create a demo dataset with realistic air quality data"""
    print("Creating demo data")
    data = {
        'Country Label': ['United States', 'China', 'India', 'United Kingdom', 'France', 
                         'Germany', 'Japan', 'Brazil', 'Russia', 'Australia'] * 5,
        'Pollutant': ['NO2', 'NO2', 'NO2', 'NO2', 'NO2', 
                     'PM2.5', 'PM2.5', 'PM2.5', 'PM2.5', 'PM2.5'] * 5,
        'Value': [35.2, 85.7, 75.3, 42.1, 38.7, 
                 12.4, 58.5, 35.2, 22.8, 8.6] * 5,
        'Unit': ['µg/m³', 'µg/m³', 'µg/m³', 'µg/m³', 'µg/m³', 
                'µg/m³', 'µg/m³', 'µg/m³', 'µg/m³', 'µg/m³'] * 5
    }
    return pd.DataFrame(data)

def get_countries(df):
    try:
        return sorted(df['Country Label'].dropna().unique().tolist())
    except Exception as e:
        print(f"Error getting countries: {e}")
        return ["United States", "China", "India"]

def get_pollutants(df):
    try:
        return sorted(df['Pollutant'].dropna().unique().tolist())
    except Exception as e:
        print(f"Error getting pollutants: {e}")
        return ["NO2", "PM2.5", "O3"]

def get_country_pollutant_avg(df, country, pollutant):
    try:
        filtered_df = df[(df['Country Label'] == country) & (df['Pollutant'] == pollutant)]
        if filtered_df.empty:
            return 0, 0, "No data"
        
        avg_value = filtered_df['Value'].mean()
        count = len(filtered_df)
        unit = filtered_df['Unit'].iloc[0] if not filtered_df['Unit'].empty else "µg/m³"
        
        return round(avg_value, 2), count, unit
    except Exception as e:
        print(f"Error calculating average for {country}/{pollutant}: {e}")
        return 0, 0, "Error"

def create_bar_chart(value, country, pollutant, unit, count):
    try:
        if value == 0 and count == 0:
            fig = px.bar(x=["No data"], y=[0])
            fig.update_layout(
                title=f"No data for {pollutant} in {country}",
                xaxis_title="",
                yaxis_title="",
                height=400,
            )
        else:
            fig = px.bar(x=[country], y=[value], 
                         labels={'x': 'Country', 'y': f'{pollutant} ({unit})'},
                         title=f"{pollutant} Level in {country} (based on {count} measurements)")
            fig.update_layout(
                height=400,
                yaxis_title=f"{pollutant} ({unit})",
            )
        
        graph_json = json.dumps(fig, cls=plotly.utils.PlotlyJSONEncoder)
        return graph_json
    except Exception as e:
        print(f"Error creating chart: {e}")
        fig = px.bar(x=["Error"], y=[0])
        fig.update_layout(title=f"Error creating chart")
        return json.dumps(fig, cls=plotly.utils.PlotlyJSONEncoder)

@app.route('/')
def index():
    try:
        df = load_data()
        countries = get_countries(df)
        pollutants = get_pollutants(df)
        
        default_country1 = countries[0] if countries else "No data"
        default_country2 = countries[1] if len(countries) > 1 else countries[0] if countries else "No data"
        default_pollutant = pollutants[0] if pollutants else "NO2"
        
        value1, count1, unit1 = get_country_pollutant_avg(df, default_country1, default_pollutant)
        value2, count2, unit2 = get_country_pollutant_avg(df, default_country2, default_pollutant)
        
        graph1_json = create_bar_chart(value1, default_country1, default_pollutant, unit1, count1)
        graph2_json = create_bar_chart(value2, default_country2, default_pollutant, unit2, count2)
        
        return render_template('index.html', 
                               countries=countries,
                               pollutants=pollutants,
                               default_country1=default_country1,
                               default_country2=default_country2,
                               default_pollutant=default_pollutant,
                               graph1_json=graph1_json,
                               graph2_json=graph2_json)
    except Exception as e:
        error_message = f"Application error: {str(e)}"
        print(error_message)
        return render_template('error.html', error=error_message)

@app.route('/update_chart/<country>/<pollutant>/<position>')
def update_chart(country, pollutant, position):
    try:
        df = load_data()
        value, count, unit = get_country_pollutant_avg(df, country, pollutant)
        graph_json = create_bar_chart(value, country, pollutant, unit, count)
        return jsonify({"chart": graph_json})
    except Exception as e:
        return jsonify({"error": str(e)})

#Error handler for 404
@app.errorhandler(404)
def page_not_found(e):
    return render_template('error.html', error="Page not found"), 404

#Error handler for 500
@app.errorhandler(500)
def server_error(e):
    return render_template('error.html', error="Server error"), 500

if __name__ == '__main__':
    app.run(debug=True)
