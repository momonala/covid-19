### Scatter Plot

Here we have a scatter plot where we can visualize COVID-19 and demographic data scraped from [worldometers.info](https://www.worldometers.info/), a webiste compiling general demographic data about the planet. You can also view the data table below to see all the raw data. The table can be filtered 

ex. `>100` in the field New Cases will show all the countries that had more than 100 new cases yesterday. 

#### Linear vs Logarithmic
Again, you can chose to visualize the data linearly, or logarithmically. The advantage of that, is that we can regress one data variable against another, to see correlations. If both x and y are plotted logarithmically, and we see a near-straight line with the scatter points, then those data can be thought of to have some sort of correlation (but not necessarily causation).

#### Examples
Plotting Total Deaths against Total Cases results in a clear corrleation, that deaths increase as the number of cases increase. In this case, that value is the case-fatality-ratio, which is a metric for how deadly the disease is for those who contract it. You can read more about how to interpret that finding at [ourworldindata.org](https://ourworldindata.org/coronavirus#the-case-fatality-rate-cfr).

Plotting the Total Deaths/1M population against the Urban Population% also shows a loose correlation, suggesting that countries with old population might be more affected by the disease in terms of deaths per capita.

#### Minimum Case # Threshold
You can also use the `Min # Cases Threshold` to filter out any countries who have fewer that that many cases. Countries with few cases can often make the data more noisy.

#### Notes
Only countries which are selected in from the dropdown in the line graph chart above will be colored and labeled, to keep things clean. You can chose to show all labels by checking the `Show All Labels` box. If they do not show up immediately, double click anywhere on the chart to refresh it, and they should appear.

#### Data Values
Specific values we can regress are: 

- Total, New, and per 1 million population Confirmed Cases
- Total, New, and per 1 million population Confirmed Deaths
- Total Recoverd
- Total Active Cases (Confirmed - Recoverd)
- Total Serious/Critical Cases
- Total and per 1 million population Tests
- Population, Density, Land Area, Median Age, and Urban Population.

Note that there is missing data in some fields for various countries.
