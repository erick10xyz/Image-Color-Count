import numpy as np
from PIL import Image
import pandas as pd
from flask import Flask, render_template, request, redirect, url_for
from flask_bootstrap import Bootstrap5
import requests
from io import BytesIO
import os

app = Flask(__name__)
Bootstrap5(app)


# Temporary storage of data of an image which being converted in the process
file = 'image_color.csv'
# Delete storage if not empty
if(os.path.exists(file) and os.path.isfile(file)):
  os.remove(file)
  print("file deleted")
else:
  print("file not found")

#  Paste your image address, get image information and convert to numpy array and save as Dataframe type
@app.route("/", methods=["GET", "POST"])
def home():
    if request.method == "POST":
        image_url = request.form.get("imgfile")
        response = requests.get(image_url)
        img = Image.open(BytesIO(response.content))
        np_img = np.array(img)
        colors = pd.DataFrame(np_img.reshape(-1, 3), columns=list("RGB"))
        colors["count"] = 1
        colors = colors.groupby(["R", "G", "B"]).count().reset_index()
        colors.to_csv("image_color.csv")
        return redirect(url_for('calc_colors'))
    return render_template("index.html")


# count the colors of an image and get the max 10
@app.route("/colorlist")
def calc_colors():
    store_colors = pd.read_csv('image_color.csv')
    total = len(store_colors)
    top_color = store_colors.nlargest(10, 'count', keep='first')
    clean_df = pd.DataFrame(top_color)
    rgb_colors = []
    for item in range(len(clean_df)):
        rgb_colors.append((clean_df.iloc[item, 1], clean_df.iloc[item, 2], clean_df.iloc[item, 3]))
    percentage = []
    for i in range(len(clean_df)):
        numbers = clean_df.iloc[i, 4]
        percentage.append((int(numbers) / total) * 100)
    clean_df["rgb_colors"] = rgb_colors
    clean_df["percentage"] = percentage
    print(clean_df)
    return render_template("colorlist.html", rgb_data=clean_df)

if __name__ == '__main__':
    app.run(debug=True)
