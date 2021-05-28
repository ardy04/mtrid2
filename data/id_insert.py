import uuid
import pandas as pd


df = pd.read_excel("cap_data.xlsx")
id = [uuid.uuid1() for i in range(1,3001)]
df.insert(10, "Unique_ID", id)
print(df.head)
df.to_excel("cap_data_withID.xlsx")

