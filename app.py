from flask import Flask, render_template, jsonify
import pandas as pd
import json
import plotly
import plotly.express as px
import os

# Initialize Flask application
app = Flask(__name__)

# Load data with robust error handling
def load_data():
    try:
        # Get path from environment variable, or use default
        csv_path = os.environ.get('CSV_PATH', 'openaq.csv')
        
        print(f"Looking for CSV at: {csv_path}")
        
        # Check if file exists
        if not os.path.exists(csv_path):
            print(f"CSV file not found at {csv_path}")
            return pd.DataFrame(columns=['Country Label', 'Pollutant', 'Value', 'Unit'])
            
        df = pd.read_csv(csv_path, on_bad_lines='skip')
        
        # Print data summary to help debug
        print(f"CSV loaded successfully. Shape: {df.shape}")
        print(f"Columns: {df.columns.tolist()}")
        
        # Filter out negative values
        if 'Value' in df.columns:
            df = df[df['Value'] >= 0]
        else:
            print(f"Column 'Value' not found in CSV. Available columns: {df.columns.tolist()}")
            
        return df
    except Exception as e:
        print(f"Error loading data: {e}")
        return pd.DataFrame(columns=['Country Label', 'Pollutant', 'Value', 'Unit'])

# Get list of unique countries
def get_countries(df):
    try:
        return sorted(df['Country Label'].dropna().unique().tolist())
    except Exception as e:
        print(f"Error getting countries: {e}")
        return ["No data available"]

# Get list of unique pollutants
def get_pollutants(df):
    try:
        return sorted(df['Pollutant'].dropna().unique().tolist())
    except Exception as e:
        print(f"Error getting pollutants: {e}")
        return ["No data available"]

# Calculate average pollutant value for a country
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
        print(f"Error calculating average: {e}")
        return 0, 0, "Error"

# Create bar chart
def create_bar_chart(value, country, pollutant, unit, count):
    try:
        if value == 0 and count == 0:
            # Create empty figure with message when no data
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
        
        # Convert to JSON for embedding in HTML
        graph_json = json.dumps(fig, cls=plotly.utils.PlotlyJSONEncoder)
        return graph_json
    except Exception as e:
        print(f"Error creating chart: {e}")
        fig = px.bar(x=["Error"], y=[0])
        fig.update_layout(title=f"Error creating chart")
        return json.dumps(fig, cls=plotly.utils.PlotlyJSONEncoder)

# Main route
@app.route('/')
def index():
    try:
        df = load_data()
        countries = get_countries(df)
        pollutants = get_pollutants(df)
        
        # Default selections
        default_country1 = countries[0] if countries else "No data"
        default_country2 = countries[1] if len(countries) > 1 else countries[0] if countries else "No data"
        default_pollutant = "NO2"  # Most common pollutant based on previous analysis
        
        # Get data for default selections
        value1, count1, unit1 = get_country_pollutant_avg(df, default_country1, default_pollutant)
        value2, count2, unit2 = get_country_pollutant_avg(df, default_country2, default_pollutant)
        
        # Create default charts
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

# Chart update route
@app.route('/update_chart/<country>/<pollutant>/<position>')
def update_chart(country, pollutant, position):
    try:
        df = load_data()
        value, count, unit = get_country_pollutant_avg(df, country, pollutant)
        graph_json = create_bar_chart(value, country, pollutant, unit, count)
        return jsonify({"chart": graph_json})
    except Exception as e:
        return jsonify({"error": str(e)})

# Only run the app directly when executing this file
if __name__ == '__main__':
    app.run(debug=True)
