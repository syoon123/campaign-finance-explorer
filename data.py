# %%
import requests
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

# %%
# Get Democratic candidates' ID
url="https://api.open.fec.gov/v1/candidates/?election_year=2020&is_active_candidate=true&sort_nulls_last=false&sort=name&api_key=PXwofAIOrHnlY4D2tImllz22JVUiRmigH9XQwgpm&office=P&sort_null_only=false&party=DEM&candidate_status=C&page=1&sort_hide_null=false&per_page=50"
data = requests.get(url).json()
results = data["results"]
dict1 = dict()
for item in results:
    name = item["name"]
    name = name.split(",")
    name = name[1]+" "+name[0]
    dict1[item["candidate_id"]] = name
df = pd.DataFrame.from_dict(dict1, orient='index', columns = ['id'])

#%%
# Get each candidates' financial summary
df["Receipts"] = np.nan
df["Disbursements"] = np.nan
df["Cash_on_hand"] = np.nan
for key,value in dict1.items():
    url = f"https://api.open.fec.gov/v1/candidates/totals/?election_year=2020&sort_nulls_last=false&api_key=PXwofAIOrHnlY4D2tImllz22JVUiRmigH9XQwgpm&sort_null_only=false&page=1&election_full=true&candidate_id={key}&sort_hide_null=false&per_page=20"
    data = requests.get(url).json()
    results = data["results"]
    df.loc[key,"Receipts"] = results[0]["receipts"]
    df.loc[key,"Disbursements"] = results[0]["disbursements"]
    df.loc[key,"Cash_on_hand"] = results[0]["receipts"] - results[0]["disbursements"]
# Only show those candidates that are significant
df1 = df[df.Receipts > 1000000]

#%%
# Plot
ax = df1.plot(x="id", y="Disbursements", kind="bar")
df1.plot(x="id", y="Cash_on_hand", kind="bar", ax=ax, color="C2")

plt.show()