import tkinter as tk
from tkinter import ttk
from tkinter import messagebox
from src.fhir_module import *
import asyncio
from threading import *


class App:
    def __init__(self):
        self.practitioner = None
        self.client = None
        self.update_interval = None

    def set_client(self, client):
        self.client = client

    def set_practitioner(self, practitioner):
        self.practitioner = practitioner

    def set_interval(self, interval):
        self.update_interval = interval


def get_patients(event=None):
    practitioner_id = entry_field.get()
    try:
        if practitioner_id == "":
            raise KeyError

        current_practitioner = client.get_practitioner_info(practitioner_id)
        # Updating the UI with the practitioner's name
        practitioner_name = "Dr. " + current_practitioner.first_name + " " + current_practitioner.last_name
        label = tk.Label(main_UI, text=practitioner_name)
        entry_field.destroy()
        entry_label.destroy()
        get_patients_button.destroy()
        label.grid(row=0, column=0, columnspan=4)

        # get the practitioner's patient list
        current_practitioner.get_patient_list(client)
        patient_list = current_practitioner.get_all_patients()

        # display patient list
        for patient in patient_list.get_patient_list():
            patient_name = patient.first_name + " " + patient.last_name
            patient_data = patient.get_data()
            cholesterol_level = str(patient_data[0]) + " " + patient_data[1]
            effective_time = patient_data[2]
            new_entry = (patient_name, cholesterol_level, effective_time)
            if not duplicate_item(all_patients, new_entry):
                all_patients.insert("", "end", values=new_entry)

        application.set_practitioner(current_practitioner)
    except KeyError:
        messagebox.showinfo("Error", "Invalid practitioner identifier")


def highlight_patients():
    children = monitored_patients.get_children('')
    for child in children:
        values = monitored_patients.item(child, "values")
        patient_cholesterol = values[1].split(' ')[0]
        if not patient_cholesterol.isdigit():
            if float(patient_cholesterol) == application.practitioner.monitored_patients.average_cholesterol_level:
                monitored_patients.item(child, tags=('high',))

    monitored_patients.tag_configure('high', foreground='#E8E8E8')


def update_data():
    patient_list = application.practitioner.get_monitored_patients()
    children = monitored_patients.get_children('')

    # for each item, collect corresponding patient data and update
    for child in children:
        values = monitored_patients.item(child, "values")
        current_patient = patient_list.select_patient(values[0])
        patient_data = current_patient.get_data()
        update_entry = (values[0], str(patient_data[0])+" "+patient_data[1], patient_data[2])
        monitored_patients.item(child, values=update_entry)

    highlight_patients()


def display_patient_info(event=None):
    item = monitored_patients.selection()
    values = monitored_patients.item(item, "values")
    try:
        patient = application.practitioner.get_monitored_patients().select_patient(values[0])
    except AttributeError:
        return
    except IndexError:
        return

    if patient is None:
        return

    info_window = tk.Toplevel()
    info_window.title(patient.first_name+" "+patient.last_name)
    cols = ("Birthdate", "Gender", "Address")
    patient_info = ttk.Treeview(info_window, columns=cols, show='headings')
    for col in cols:
        patient_info.heading(col, text=col)
        if col == "Address":
            patient_info.column(col, width=400)
        else:
            patient_info.column(col, width=80)
    patient_info.grid(row=0, column=0)
    new_entry = (patient.birth_date, patient.gender, patient.get_address())
    patient_info.insert("", "end", values=new_entry)


async def get_patient_data():
    while True:
        application.practitioner.get_patient_data(application.client)
        update_data()
        await asyncio.sleep(application.update_interval)


def remove_monitored_patient(event=None):
    item = monitored_patients.selection()
    monitored_patients.delete(item)


def add_monitored_patient(event=None):
    item = all_patients.selection()
    try:
        patient = all_patients.item(item, "values")
        new_entry = (patient[0], patient[1], patient[2])
        if not duplicate_item(monitored_patients, new_entry):
            monitored_patients.insert("", "end", values=new_entry)
            application.practitioner.add_patient_monitor(patient[0])
            highlight_patients()
    except IndexError:
        return
    except ValueError:
        print("No patient data for " + patient[0])


def duplicate_item(tree, item):
    children = tree.get_children('')
    for child in children:
        values = tree.item(child, "values")
        if values == item:
            return True
    return False


if __name__ == '__main__':
    # create application object
    application = App()

    # Assign some dummy data
    client = CholesterolDataClient("https://fhir.monash.edu/hapi-fhir-jpaserver/fhir/")
    application.set_client(client)

    # Create the main Tkinter UI
    main_UI = tk.Tk("Cholesterol Monitor")
    entry_label = tk.Label(main_UI, text="Enter your ID")
    entry_label.grid(row=0, column=0)
    entry_field = tk.Entry(main_UI)
    entry_field.grid(row=0, column=1)
    entry_field.bind("<Return>", get_patients)
    get_patients_button = tk.Button(main_UI, text="Get patients", width=15, command=get_patients)
    get_patients_button.grid(row=0, column=2)

    # create all patients treeview
    all_patients = ttk.Treeview(main_UI, columns="Name", show='headings')
    all_patients.heading("Name", text="Name")
    all_patients.grid(row=1, column=0, columnspan=1)
    all_patients.bind("<Double-1>", add_monitored_patient)

    # create monitored patients treeview with 3 columns
    cols = ('Name', 'Total Cholesterol', 'Time')
    monitored_patients = ttk.Treeview(main_UI, columns=cols, show='headings')
    for col in cols:
        monitored_patients.heading(col, text=col)
    monitored_patients.grid(row=1, column=1, columnspan=3)
    monitored_patients.bind("<Double-1>", display_patient_info)

    # create buttons
    add_patient_button = tk.Button(main_UI, text="Add Monitor", width=15, command=add_monitored_patient)
    add_patient_button.grid(row=4, column=0)
    close_button = tk.Button(main_UI, text="Close", width=15, command=exit)
    close_button.grid(row=4, column=3)
    more_info_button = tk.Button(main_UI, text="More Info", width=15, command=display_patient_info)
    more_info_button.grid(row=4, column=1)
    remove_patient_button = tk.Button(main_UI, text="Remove Monitor", width=15, command=remove_monitored_patient)
    remove_patient_button.grid(row=4, column=2)

    # Run main UI
    main_UI.mainloop()
