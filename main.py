import mysql.connector
import pandas as pd
from datetime import datetime

try:
    conn = mysql.connector.connect(
        host='localhost',
        user='root',
        password='1234',
        database='Bajaj'
    )
    if conn.is_connected():
        print("✅ Connected to MySQL database")
except mysql.connector.Error as err:
    print("❌ Failed to connect:", err)

cursor = conn.cursor(dictionary=True)

query = """
SELECT 
    P.AMOUNT AS SALARY,
    CONCAT(E.FIRST_NAME, ' ', E.LAST_NAME) AS NAME,
    E.DOB,
    D.DEPARTMENT_NAME
FROM PAYMENTS P
JOIN EMPLOYEE E ON P.EMP_ID = E.EMP_ID
JOIN DEPARTMENT D ON E.DEPARTMENT = D.DEPARTMENT_ID
WHERE DAY(P.PAYMENT_TIME) != 1
AND P.AMOUNT = (
    SELECT MAX(AMOUNT)
    FROM PAYMENTS
    WHERE DAY(PAYMENT_TIME) != 1
);
"""

cursor.execute(query)
rows = cursor.fetchall()
df = pd.DataFrame(rows)

df['DOB'] = pd.to_datetime(df['DOB'])
today = pd.Timestamp(datetime.today().date())
df['AGE'] = df['DOB'].apply(lambda dob: today.year - dob.year - ((today.month, today.day) < (dob.month, dob.day)))

final_df = df[['SALARY', 'NAME', 'AGE', 'DEPARTMENT_NAME']]
print(final_df)

cursor.close()
conn.close()

import requests

# Your final SQL query
final_sql_query = """
SELECT
    p.AMOUNT AS SALARY,
    CONCAT(e.FIRST_NAME, ' ', e.LAST_NAME) AS NAME,
    TIMESTAMPDIFF(YEAR, e.DOB, CURDATE()) AS AGE,
    d.DEPARTMENT_NAME
FROM PAYMENTS p
JOIN EMPLOYEE e ON p.EMP_ID = e.EMP_ID
JOIN DEPARTMENT d ON e.DEPARTMENT = d.DEPARTMENT_ID
WHERE DAY(p.PAYMENT_TIME) != 1
ORDER BY p.AMOUNT DESC
LIMIT 1;
"""

# API endpoint
url = "https://bfhldevapigw.healthrx.co.in/hiring/testWebhook/PYTHON"

# Authorization token
access_token = "eyJhbGciOiJIUzI1NiJ9.eyJyZWdObyI6IlJFRzEwNTciLCJuYW1lIjoiTXVydHV6YSBTaGFoaWQiLCJlbWFpbCI6Im11cnR1emFzaGFoaWQyMjA2NDVAYWNyb3BvbGlzLmluIiwic3ViIjoid2ViaG9vay11c2VyIiwiaWF0IjoxNzQ2OTYyMDQ2LCJleHAiOjE3NDY5NjI5NDZ9.3C4TR45Tsj3Zp0ZAfy_YVHmHeMIhBuEumO2diMIinu0"

# Headers
headers = {
    "Authorization": access_token,
    "Content-Type": "application/json"
}

# Body
data = {
    "finalQuery": final_sql_query.strip()
}

# POST request
response = requests.post(url, headers=headers, json=data)

# Check response
print("Status Code:", response.status_code)
print("Response Body:", response.text)
