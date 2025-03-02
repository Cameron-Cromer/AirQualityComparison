# Air Quality Comparison Tool

A web application to compare air quality measurements between two countries based on OpenAQ data.

Data source: https://public.opendatasoft.com/explore/dataset/openaq/export/?flg=en-us&disjunctive.measurements_parameter&disjunctive.location&disjunctive.city

## Features

- Visualize and compare air pollutant levels between two countries
- Select from various pollutant types (NO2, PM2.5, O3, etc.)
- Interactive bar charts showing average pollutant levels

## Project Structure

```
air-quality-comparison/
│
├── app.py               
├── openaq.csv         
├── requirements.txt
├── runtime.txt       
├── static/
│   └── styles.css      
└── templates/
    └── index.html        
```

## How to Use

1. At the top of the page, select the pollutant you want to compare (NO2, PM2.5, O3, etc.)
2. On the left panel, select the first country from the dropdown menu
3. On the right panel, select the second country from the dropdown menu
4. The charts will automatically update to show the average pollutant levels for each country

## Technologies Used

- Backend: Flask, Pandas
- Frontend: HTML, CSS, Plotly.js
- Data Visualization: Plotly

## Notes

- The application calculates average pollutant values for each country based on all available measurements
- The number of measurements used for the calculation is displayed in the chart title
- If no data is available for a specific country/pollutant combination, the chart will display "No data"
