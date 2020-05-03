import tkinter as tk
from tkinter import ttk
from src.fhir_module import *


def get_patients():
    practitioner_id = entry_field.get()
    try:
        current_practitioner = client.get_practitioner_info(practitioner_id)
    except KeyError:
        exit("Invalid practitioner ID")

    # Updating the UI with the practitioner's name
    practitioner_name = "Dr. " + current_practitioner.first_name + " " + current_practitioner.last_name
    label = tk.Label(main_UI, text=practitioner_name, font=("Arial", 20))
    entry_field.destroy()
    entry_label.destroy()
    get_patients_button.destroy()
    label.grid(row=0, column=0, columnspan=4)

    # get the practitioner's patient list
    current_practitioner.get_patient_list(client)
    patient_list = current_practitioner.get_all_patients()

    for patient in patient_list.get_patient_list():
        patient_name = patient.first_name+" "+patient.last_name
        patient_data = patient.get_data()
        cholesterol_level = str(patient_data[0])+" "+patient_data[1]
        effective_time = patient_data[2]
        new_entry = (patient_name, cholesterol_level, effective_time)
        if not duplicate_item(all_patients, new_entry):
            all_patients.insert("", "end", values=new_entry)


def add_monitored_patient(patient):
    new_entry = (patient[0], patient[1], patient[2])
    if not duplicate_item(monitored_patients, new_entry):
        monitored_patients.insert("", "end", values=new_entry)


def remove_monitored_patient(event):
    item = monitored_patients.selection()
    monitored_patients.delete(item)


def on_all_patients_double_click(event):
    item = all_patients.selection()
    add_monitored_patient(all_patients.item(item, "values"))


def duplicate_item(tree, item):
    children = tree.get_children('')
    for child in children:
        values = tree.item(child, "values")
        if values == item:
            return True
    return False


# Assign some dummy data
client = CholesterolDataClient("https://fhir.monash.edu/hapi-fhir-jpaserver/fhir/")
health_practitioner = "Dr. James Smith"

# Create the main Tkinter UI
main_UI = tk.Tk("Cholesterol Monitor")
entry_label = tk.Label(main_UI, text="Enter your ID")
entry_label.grid(row=0, column=0)
entry_field = tk.Entry(main_UI)
entry_field.grid(row=0, column=1)
get_patients_button = tk.Button(main_UI, text="Get patients", width=15, command=get_patients)
get_patients_button.grid(row=0, column=2)


# create all patients treeview
all_patients = ttk.Treeview(main_UI, columns="Name", show='headings')
all_patients.heading("Name", text="Name")
all_patients.grid(row=1, column=0, columnspan=1)
all_patients.bind("<Double-1>", on_all_patients_double_click)

# create monitored patients treeview with 3 columns
cols = ('Name', 'Total Cholesterol', 'Time')
monitored_patients = ttk.Treeview(main_UI, columns=cols, show='headings')

# set column headings
for col in cols:
    monitored_patients.heading(col, text=col)
monitored_patients.grid(row=1, column=1, columnspan=3)
monitored_patients.bind("<Double-1>", remove_monitored_patient)

closeButton = tk.Button(main_UI, text="Close", width=15, command=exit).grid(row=4, column=2)

# Run main UI
main_UI.mainloop()
