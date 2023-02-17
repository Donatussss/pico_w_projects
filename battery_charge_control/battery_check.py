import rp2
import network
import ubinascii
import socket
import urequests
import time
from time import sleep
import machine
from machine import Pin, WDT
import ntptime
import uasyncio as asyncio

rp2.country('KE')
wdt = WDT(timeout=8000)
wlan = network.WLAN(network.STA_IF)
credentials = {
    'ssid': 'A Network',
    'password': 'Network Password'
}


def connect_to_wifi():
    wlan.active(True)
    wlan.connect(credentials['ssid'], credentials['password'])

    # wait for connection with 5 second timeout
    timeout = 10
    while timeout > 0:
        if wlan.status() < 0 or wlan.status() >= 3:
            break
        timeout -= 1
        print('Waiting for connection...')
        time.sleep(1)
        
    # blink LED to show successful connection
    if wlan.status() != 3:
        raise RuntimeError('Wi-Fi connection failed')
    else:
        led = Pin('LED', Pin.OUT)
        for i in range(wlan.status()):
            led.toggle()
            time.sleep(.1)
            led.toggle()
        
        print('Connected')
        status = wlan.ifconfig()
        print(f'IP: {status[0]}')


# sleep while still resetting watchdog timer
async def async_sleep(sleep_s):
    max_sleep = 7
    sleep_intervals = sleep_s // max_sleep
    sleep_rem = sleep_s % max_sleep
    
    i = sleep_intervals
    while i > 0:
        await asyncio.sleep(max_sleep)
        wdt.feed()
        i -= 1
    
    await asyncio.sleep(sleep_rem)
    wdt.feed()


connect_to_wifi()
ntptime.settime()

device1 = Pin(0, Pin.OUT)
device2 = Pin(1, Pin.OUT)
devices = {
    'device1': device1,
    'device2': device2,
}

current_device = 'device1'

device_dict = {
    'device1': {
        'device_ip': '192.168.xx.xx',
        'device_status': 'not available',
        'battery_percent': 'not available',
        'time_checked': 'not available',
    },
    'device2': {
        'device_ip': '192.168.xx.xx',
        'device_status': 'not available',
        'battery_percent': 'not available',
        'time_checked': 'not available',
    }
}


def get_time():
    gmt_time = list(machine.RTC().datetime())[4:]
    gmt_time[0] = (gmt_time[0] + 3) % 24
    return str(gmt_time)


def change_device(current_device, device_list):
    return device_list[(device_list.index(current_device) + 1) % len(device_list)]


def power_decision(current_device, battery_percent, power_plugged):
    # power loss scenario
    # device was charging but then power loss occured
    if device_dict[current_device]["device_status"] == 'charging' and not power_plugged:
        devices[current_device].off()
        device_dict[current_device]["device_status"] = 'discharging'
    
    if device_dict[current_device]["device_status"] == 'not available' and power_plugged:
        device_dict[current_device]["device_status"] = 'charging'
    elif device_dict[current_device]["device_status"] == 'not available' and not power_plugged:
        device_dict[current_device]["device_status"] = 'discharging'
    
    if device_dict[current_device]["device_status"] == 'charging' and battery_percent > 80:
        devices[current_device].off()
        device_dict[current_device]["device_status"] = 'discharging'
        
    elif device_dict[current_device]["device_status"] == 'discharging' and battery_percent < 20:
        devices[current_device].on()
        device_dict[current_device]["device_status"] = 'charging'
    
    return ''        


async def serve_client(reader, writer):
    # print("Client connected")
    request_line = await reader.readline()
    
    # We are not interested in HTTP request headers, skip them
    while await reader.readline() != b"\r\n":
        pass
    
    response = str(device_dict)    
    writer.write(response)

    await writer.drain()
    await writer.wait_closed()
    # print("Client disconnected")


async def main():
    global current_device

    # setting up webserver
    asyncio.create_task(asyncio.start_server(serve_client, "0.0.0.0", 80))

    while True:
        try:
            r = urequests.get(f'http://{device_dict[current_device]["device_ip"]}:5000/battery', timeout=5)
            params = r.text
            r.close()
            battery_percent, power_plugged = params.split(" ")
            power_decision(current_device, int(battery_percent), power_plugged=="True")
        
        except Exception as e:
            # print(e)
            wdt.feed()
            device_dict[current_device]["device_status"] = 'not available'
            
        if device_dict[current_device]["device_status"] != 'not available':            
            device_dict[current_device]["battery_percent"] = battery_percent
            device_dict[current_device]["time_checked"] = get_time()

        asyncio.run(async_sleep(5))
        current_device = change_device(current_device, list(device_dict.keys()))


try:
    asyncio.run(main())
finally:
    asyncio.new_event_loop()