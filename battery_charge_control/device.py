from flask import Flask
import psutil

app = Flask(__name__)

@app.route('/battery', methods=['POST', 'GET'])
def battery():
    battery = psutil.sensors_battery()
    return str(battery.battery_percent) + ' ' + str(battery.power_plugged)


if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=5000)