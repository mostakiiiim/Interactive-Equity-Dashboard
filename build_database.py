import pandas as pd
import sqlite3

#load the kaggle csv into pandas dataframe

print ("Loading Csv")
df = pd.read_csv("all_stocks_5yr.csv")

#Connect to local Sqlite database file

print("Connecting to Sqlite database...")
conn=sqlite3.connect('stocks.db')

#Save the dataframe into database as a SQL table

print("Writing SQL table...")
df.to_sql('historical_prices', conn, if_exists='replace', index = False)

#close the connection

conn.close()
print("Database created successfully! New file created stocks.db file")

