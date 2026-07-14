import json

import requests

# Request catalogue
catalogue = requests.get(
    "https://github.com/awesome-spectral-indices/awesome-earth-observation-instruments/raw/refs/heads/main/catalogue/catalogue.json"
).json()
# Save the dict as json file
with open("./xeo/data/catalogue.json", "w") as fp:
    json.dump(catalogue, fp, indent=4, sort_keys=True)