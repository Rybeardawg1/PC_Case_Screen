#!/usr/bin/env python

from flask import Flask, jsonify
import psutil
import clr

# Add path to OpenHardwareMonitorLib.dll
clr.AddReference(r"C:\Program Files\OpenHardwareMonitor\OpenHardwareMonitorLib.dll")
from OpenHardwareMonitor import Hardware

app = Flask(__name__)


def initialize_openhardwaremonitor():
    handle = Hardware.Computer()
    handle.MainboardEnabled = False
    handle.CPUEnabled = True
    handle.RAMEnabled = False
    handle.GPUEnabled = True
    handle.HDDEnabled = False
    handle.Open()
    return handle


ohm_handle = initialize_openhardwaremonitor()

previous_disk_io = psutil.disk_io_counters()
previous_net_io = psutil.net_io_counters()


def get_gpu_info():
    gpu_temp = None
    gpu_load = None
    for i in ohm_handle.Hardware:
        if (
            i.HardwareType == Hardware.HardwareType.GpuNvidia
            or i.HardwareType == Hardware.HardwareType.GpuAti
        ):
            i.Update()
            for sensor in i.Sensors:
                if (
                    sensor.SensorType == Hardware.SensorType.Temperature
                    and "GPU" in sensor.Name
                ):
                    gpu_temp = sensor.Value
                elif (
                    sensor.SensorType == Hardware.SensorType.Load
                    and "GPU" in sensor.Name
                ):
                    gpu_load = sensor.Value
    return gpu_temp, gpu_load


def get_cpu_temp():
    for i in ohm_handle.Hardware:
        if i.HardwareType == Hardware.HardwareType.CPU:
            i.Update()
            for sensor in i.Sensors:
                if sensor.SensorType == Hardware.SensorType.Temperature:
                    return sensor.Value
    return None


def get_disk_usage():
    global previous_disk_io
    current_disk_io = psutil.disk_io_counters()
    read_bytes = current_disk_io.read_bytes - previous_disk_io.read_bytes
    write_bytes = current_disk_io.write_bytes - previous_disk_io.write_bytes
    previous_disk_io = current_disk_io
    return read_bytes / (1024 * 1024), write_bytes / (1024 * 1024)


def get_network_usage(interval=1):
    global previous_net_io
    current_net_io = psutil.net_io_counters()
    sent = (
        (current_net_io.bytes_sent - previous_net_io.bytes_sent)
        / (1024 * 1024)
        / interval
    )
    recv = (
        (current_net_io.bytes_recv - previous_net_io.bytes_recv)
        / (1024 * 1024)
        / interval
    )
    previous_net_io = current_net_io
    return sent, recv


def get_system_vitals():
    cpu_temp = get_cpu_temp()
    gpu_temp, gpu_load = get_gpu_info()
    read_bytes, write_bytes = get_disk_usage()
    sent, recv = get_network_usage()

    vitals = {
        "cpu_usage": f"{psutil.cpu_percent(interval=1)}%",
        "memory_usage": f"{psutil.virtual_memory().percent}%",
        "disk_usage_read": f"{read_bytes:.2f} MB/s",
        "disk_usage_write": f"{write_bytes:.2f} MB/s",
        "cpu_temp": f"{cpu_temp:.2f}°C" if cpu_temp is not None else "N/A",
        "gpu_temp": f"{gpu_temp:.2f}°C" if gpu_temp is not None else "N/A",
        "gpu_usage": f"{gpu_load:.2f}%" if gpu_load is not None else "N/A",
        "network_sent": f"{sent:.2f} MB/s",
        "network_recv": f"{recv:.2f} MB/s",
    }
    return vitals


@app.route("/")
def vitals():
    return jsonify(get_system_vitals())


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=3000)
