import requests #pip install requests
from flask import Flask, render_template # pip install flask 

app = Flask(__name__)

data_dict = {
    "name": "zeeshan ali haider",
    "age": 20,
    "city": "lahore"
}




@app.route("/")
def main():
    return render_template("index.html", data=data_dict)


if __name__ == "__main__":
    app.run(debug=True)



#api_key = "RiCwmgdDXM81dqh9MrUMDqEu1LY7DlmZdIvUmmZJ"


#url = f"https://api.nasa.gov/?utm_sq=g9ubdahrerpage%2F2%2F&utm_gp=a85t9o&utm_medium%C3%A2%E2%82%AC%C2%A6=undefinedpage%2F13%2F&utm_partner=symbaloonl&utm_c2525252520ontent2525252520ontent=%5Bobject%2BObject%5D&utm_medium%E2%80%A6=undefined&utm_s=%5Bobject%2BObject%5D&partner_key=JeanFran%C3%A7oisTOURELpage%2F2%2F&coupon_code=customerreferral10+{api_key}"

#response = requests.get(url)

#if response.status_code == 200:
 #   data = response.json()
  #  print(data["title"])  # Assuming the data contains a "title" field
    