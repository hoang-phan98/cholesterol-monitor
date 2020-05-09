import threading
import tkinter as tk
from tkinter import ttk
from tkinter import messagebox
from src.fhir_module import *
import pickle
import time
from PIL import ImageTk, Image


class App:
    def __init__(self):
        self.practitioner = None
        self.client = None
        self.update_interval = 5
        self.subthread = None

    def set_client(self, client):
        self.client = client

    def set_practitioner(self, practitioner):
        self.practitioner = practitioner

    def set_interval(self, interval):
        self.update_interval = interval


def fixed_map(option, style):
    # Fix for setting text colour for Tkinter 8.6.9
    # From: https://core.tcl.tk/tk/info/509cafafae
    #
    # Returns the style map for 'option' with any styles starting with
    # ('!disabled', '!selected', ...) filtered out.

    # style.map() returns an empty list for missing options, so this
    # should be future-safe.
    return [elm for elm in style.map('Treeview', query_opt=option) if
      elm[:2] != ('!disabled', '!selected')]


def get_patients(event=None):
    """
    Retrieve and display the list of all patients of the practitioner with the given identifier
    First try to load data from local storage, if not found, request from server
    """
    practitioner_id = entry_field.get()

    try:
        if practitioner_id == "":
            raise KeyError

        try:
            filename = "Practitioner Data/" + practitioner_id
            file = open(filename, 'rb')
            current_practitioner = pickle.load(file)
            file.close()
        except FileNotFoundError:
            print("No data found in storage, requesting from server...")
            current_practitioner = client.get_practitioner_info(practitioner_id)
            current_practitioner.get_patient_list(client)

        # Updating the UI with the practitioner's name and time interval input
        entry_field.destroy()
        entry_label.destroy()
        get_patients_button.destroy()
        practitioner_name = "Dr. " + current_practitioner.first_name + " " + current_practitioner.last_name
        label = tk.Label(main_UI, text=practitioner_name)
        label.grid(row=0, column=0)
        interval_entry_label = tk.Label(main_UI, text="Current update interval: "+str(application.update_interval))
        interval_entry_label.grid(row=0, column=1)
        global time_entry_field
        time_entry_field = tk.Entry(main_UI)
        time_entry_field.grid(row=0, column=2)
        time_entry_field.bind("<Return>", set_update_interval)
        time_entry_button = tk.Button(main_UI, text="Set update interval", width=15, command=set_update_interval)
        time_entry_button.grid(row=0, column=3)

        # get the practitioner's patient list
        patient_list = current_practitioner.get_all_patients()

        # display patient list
        for patient in patient_list.get_patient_list():
            # Assign patient name
            patient_name = patient.first_name + " " + patient.last_name
            # Assign patient data values
            patient_data = patient.get_data()
            cholesterol_level = str(patient_data[0]) + " " + patient_data[1]
            effective_time = patient_data[2]
            # Assign new entry values
            new_entry = (patient_name, cholesterol_level, effective_time)

            # Insert into treeview if the patient does not already exist
            if not duplicate_item(all_patients, new_entry):
                all_patients.insert("", "end", values=new_entry)

        # Start a separate thread to update the patient's data concurrently
        application.set_practitioner(current_practitioner)
        application.subthread = threading.Thread(target=get_patient_data)
        application.subthread.setDaemon(True)
        application.subthread.start()

    except KeyError:
        messagebox.showinfo("Error", "Invalid practitioner identifier")


def set_update_interval(event=None):
    """
    Set the update interval for requesting patient's data from the server
    """
    application.set_interval(int(time_entry_field.get()))
    interval_entry_label = tk.Label(main_UI, text="Current update interval: " + str(application.update_interval))
    interval_entry_label.grid(row=0, column=1)


def update_data(tree):
    """
    Request new data from the server for each patient in the practitioner's monitored patients list
    Update the information in the GUI display accordingly
    """
    # Get the practitioner's list of monitored patients
    patient_list = application.practitioner.get_monitored_patients()
    children = tree.get_children('')

    # for each item, collect corresponding patient data and update
    for child in children:
        values = tree.item(child, "values")
        # Get patient and patient data based on their full name
        current_patient = patient_list.select_patient(values[0])
        patient_data = current_patient.get_data()
        # Update table with newly retrieved patient data
        update_entry = (values[0], str(patient_data[0])+" "+patient_data[1], patient_data[2])
        tree.item(child, values=update_entry)

    # Highlight patients with abnormal cholesterol value
    highlight_patients(tree)


def highlight_patients(tree):
    """
    Check the cholesterol level of each monitored patient
    If the level is higher than the average of all monitored patients, highlight this patient in red
    """
    try:
        children = tree.get_children('')
        for child in children:
            values = tree.item(child, "values")
            patient_cholesterol = values[1].split(' ')[0]
            try:
                if float(patient_cholesterol) > application.practitioner.get_monitored_patients().average_cholesterol_level:
                    tree.item(child, tags=['high'])
                    tree.tag_configure('high', foreground='red')
            except ValueError:
                continue
    except tk.TclError:
        return


def display_patient_info(event=None):
    """
    Display the selected patient's personal info in a pop-up window
    """
    item = monitored_patients.selection()
    values = monitored_patients.item(item, "values")
    try:
        # Select patient from the list
        patient = application.practitioner.get_monitored_patients().select_patient(values[0])
    except AttributeError:
        return
    except IndexError:
        return
    if patient is None:
        return

    # Create a pop-up window to display patient's personal info
    info_window = tk.Toplevel()
    info_window.title(patient.first_name+" "+patient.last_name)
    cols = ("Birth date", "Gender", "Address")
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


def get_patient_data():
    """
    Request new patient data from server and update display every N seconds
    """
    while True:
        # Execute if there's at least one patient being monitored
        if len(application.practitioner.get_monitored_patients()) > 0:
            application.practitioner.get_patient_data(application.client)
            update_data(monitored_patients)
            time.sleep(application.update_interval)


def remove_monitored_patient(event=None):
    """
    Remove a patient from the list of monitored patients
    also remove the patient to the practitioner's monitored patients list object
    """
    item = monitored_patients.selection()
    values = monitored_patients.item(item, "values")
    # Remove item from practitioner's monitored patient list
    application.practitioner.remove_patient_monitor(values[0])
    # Remove item from treeview
    monitored_patients.delete(item)


def add_monitored_patient(event=None):
    """
    Add a patient from the list of all patients to the list of monitored patients
    also add the patient to the practitioner's monitored patients list object
    """
    item = all_patients.selection()
    try:
        patient = all_patients.item(item, "values")
        new_entry = (patient[0], patient[1], patient[2])
        if not duplicate_item(monitored_patients, new_entry):
            # Add patient to treeview
            monitored_patients.insert("", "end", values=new_entry)
            # Add patient to practitioner's monitored patient list
            application.practitioner.add_patient_monitor(patient[0])
            highlight_patients(monitored_patients)
    except IndexError:
        return
    except ValueError:
        print("No patient data for " + patient[0])


def duplicate_item(tree, item):
    """
    Checks whether an item already exists in the Treeview
    :param tree: tkinter Treeview
    :param item: an item to be added
    :return: True if item already in list of children, False otherwise
    """
    children = tree.get_children('')
    for child in children:
        values = tree.item(child, "values")
        if values == item:
            return True
    return False


def exit_program():
    """
    Close the program and persists current practitioner's data using pickle
    """
    try:
        # Clear the practitioner's monitored patient list for next run
        application.practitioner.clear_monitor()
        # Copy the practitioner object to a binary file
        filename = "Practitioner Data/"+str(application.practitioner.id)
        outfile = open(filename, 'wb')
        pickle.dump(application.practitioner, outfile)
        outfile.close()
        exit(0)
    except AttributeError:
        exit(0)


if __name__ == '__main__':
    # create application object
    application = App()

    # Assign some dummy data
    client = CholesterolDataClient("https://fhir.monash.edu/hapi-fhir-jpaserver/fhir/")
    application.set_client(client)

    # Create the main Tkinter UI
    main_UI = tk.Tk("Cholesterol Monitor")
    main_UI.title("Quarantine Coders' Application")
    entry_icon = ImageTk.PhotoImage(Image.open("Monash_Uni_Logo.png"))
    main_UI.iconphoto(True, entry_icon)
    entry_label = tk.Label(main_UI, text="Enter your ID")
    entry_label.grid(row=0, column=0)
    entry_field = tk.Entry(main_UI)
    entry_field.grid(row=0, column=1)
    entry_field.bind("<Return>", get_patients)
    get_patients_button = tk.Button(main_UI, text="Get patients", width=15, command=get_patients)
    get_patients_button.grid(row=0, column=2)
    global time_entry_field

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
    close_button = tk.Button(main_UI, text="Close", width=15, command=exit_program)
    close_button.grid(row=4, column=3)
    more_info_button = tk.Button(main_UI, text="More Info", width=15, command=display_patient_info)
    more_info_button.grid(row=4, column=1)
    remove_patient_button = tk.Button(main_UI, text="Remove Monitor", width=15, command=remove_monitored_patient)
    remove_patient_button.grid(row=4, column=2)

    style = ttk.Style()
    style.map('Treeview', foreground=fixed_map('foreground', style),
              background=fixed_map('background', style))

    # Run main UI
    main_UI.mainloop()
