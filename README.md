# Air Quality Comparison Tool (https://airqualitycomparison.onrender.com/)

A web application to compare air quality measurements between two selected countries based on the OpenAQ API dataset (openaq.csv).

Data source: https://public.opendatasoft.com/explore/dataset/openaq/export/?flg=en-us&disjunctive.measurements_parameter&disjunctive.location&disjunctive.city

## Features

- Visualize and compare air pollutant levels between two countries
- Select from various air pollutant types (NO2, PM2.5, O3, etc.)
- Interactive bar charts showing average pollutant levels based on the data given.

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
2. In the left panel, select country 'A', that you'd like to compare with country 'B'
3. On the right panel, select country 'B', that you'd like to compare with country 'A'
4. The charts will automatically update to show the average air pollutant levels for each country

## Technologies Used

- Frontend: HTML, CSS, JavaScript, Plotly.js
- Backend: Flask, Pandas
- Data Visualization: Plotly

## Notes

- The application calculates average pollutant values for each country based on the public OpenAQ dataset, linked at the top.
- The number of measurements available in the dataset and used for the calculation is displayed in the chart title.
- If no data is available for a specific country/pollutant combination, the chart will display "No data".
