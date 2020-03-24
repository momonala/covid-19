### Line Plot

Here we have a line plot where we can visualize COVID-19 time series data, which has open sourced by Johns Hopkins University. The raw data can found on [Github](https://github.com/CSSEGISandData/COVID-19).

#### Data
Time Series graphing allows us to visualize how trends change over time. In this case, under the dropdown for `Data Source` we have raw data of Covid-19 `Confirmed Cases`, `Deaths`, and `Recoveries` for each country. 

Additionally, there is the caluclated value for the `Case Fatality Ratio`, or CFR. The CFR gives an indication for how deadly a disease is for those who contract it. It is a simple calculation of `Deaths / Confirmed Cases`. While useful, in an ongoing epidemic like this one, it is not a perfect metric calculate. The reason is that we don't know the *Total number of cases*, only the confirmed. These numbers can differ wildly, especially in the midst of an epidemic. For more information and other fatality metrics, see [ourworldindata.org](https://ourworldindata.org/coronavirus#what-do-we-know-about-the-risk-of-dying-from-covid-19) provides a great overview.

#### Linear vs. Logarithmic
All plots can be plotted linearly or logarithmically. A logarithmic chart is the natural scale for exponential grwoth. It is one where the axis increases in increments of 10 fold, rather than increments of 1. When plotted in this way, exponential growth is represented as a straight line, rather than a steep curve, the latter of which is harder to see small changes. In a logarithmic chart, deviations from a straight line show deviations from the exponential. So a slope curving flat or downwards means that the rate of increase is decreasing or negative, respectively. This can clearly be seen in China's growth trends, or in many European countries (Germany, Italy) in early April.

Grant Sanderson from 3Blue1Brown has a [great video on understanding exponential growth in the context of epidemics](https://www.youtube.com/watch?v=Kas0tIxDvrg) 

#### Data Views
There are several different views for the data. `Cumulative` allows one to view the total for a country at any given day. `Daily Increase` is simply how much the total number of cases increased day-over-day. Cases since 10, and 100, only plot the countries once they have a minimum number of cases, since growth takes various amounts of time to kick in. It allows you to compare countries from some initial starting point of when they experience the virus.

#### Trajectory
`Trajectory` is a useful view, which shows the exponential trajectory which each country is following, regardless of which stage in time it is currently in. It plots new confirmed cases of COVID-19 in the past day vs. the total confirmed cases to date. A country only gets plotted if once it meets a minimum threshold number of cases. This minimum allows you to see all countries start their trajectory at the same point at which the virus reaches each country. A line which drops off from the linear path means that there are few new cases being added, meaning they are sucessfully combatting the virus, as China and South Korea's trends show. It also shows that most countries are following the same trajectory, but are just at different stages. For a deeper primer on Trajectory charts, check out [Minute Physics's video on the topic](https://www.youtube.com/watch?v=54XLXg4fYsc&feature=emb_logo).
