import flet as ft
import psutil
import time
from threading import Thread
import random

def fetch_process_data():
    processes = []
    for proc in psutil.process_iter(['pid', 'name', 'cpu_times', 'create_time']):
        with proc.oneshot():
            try:
                pid = proc.info['pid']
                name = proc.info['name']
                user_time = proc.info['cpu_times'].user
                system_time = proc.info['cpu_times'].system
                burst_time = user_time + system_time
                arrival_time = proc.info['create_time']
                process = {
                    "pid": pid,
                    "name": name,
                    "arrival_time": arrival_time,
                    "burst_time": burst_time,
                    "start_time": None,
                    "completion_time": None,
                    "turnaround_time": None,
                    "waiting_time": None,
                }
                processes.append(process)
            except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
                pass
    return processes

def run_sjf(processes):
    current_time = time.time()
    processes.sort(key=lambda p: p["burst_time"])
    for process in processes:
        if current_time < process["arrival_time"]:
            current_time = process["arrival_time"]
        process["start_time"] = current_time
        current_time += process["burst_time"]
        process["completion_time"] = current_time
        process["turnaround_time"] = process["completion_time"] - process["arrival_time"]
        process["waiting_time"] = process["turnaround_time"] - process["burst_time"]
    return processes

def main(page: ft.Page):
    page.title = "Live CPU Scheduler Simulation"
    processes = []
    page.scroll = True
    page.vertical_alignment='center'
    page.horizontal_alignment='center'
    page.padding = 20
    page.theme_mode='dark'

    def update_process_list():
        nonlocal processes
        processes = fetch_process_data()
        processes = run_sjf(processes)
        update_data_table()

    def run_and_display_simulation():
        while True:
            update_process_list()
            time.sleep(1)

    def update_data_table():
        nonlocal processes
        table = process_table
        table.rows.clear()
        turnaround_data = []  # List to store turnaround time data for the chart

        for process in processes:
            start_time = str(process['start_time']) if process['start_time'] else ""
            completion_time = str(process['completion_time']) if process['completion_time'] else ""
            turnaround_time = str(process['turnaround_time']) if process['turnaround_time'] else ""
            waiting_time = str(process['waiting_time']) if process['waiting_time'] else ""
            table.rows.append(ft.DataRow(
                cells=[
                    ft.DataCell(ft.Text(str(process['pid']))),
                    ft.DataCell(ft.Text(process['name'])),
                    ft.DataCell(ft.Text(str(process['arrival_time']))),
                    ft.DataCell(ft.Text(str(process['burst_time']))),
                    ft.DataCell(ft.Text(start_time)),
                    ft.DataCell(ft.Text(completion_time)),
                    ft.DataCell(ft.Text(turnaround_time)),
                    ft.DataCell(ft.Text(waiting_time)),
                ]
            ))
            turnaround_data.append(float(turnaround_time))  # Add turnaround time to the chart data

        update_graph(turnaround_data)  # Update the chart with the new data

    def update_graph(turnaround_data):
        nonlocal chart
        chart.bar_groups[0].bar_rods[0].to_y = random.randint(15, 100)  # Update the bar height for the first group
        chart.bar_groups[1].bar_rods[0].to_y = random.randint(15, 100)  # Update the bar height for the second group
        chart.bar_groups[2].bar_rods[0].to_y = random.randint(15, 100)  # Update the bar height for the third group
        page.update()

    process_rows = ft.Column()
    process_table = ft.DataTable(
        columns=[
            ft.DataColumn(ft.Text("PID")),
            ft.DataColumn(ft.Text("Name")),
            ft.DataColumn(ft.Text("Arrival Time")),
            ft.DataColumn(ft.Text("Burst Time")),
            ft.DataColumn(ft.Text("Start Time")),
            ft.DataColumn(ft.Text("Completion Time")),
            ft.DataColumn(ft.Text("Turnaround Time")),
            ft.DataColumn(ft.Text("Waiting Time")),
        ],
        rows=process_rows.controls,
    )
    
    chart = ft.BarChart(
        bar_groups=[
            ft.BarChartGroup(
                x=0,
                bar_rods=[
                    ft.BarChartRod(
                        from_y=0,
                        to_y=random.randint(15, 100),
                        width=40,
                        color=ft.colors.AMBER,
                        tooltip="Turnaround Time",
                        border_radius=0,
                    ),
                ],
            ),
            ft.BarChartGroup(
                x=1,
                bar_rods=[
                    ft.BarChartRod(
                        from_y=0,
                        to_y=random.randint(15, 100),
                        width=40,
                        color=ft.colors.BLUE,
                        tooltip="Turnaround Time",
                        border_radius=0,
                    ),
                ],
            ),
            ft.BarChartGroup(
                x=2,
                bar_rods=[
                    ft.BarChartRod(
                        from_y=0,
                        to_y=random.randint(15, 100),
                        width=40,
                        color=ft.colors.ORANGE,
                        tooltip="Turnaround Time",
                        border_radius=0,
                    ),
                ],
            ),
        ],
        border=ft.border.all(1, ft.colors.GREY_400),
        left_axis=ft.ChartAxis(
            labels_size=40, title=ft.Text("Turnaround Time"), title_size=40
        ),
        bottom_axis=ft.ChartAxis(
            labels=[
                ft.ChartAxisLabel(
                    value=0, label=ft.Container(ft.Text("1"), padding=10)
                ),
                ft.ChartAxisLabel(
                    value=1, label=ft.Container(ft.Text("2"), padding=10)
                ),
                ft.ChartAxisLabel(
                    value=2, label=ft.Container(ft.Text("3"), padding=10)
                ),
            ],
            labels_size=40,
        ),
        horizontal_grid_lines=ft.ChartGridLines(
            color=ft.colors.GREY_300, width=1, dash_pattern=[3, 3]
        ),
        tooltip_bgcolor=ft.colors.with_opacity(0.5, ft.colors.GREY_300),
        max_y=110,
        interactive=True,
        expand=True,
    )

    page.add(
        ft.AppBar(title=ft.Text("Process Scheduling Simulation Live"), bgcolor=ft.colors.RED, color='white'),
        ft.Container(content=chart,bgcolor='',height=300,padding=20),
        ft.Column(
            controls=[
                process_table,
            ]
        )
    )

    # Start the simulation and update loop in a separate thread
    Thread(target=run_and_display_simulation, daemon=True).start()

ft.app(target=main)