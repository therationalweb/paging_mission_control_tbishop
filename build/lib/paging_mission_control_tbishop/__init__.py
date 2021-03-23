import tkinter as tk
from tkinter.filedialog import askopenfilename
import tkinter.scrolledtext as scrolledtext
from datetime import datetime, timedelta
from collections import deque
import os
import json

# Beautiful is better than ugly
# Simple is better than complex

# This dictionary will hold the incident data, i.e. those instances
# when a reading is outside the given tolerance.
incidents = {}


def set_state(state):
    if state == "default":
        lbl_contents.pack_forget()
        txt_contents.pack_forget()
        txt_contents.config(state="normal")
        txt_contents.delete("1.0", tk.END)
        lbl_results.pack_forget()
        txt_results.pack_forget()
        update_progress("Ready ...")
        incidents.clear()
        return
    elif state == "parse":
        lbl_contents.pack()
        txt_contents.pack()
        txt_contents.config(state="disabled")
        lbl_results.pack()
        txt_results.pack()
        return


def update_progress(text_to_show):
    """ Update the status bar in the window """
    lbl_progress["text"] = text_to_show
    return


def append_status_text(text_to_append):
    """Append text to the status text field"""
    txt_status.insert(tk.END, text_to_append)
    return


def open_file():
    """Open a file for parsing."""
    set_state("default")
    filepath = askopenfilename(
        filetypes=[("Text Files", "*.txt"), ("All Files", "*.*")]
    )
    if not filepath:
        return

    file_stats = os.stat(filepath)
    update_progress(
        "File Found. "
        + str(file_stats.st_size)
        + " Bytes processed. Click Parse to continue."
    )

    with open(filepath, "r") as input_file:
        cnt = 0
        for line in input_file:
            text = line
            txt_contents.insert(tk.END, text.replace("|", "\t"))
            cnt += 1
    set_state("parse")
    # Closing the file **should not** be needed when using the 'with open() ...' approach,
    # but it isn't going to hurt.
    input_file.close
    return


def add_incident(incident_dict):
    sid = incident_dict["satellite_id"]
    comp = incident_dict["component"]
    ts = incident_dict["timestamp"]
    # 1) Is there an entry in the incident dictionary for this satellite?  If not, create one using the incident info.
    if sid not in incidents:
        incidents[sid] = {}
        incidents[sid][comp] = deque()
        incidents[sid][comp].append(ts)
    elif sid in incidents:
        # 2) If there is an entry, does it have a component entry? If not, create one using the incident info.
        if comp not in incidents[sid]:
            incidents[sid][comp] = deque()
            incidents[sid][comp].append(ts)
        # 3) If there is an entry - we have to figure out if we have broken the 3 entries in 5 minute
        #    rule, and if so, issue an alert.
        elif comp in incidents[sid]:
            # If there's only 1 entry in the deque, add this entry. No action required until there are 2.
            if len(incidents[sid][comp]) <= 1:
                incidents[sid][comp].append(ts)
            else:
                # There are 2 items in the deque ...
                # Calculate the threshold time (lowest entry in the deque + 5 mins)
                threshold_time = incidents[sid][comp][0] + timedelta(
                    minutes=5
                )  # Using this methodology ensures time calc over midnight is ok
                too_long = True if ts >= threshold_time else False
                if too_long:
                    incidents[sid][comp].popleft()
                    incidents[sid][comp].append(ts)
                else:
                    incidents[sid][comp].clear()
                    serverity = "RED HIGH" if comp == "TSTAT" else "RED LOW"
                    output_dict = {
                        "satelliteId": int(sid),
                        "severity": serverity,
                        "component": comp,
                        "timestamp": ts.strftime("%Y-%m-%dT%H:%M:%S.%fZ"),
                    }
                    json_txt = json.dumps(output_dict, indent=4) + "\n"
                    txt_results.insert(tk.END, json_txt)
    return


def parse_satellite_data():
    line_count = int(txt_contents.index("end-1c").split(".")[0])
    line_number = 1

    while line_number <= line_count:
        current_line_contents = txt_contents.get(
            str(line_number) + ".0", str(line_number) + ".0 lineend"
        )
        line_values_list = current_line_contents.split("\t")
        satellite_id, component, reading, red_high, red_low, dt = (
            line_values_list[1],
            line_values_list[7],
            line_values_list[6],
            line_values_list[2],
            line_values_list[5],
            datetime.strptime(line_values_list[0], "%Y%m%d %H:%M:%S.%f"),
        )
        if ((component == "TSTAT") and (float(reading) > int(red_high))) or (
            (component == "BATT") and (float(reading) < int(red_low))
        ):
            incident_dict = {
                "satellite_id": satellite_id,
                "component": component,
                "timestamp": dt,
            }
            add_incident(incident_dict)

        line_number += 1

    return


window = tk.Tk()
window.geometry("800x800")
window.title("Telemetry, Tracking, and Control System (TTCS)")

# Create the main frame
frm_main = tk.Frame(
    window, width=800, height=830, bg="White", relief=tk.SUNKEN, borderwidth=5
)
frm_main.pack(fill=tk.BOTH, expand=True)

# Create the button frame
frm_btns = tk.Frame(
    frm_main,
    width=100,
    height=800,
    bg="Silver",
    relief=tk.GROOVE,
    borderwidth=2,
    padx=5,
    pady=5,
)
frm_btns.pack(fill=tk.BOTH, side=tk.LEFT, expand=True)

# Create the content frame
frm_content = tk.Frame(frm_main, width=700, height=800, bg="SteelBlue", padx=5, pady=5)
frm_content.pack(fill=tk.BOTH, side=tk.LEFT, expand=True)

# Create the load button
btn_load = tk.Button(frm_btns, text="Load", width=10, command=open_file)
btn_load.pack()

# Create the parse button
btn_parse = tk.Button(frm_btns, text="Parse", width=10, command=parse_satellite_data)
btn_parse.pack()

# Create the instructions label
lbl_instructions = tk.Label(
    frm_content,
    text="About:\nThis program uses satellite telemetry and tracking data to provide information on the health and operability of satellites.\n\nInstructions:\nClick the Load button to find and upload the satellite data. Once loaded, click the Parse button.",
    relief=tk.GROOVE,
    width=700,
    wraplength=700,
    justify="left",
    background="Steelblue",
    foreground="White",
    anchor="w",
    font="Verdana 10 normal",
    padx=5,
    pady=5,
)
lbl_instructions.pack(padx=4, pady=2)

# Create the file contents label
# Hidden until a file is selected
lbl_contents = tk.Label(
    frm_content,
    text="Telemetry\Tracking Data Received",
    width=700,
    background="Steelblue",
    foreground="White",
    anchor="w",
    font="Verdana 12 normal",
    pady=5,
)
# lbl_contents.pack()

# Create the file contents text field
# Hidden until a file is selected
txt_contents = tk.scrolledtext.ScrolledText(
    frm_content, height=10, width=700, bg="AliceBlue", font="Calibri 10 normal"
)

# Create the alerts/results label
lbl_results = tk.Label(
    frm_content,
    text="Parse Results",
    width=700,
    background="Steelblue",
    foreground="White",
    anchor="w",
    font="Verdana 12 normal",
    pady=5,
)

# Create the alerts/results field
txt_results = tk.Text(
    frm_content,
    height=25,
    width=700,
    bg="AliceBlue",
    fg="Black",
    font="Calibri 10 normal",
)

frm_progress = tk.Frame(window, width=700, height=20, bg="Silver", padx=5, pady=5)
frm_progress.pack(fill=tk.BOTH, side=tk.LEFT, expand=True)

lbl_progress = tk.Label(
    frm_progress,
    text="Ready ...",
    width=700,
    height=1,
    background="Silver",
    foreground="Black",
    anchor="w",
)
lbl_progress.pack()

window.mainloop()
