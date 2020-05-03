import tkinter as tk
from tkinter import ttk


def get_patients():
    for patient in patient_list:
        if not duplicate_item(all_patients, patient):
            all_patients.insert("", "end", values=patient)


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
health_practitioner = "Dr. James Smith"
patient_list = [('ZHANG WEI', '20 mg/dL', '2005-09-27 48:33+10:00'),
                ('ANIKA AADESH', '33 mg/dL', '2015-09-07 48:33+12:00'),
                ('HILAL AKAY', '12 mg/dL', '2015-09-17 48:33+11:00')]

# Create the main Tkinter UI
main_UI = tk.Tk("Cholesterol Monitor")
label = tk.Label(main_UI, text=health_practitioner, font=("Arial", 20)).grid(row=0, columnspan=3)

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
monitored_patients.grid(row=1, column=1, columnspan=2)
monitored_patients.bind("<Double-1>", remove_monitored_patient)

getPatients = tk.Button(main_UI, text="Get patients", width=15, command=get_patients).grid(row=4, column=0)
closeButton = tk.Button(main_UI, text="Close", width=15, command=exit).grid(row=4, column=2)

# Run main UI
main_UI.mainloop()
