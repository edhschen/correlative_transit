from ..connection import *

# change this to main or sample dataset depending on what's being used
tables = {
    "ODX": "sfbay-bart-hourlyridership-2021"
}

query = """
SELECT date, exit_station, SUM(trip_count) as exits
FROM `sfbay-bart-hourlyridership-21`
GROUP BY date, exit_station
ORDER BY date
"""

result = testQuery(query)
exits = result.groupby('date')[['exit_station', 'exits']].apply(lambda x: x.set_index('exit_station').to_dict()).to_json()

with open("sfbay-bart-exits.json", "w") as file:
    file.write(exits)


"""
SELECT entry.year, entry.week, entry.hour, entry.entry_station, entry.entries - exits.exits
FROM (
    SELECT year(date) as year, week(date) as week, hour, entry_station, ROUND(AVG(trips),2) as entries
    FROM (
        SELECT date, hour, entry_station, SUM(trip_count) as trips
        FROM `sfbay-bart-hourlyridership-21`
        GROUP BY date, hour, entry_station
    ) as subtable WHERE entry_station = "WARM"
    GROUP BY year(date), week(date), hour, entry_station
    ORDER BY week(date), hour
) entry
LEFT JOIN
(
    SELECT year(date) as year, week(date) as week, hour, exit_station, ROUND(AVG(trips),2) as exits
    FROM (
        SELECT date, hour, exit_station, SUM(trip_count) as trips
        FROM `sfbay-bart-hourlyridership-21`
        GROUP BY date, hour, exit_station
    ) as subtable WHERE exit_station = "WARM"
    GROUP BY year(date), week(date), hour, exit_station
    ORDER BY week(date), hour
) exits
ON exits.year = entry.year AND exits.week = entry.week AND exits.hour = entry.hour AND entry.entry_station = exits.exit_station
UNION 
SELECT entry.year, entry.week, entry.hour, entry.entry_station, entry.entries - exits.exits
FROM (
    SELECT year(date) as year, week(date) as week, hour, entry_station, ROUND(AVG(trips),2) as entries
    FROM (
        SELECT date, hour, entry_station, SUM(trip_count) as trips
        FROM `sfbay-bart-hourlyridership-21`
        GROUP BY date, hour, entry_station
    ) as subtable WHERE entry_station = "WARM"
    GROUP BY year(date), week(date), hour, entry_station
    ORDER BY week(date), hour
) entry
RIGHT JOIN 
(
    SELECT year(date) as year, week(date) as week, hour, exit_station, ROUND(AVG(trips),2) as exits
    FROM (
        SELECT date, hour, exit_station, SUM(trip_count) as trips
        FROM `sfbay-bart-hourlyridership-21`
        GROUP BY date, hour, exit_station
    ) as subtable WHERE exit_station = "WARM"
    GROUP BY year(date), week(date), hour, exit_station
    ORDER BY week(date), hour
) exits
ON exits.year = entry.year AND exits.week = entry.week AND exits.hour = entry.hour AND entry.entry_station = exits.exit_station
"""