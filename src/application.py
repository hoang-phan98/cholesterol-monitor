import tkinter as tk
from tkinter import ttk
from tkinter import messagebox
from src.fhir_module import *
from PIL import ImageTk, Image
import pickle
import time
import threading
import matplotlib
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure
from abc import ABC, abstractmethod
matplotlib.use("TkAgg")


class Observer(ABC):
    def set_subject(self, subject):
        self._subject = subject

    @abstractmethod
    def update(self):
        pass


class GraphicalMonitor(Observer, Figure):

    def update(self):
        if self._subject is not None:  # If subject has not been specified, do nothing
            self.show()


class CholesterolMonitor(Observer, ttk.Treeview):
    """
    This class is the table which displays all of the patients being monitored and their data
    It observes the monitored patient list and update its display accordingly
    """

    def update(self):
        """
        Update the view according to the Patient List object being observed
        :return: None
        """
        if self._subject is not None:  # If subject has not been specified, do nothing
            children = self.get_children('')
            for item in children:
                values = self.item(item, "values")
                patient_name = values[0]
                current_patient = self._subject.select_patient(patient_name)
                if is_new_cholesterol_data(values, current_patient):  # Check if the new values are different
                    self.item(item, values=format_data(current_patient)[:3])  # update the display with new data


class BloodPressureMonitor(Observer, ttk.Treeview):
    """
    This class is the table which displays all of the patients being monitored and their data
    It observes the monitored patient list and update its display accordingly
    """

    def update(self):
        """
        Update the view according to the Patient List object being observed
        :return: None
        """
        if self._subject is not None:  # If subject has not been specified, do nothing
            children = self.get_children('')
            for item in children:
                values = self.item(item, "values")
                patient_name = values[0]
                current_patient = self._subject.select_patient(patient_name)
                if is_new_blood_pressure_data(values, current_patient):  # Check if the new values are different
                    self.item(item, values=format_data(current_patient)[3:])  # update the display with new data


class HistoricalSystolicMonitor(Observer, ttk.Treeview):
    """
    This class is a table which displays the latest 5 systolic blood pressure observations for all patients with
    a high systolic blood pressure level
    """

    def update(self):
        """
        Update the table according to the Patient List object being observed
        :return: None
        """
        if self._subject is not None:  # If subject has not been specified, do nothing
            children = self.get_children('')
            for item in children:
                values = self.item(item, "values")
                patient_name = values[0]
                current_patient = self._subject.select_patient(patient_name)
                new_data = format_historical_systolic_data(current_patient)
                if new_data != values:  # Check if the new values are different
                    self.item(item, values=new_data)  # update the display with new data


class App:
    """
    Driver class which contains the logged in practitioner, client and UI components
    """

    def __init__(self):
        self.practitioner = None
        self.cholesterol_client = None
        self.blood_pressure_client = None
        self.update_interval = 5
        self.systolic_limit = '125'
        self.diastolic_limit = '80'
        self.main_UI = None
        self.entry_field = None
        self.entry_label = None
        self.get_patients_button = None
        self.time_entry_button = None
        self.time_entry_field = None
        self.time_entry_label = None
        self.all_patients = None
        self.cholesterol_monitor = None
        self.systolic_limit_field = None
        self.systolic_limit_label = None
        self.diastolic_limit_field = None
        self.diastolic_limit_label = None
        self.blood_pressure_monitor = None
        self.cholesterol_graphical_monitor = None
        self.BP_graphical_monitor = None
        self.selected_monitor_option = None
        self.option_menu = None

    def set_cholesterol_client(self, client):
        self.cholesterol_client = client

    def set_blood_pressure_client(self, client):
        self.blood_pressure_client = client

    def set_practitioner(self, practitioner):
        self.practitioner = practitioner

    def set_systolic_limit(self, event=None):
        """Set the systolic limit entered and update the display"""

        # Get value from entry field and update the app's attribute
        systolic_limit = self.systolic_limit_field.get()
        self.systolic_limit = float(systolic_limit)

        # Update the display
        self.systolic_limit_label.destroy()
        self.systolic_limit_label = tk.Label(self.main_UI, text="Systolic BP Limit: " + str(self.systolic_limit))
        self.systolic_limit_label.grid(row=0, column=4, rowspan=2)

        # Highlight the patients based on the new limit
        self.highlight_patients()

    def set_diastolic_limit(self, event=None):
        """Set the diastolic limit entered and update the display"""

        # Get value from entry field and update the app's attribute
        diastolic_limit = self.diastolic_limit_field.get()
        self.diastolic_limit = float(diastolic_limit)

        # Update the display
        self.diastolic_limit_label.destroy()
        self.diastolic_limit_label = tk.Label(self.main_UI, text="Diastolic BP Limit: " + str(self.diastolic_limit))
        self.diastolic_limit_label.grid(row=0, column=6, rowspan=2)

        # Highlight the patients based on the new limit
        self.highlight_patients()

    def run(self):
        """
        Initializes the GUI display
        :return: None
        """
        # Create the main Tkinter UI
        self.main_UI = tk.Tk("Cholesterol Monitor")
        self.main_UI.title("Quarantine Coders' Application")
        entry_icon = ImageTk.PhotoImage(Image.open("Monash_Uni_Logo.png"))
        self.main_UI.iconphoto(True, entry_icon)
        self.entry_label = tk.Label(self.main_UI, text="Enter your identifier")
        self.entry_label.grid(row=0, column=0)
        self.entry_field = tk.Entry(self.main_UI)
        self.entry_field.grid(row=0, column=1)
        self.entry_field.bind("<Return>", self.practitioner_login)
        self.get_patients_button = tk.Button(self.main_UI, text="Get patients", width=15,
                                             command=self.practitioner_login)
        self.get_patients_button.grid(row=0, column=2)

        # create all patients treeview
        self.all_patients = ttk.Treeview(self.main_UI, columns="Name", show='headings')
        self.all_patients.heading("Name", text="Name")
        self.all_patients.column("Name", width=150)
        self.all_patients.grid(row=2, column=0, columnspan=1)
        self.all_patients.bind("<Double-1>", self.add_monitored_patient)

        # create cholesterol monitor treeview
        cols = ('Name', 'Total Cholesterol', 'Time')
        self.cholesterol_monitor = CholesterolMonitor(self.main_UI, columns=cols, show='headings')
        for col in cols:
            self.cholesterol_monitor.heading(col, text=col)
            self.cholesterol_monitor.column(col, width=150)
        self.cholesterol_monitor.grid(row=2, column=1, columnspan=3)
        self.cholesterol_monitor.bind("<Double-1>", self.display_patient_info)
        self.cholesterol_monitor.bind("<Delete>", self.remove_monitored_patient)

        # create blood pressure monitor treeview
        cols = ('Name', 'Systolic Blood Pressure', 'Diastolic Blood Pressure', 'Time')
        self.blood_pressure_monitor = BloodPressureMonitor(self.main_UI, columns=cols, show='headings')
        for col in cols:
            self.blood_pressure_monitor.heading(col, text=col)
        self.blood_pressure_monitor.grid(row=2, column=4, columnspan=4)
        self.blood_pressure_monitor.bind("<Delete>", self.remove_monitored_patient)

        # create buttons
        add_patient_button = tk.Button(self.main_UI, text="Add Monitor", width=15, command=self.add_monitored_patient)
        add_patient_button.grid(row=4, column=0)
        close_button = tk.Button(self.main_UI, text="Close", width=15, command=self.exit_program)
        close_button.grid(row=4, column=6)
        more_info_button = tk.Button(self.main_UI, text="More Info", width=15, command=self.display_patient_info)
        more_info_button.grid(row=4, column=1)
        remove_patient_button = tk.Button(self.main_UI, text="Remove Monitor", width=15,
                                          command=self.remove_monitored_patient)
        remove_patient_button.grid(row=4, column=2)
        graph_cholesterol_button = tk.Button(self.main_UI, text="Graph Cholesterol", width=15,
                                             command=self.cholesterol_graph)
        graph_cholesterol_button.grid(row=4, column=3)
        graph_blood_pressure_button = tk.Button(self.main_UI, text="Graph Blood Pressure", width=20,
                                                command=self.blood_pressure_graph)
        graph_blood_pressure_button.grid(row=4, column=4)
        monitor_blood_pressure_button = tk.Button(self.main_UI, text="Monitor Blood Pressure", width=20,
                                                  command=self.monitor_blood_pressure)
        monitor_blood_pressure_button.grid(row=4, column=5)

        # Fix highlighting bug
        style = ttk.Style()
        style.map('Treeview', foreground=fixed_map('foreground', style),
                  background=fixed_map('background', style))

        # Run main UI
        self.main_UI.mainloop()

    def practitioner_login(self, event=None):
        """
        Retrieve and display the list of all patients of the practitioner with the given identifier
        First try to load data from local storage, if not found, request from server
        """

        # Get practitioner id from entry field
        practitioner_id = self.entry_field.get()

        try:
            if practitioner_id == "":  # if no identifier specified
                raise KeyError
            try:
                # Try to get load data from local storage
                filename = "Practitioner Data/" + practitioner_id
                file = open(filename, 'rb')
                current_practitioner = pickle.load(file)
                file.close()
            except FileNotFoundError:
                print("No data found in storage, requesting from server...")
                current_practitioner = self.cholesterol_client.get_practitioner_info(practitioner_id)
                current_practitioner.get_patient_list(self.cholesterol_client)

                # Retrieve and update patient data from the server
                for patient in current_practitioner.get_all_patients().get_patient_list():
                    cholesterol_data = self.cholesterol_client.get_patient_data(patient.id)
                    blood_pressure_data = self.blood_pressure_client.get_patient_data(patient.id)
                    patient.update_data(cholesterol_data)
                    patient.update_data(blood_pressure_data)

            # Updating the UI with the practitioner's name and time interval input
            self.entry_field.destroy()
            self.entry_label.destroy()
            self.get_patients_button.destroy()
            practitioner_name = "Dr. " + current_practitioner.first_name + " " + current_practitioner.last_name
            label = tk.Label(self.main_UI, text=practitioner_name)
            label.grid(row=0, column=0, rowspan=2)

            # Select monitor type
            monitor_options = ["Cholesterol", "Blood Pressure", "Both"]
            self.selected_monitor_option = tk.StringVar(self.main_UI)
            self.selected_monitor_option.set(monitor_options[0])
            self.option_menu = tk.OptionMenu(self.main_UI, self.selected_monitor_option, *monitor_options)
            self.option_menu.grid(row=0, column=3)
            update_monitor_button = tk.Button(self.main_UI, text="Update Monitor", width=15, command=self.update_monitor)
            update_monitor_button.grid(row=1, column=3)

            # Time interval entry
            self.time_entry_label = tk.Label(self.main_UI, text="Current update interval: " + str(self.update_interval))
            self.time_entry_label.grid(row=0, column=1, rowspan=2)
            self.time_entry_field = tk.Entry(self.main_UI, width=15)
            self.time_entry_field.grid(row=0, column=2)
            self.time_entry_field.bind("<Return>", self.set_update_interval)
            self.time_entry_button = tk.Button(self.main_UI, text="Set update interval", width=15,
                                               command=self.set_update_interval)
            self.time_entry_button.grid(row=1, column=2)

            # Systolic Limit entry
            self.systolic_limit_label = tk.Label(self.main_UI, text="Systolic BP Limit: " + str(self.systolic_limit))
            self.systolic_limit_label.grid(row=0, column=4, rowspan=2)
            self.systolic_limit_field = tk.Entry(self.main_UI, width=15)
            self.systolic_limit_field.grid(row=0, column=5)
            systolic_limit_button = tk.Button(self.main_UI, text="Set Systolic limit", width=15,
                                              command=self.set_systolic_limit)
            systolic_limit_button.grid(row=1, column=5)

            # Diastolic Limit entry
            self.diastolic_limit_label = tk.Label(self.main_UI, text="Diastolic BP Limit: " + str(self.diastolic_limit))
            self.diastolic_limit_label.grid(row=0, column=6, rowspan=2)
            self.diastolic_limit_field = tk.Entry(self.main_UI, width=15)
            self.diastolic_limit_field.grid(row=0, column=7)
            diastolic_limit_button = tk.Button(self.main_UI, text="Set Diastolic limit", width=15,
                                               command=self.set_diastolic_limit)
            diastolic_limit_button.grid(row=1, column=7)

            # Get the practitioner's patient list
            patient_list = current_practitioner.get_all_patients()

            # display patient list
            for patient in patient_list.get_patient_list():
                # Insert into treeview if the patient does not already exist
                if not duplicate_item(self.all_patients, format_data(patient)):
                    self.all_patients.insert("", "end", values=format_data(patient))

            # Start a separate thread to update the patient's data concurrently
            self.set_practitioner(current_practitioner)
            subthread = threading.Thread(target=self.request_patient_data)
            subthread.setDaemon(True)
            subthread.start()

            # Attach monitored patient list to treeview observer
            self.practitioner.get_monitored_patients().attach(self.cholesterol_monitor)
            self.practitioner.get_monitored_patients().attach(self.blood_pressure_monitor)

        except KeyError:
            messagebox.showinfo("Error", "Invalid practitioner identifier")

    def set_update_interval(self, event=None):
        """
        Set the update interval for requesting patient's data from the server
        """
        # get interval value from entry field
        update_interval = int(self.time_entry_field.get())
        self.update_interval = update_interval
        self.time_entry_label.destroy()
        self.time_entry_label = tk.Label(self.main_UI, text="Current update interval: " +
                                                            str(self.update_interval))
        self.time_entry_label.grid(row=0, column=1, rowspan=2)

    def exit_program(self):
        """
        Close the program and persists current practitioner's data using pickle
        """
        try:
            # Clear the practitioner's monitored patient list for next run
            self.practitioner.clear_monitor()
            # Copy the practitioner object to a binary file
            filename = "Practitioner Data/" + str(self.practitioner.id)
            outfile = open(filename, 'wb')
            pickle.dump(self.practitioner, outfile)
            outfile.close()
            exit(0)
        except AttributeError:
            exit(0)

    def request_patient_data(self):
        """
        Request new patient data from server depending on monitor type and update display every N seconds
        """
        while True:
            # Execute if there's at least one patient being monitored
            if len(self.practitioner.get_monitored_patients()) > 0:

                # Request data from server depending on monitor option
                if self.selected_monitor_option.get() == "Cholesterol" or self.selected_monitor_option.get() == "Both":
                    print("Requesting cholesterol data for " +
                          str(len(self.practitioner.get_monitored_patients().get_patient_list())) + " patient(s)")
                    self.practitioner.get_patient_data(self.cholesterol_client)
                if self.selected_monitor_option.get() == "Blood Pressure" or self.selected_monitor_option.get() == "Both":
                    print("Requesting blood pressure data for " +
                          str(len(self.practitioner.get_monitored_patients().get_patient_list())) + " patient(s)")
                    self.practitioner.get_patient_data(self.blood_pressure_client)

                # Notify Treeview observer of data changes
                try:
                    self.practitioner.get_monitored_patients().notify()
                except AttributeError:
                    time.sleep(1)

                self.highlight_patients()
                self.cholesterol_graph_data()
                self.blood_pressure_graph_data()

                # Sleep
                time.sleep(self.update_interval)

    def add_monitored_patient(self, event=None):
        """
        Add a patient from the list of all patients to the relevant monitor(s)
        also add the patient to the practitioner's monitored patients list object
        """
        selected = self.all_patients.selection()
        values = None
        for item in selected:
            try:
                values = self.all_patients.item(item, "values")
                if not duplicate_item(self.cholesterol_monitor, values[:3]) and \
                        not duplicate_item(self.blood_pressure_monitor, values[3:]):

                    # Add patient to treeview depending on monitor option
                    if self.selected_monitor_option.get() == "Cholesterol" or self.selected_monitor_option.get() == "Both":
                        self.cholesterol_monitor.insert("", "end", values=values[:3])
                    if self.selected_monitor_option.get() == "Blood Pressure" or self.selected_monitor_option.get() == "Both":
                        self.blood_pressure_monitor.insert("", "end", values=values[3:])

                    # Add patient to practitioner's monitored patient list
                    self.practitioner.add_patient_monitor(values[0])
                    self.highlight_patients()
            except IndexError:
                return
            except ValueError:
                print("No patient data for " + values[0])

    def remove_monitored_patient(self, event=None):
        """
        Remove a patient from the list of monitored patients
        also remove the patient to the practitioner's monitored patients list object
        """
        try:

            # Prioritize selection from cholesterol monitor
            selected = self.cholesterol_monitor.selection()
            if len(selected) == 0:
                # If no selection from cholesterol monitor, try blood pressure monitor
                selected = self.blood_pressure_monitor.selection()

            # For each selected patients
            for item in selected:

                try:
                    # Get the values from cholesterol monitor
                    values = self.cholesterol_monitor.item(item, "values")

                    # Remove item from practitioner's monitored patient list
                    self.practitioner.remove_patient_monitor(values[0])

                    # Remove item from Cholesterol monitor
                    index = self.cholesterol_monitor.get_children().index(item)
                    self.cholesterol_monitor.delete(item)

                    # Remove the same item from BP monitor
                    item = self.blood_pressure_monitor.get_children()[index]
                    self.blood_pressure_monitor.delete(item)

                except tk.TclError:
                    # Get the values from BP monitor
                    values = self.blood_pressure_monitor.item(item, "values")

                    # Remove item from practitioner's monitored patient list
                    self.practitioner.remove_patient_monitor(values[0])

                    # Remove item from BP monitor
                    index = self.blood_pressure_monitor.get_children().index(item)
                    self.blood_pressure_monitor.delete(item)

                    # Remove the same item from Cholesterol monitor
                    item = self.cholesterol_monitor.get_children()[index]
                    self.cholesterol_monitor.delete(item)

            self.highlight_patients()
        except IndexError:
            return

    def display_patient_info(self, event=None):
        """
        Display the selected patient's personal info in a pop-up window
        """
        # Prioritize selection from cholesterol monitor
        selected_patients = self.cholesterol_monitor.selection()
        if len(selected_patients) == 0:
            # If no selection from cholesterol monitor, try blood pressure monitor
            selected_patients = self.blood_pressure_monitor.selection()

        # For each selected patient
        for item in selected_patients:
            # Get the values from the cholesterol monitor
            try:
                values = self.cholesterol_monitor.item(item, "values")
            except tk.TclError:
                index = self.blood_pressure_monitor.get_children().index(item)
                item = self.cholesterol_monitor.get_children()[index]
                values = self.cholesterol_monitor.item(item, "values")

            # Select patient from the list
            try:
                patient = self.practitioner.get_monitored_patients().select_patient(values[0])
            except AttributeError:
                return
            except IndexError:
                return
            if patient is None:
                return

            # Create a pop-up window to display patient's personal info
            info_window = tk.Toplevel()
            info_window.title(patient.first_name + " " + patient.last_name)
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

    def highlight_patients(self):
        """
        For the cholesterol monitor:
        If the cholesterol level is higher than the average of all monitored patients, highlight this patient in red

        For the blood pressure monitor:
        If the systolic level is higher than the limit, highlight this patient in yellow
        If the diastolic level is higher than the limit, highlight this patient in blue
        If the both levels are higher than the limits, highlight this patient in purple
        """
        try:
            # Cholesterol Monitor
            children = self.cholesterol_monitor.get_children('')
            for child in children:
                values = self.cholesterol_monitor.item(child, "values")
                patient_cholesterol = values[1].split(' ')[0]
                try:
                    if float(
                            patient_cholesterol) > self.practitioner.get_monitored_patients().average_cholesterol_level:
                        self.cholesterol_monitor.item(child, tags=['high cholesterol'])
                    else:
                        self.cholesterol_monitor.item(child, tags=['normal'])
                    self.cholesterol_monitor.tag_configure('normal', foreground=None)
                    self.cholesterol_monitor.tag_configure('high cholesterol', foreground='red')
                except ValueError:
                    continue

            # Blood pressure monitor
            children = self.blood_pressure_monitor.get_children('')
            for child in children:
                values = self.blood_pressure_monitor.item(child, "values")
                patient_systolic_blood_pressure = values[1].split('mm')[0]
                patient_diastolic_blood_pressure = values[2].split('mm')[0]
                try:
                    if float(patient_systolic_blood_pressure) > float(self.systolic_limit) and \
                            float(patient_diastolic_blood_pressure) > float(self.diastolic_limit):
                        self.blood_pressure_monitor.item(child, tags=['high blood pressure'])
                    elif float(patient_systolic_blood_pressure) > float(self.systolic_limit):
                        self.blood_pressure_monitor.item(child, tags=['high systolic pressure'])
                    elif float(patient_diastolic_blood_pressure) > float(self.diastolic_limit):
                        self.blood_pressure_monitor.item(child, tags=['high diastolic pressure'])
                    else:
                        self.blood_pressure_monitor.item(child, tags=['normal'])

                    self.blood_pressure_monitor.tag_configure('normal', foreground=None)
                    self.blood_pressure_monitor.tag_configure('high systolic pressure', foreground='green')
                    self.blood_pressure_monitor.tag_configure('high diastolic pressure', foreground='blue')
                    self.blood_pressure_monitor.tag_configure('high blood pressure', foreground='purple')
                except ValueError:
                    continue

        except tk.TclError:
            return

    def cholesterol_graph_data(self, event=None):
        """
        Visually displays the monitored patients cholesterol levels in the form of a bar graph.
        """
        try:
            if self.practitioner is not None:
                patients = []
                patient_data = []
                children = self.cholesterol_monitor.get_children('')
                for child in children:
                    values = self.cholesterol_monitor.item(child, "values")
                    patient_cholesterol = values[1].split(' ')[0]
                    if patient_cholesterol != "-":
                        patient_data.append(float(patient_cholesterol))
                        patient_name = values[0]
                        patients.append(patient_name)
                X = patients
                Y = patient_data
                return (X, Y)

        except KeyError:
            messagebox.showinfo("Error", "No practitioner identifier given")

    def cholesterol_graph(self, event=None):

        graph_data = self.cholesterol_graph_data()
        self.cholesterol_graphical_monitor = GraphicalMonitor(figsize=(5, 5), dpi=100)
        subplot = self.cholesterol_graphical_monitor.add_subplot(1, 1, 1)
        bars = subplot.bar(graph_data[0], graph_data[1])
        subplot.set_title("Patient Cholesterol Data")
        subplot.set_xlabel("Patient Names")
        subplot.set_ylabel("Cholesterol Values (mg/dL)")
        self.practitioner.get_monitored_patients().attach(self.cholesterol_graphical_monitor)

        for bar in bars:
            yval = bar.get_height()
            subplot.text(bar.get_x(), yval + 1, yval)

        cholesterol_graph = tk.Toplevel()
        cholesterol_graph.title("Cholesterol Graph")
        canvas = FigureCanvasTkAgg(self.cholesterol_graphical_monitor, master=cholesterol_graph)
        canvas.get_tk_widget().grid()

    def blood_pressure_graph_data(self, event=None):
        """
        Visually displays the monitored patients blood pressure levels in the form of a line graph.
        """
        try:
            if self.practitioner is not None:
                patients = []
                patient_systolic_data = []
                patient_diastolic_data = []
                children_blood_pressure = self.blood_pressure_monitor.get_children('')
                children_cholesterol = self.cholesterol_monitor.get_children('')
                for child in children_blood_pressure:
                    values = self.blood_pressure_monitor.item(child, "values")
                    patient_systolic_blood_pressure = values[1].split('m')[0]
                    patient_diastolic_blood_pressure = values[2].split('m')[0]
                    if patient_systolic_blood_pressure != "-" and patient_diastolic_blood_pressure != "-":
                        patient_systolic_data.append(float(patient_systolic_blood_pressure))
                        patient_diastolic_data.append(float(patient_diastolic_blood_pressure))

                for child in children_cholesterol:
                    values = self.cholesterol_monitor.item(child, "values")
                    patient_cholesterol = values[1].split(' ')[0]
                    patient_name = values[0]
                    if patient_cholesterol != "-":
                        patients.append(patient_name)

                X = patients
                Y1 = patient_systolic_data
                Y2 = patient_diastolic_data
                return (X, Y1, Y2)

        except KeyError:
            messagebox.showinfo("Error", "No practitioner identifier given")

    def blood_pressure_graph(self, event=None):

        try:
            graph_data = self.blood_pressure_graph_data()
            self.BP_graphical_monitor = GraphicalMonitor(figsize=(10, 5), dpi=100)
            subplot1 = self.BP_graphical_monitor.add_subplot(1, 2, 1)
            bars1 = subplot1.bar(graph_data[0], graph_data[1])
            subplot1.set_title("Patient Systolic Data")
            subplot1.set_xlabel("Patient Names")
            subplot1.set_ylabel("Systolic Blood Pressure Values (mmHg)")

            subplot2 = self.BP_graphical_monitor.add_subplot(1, 2, 2)
            bars2 = subplot2.bar(graph_data[0], graph_data[2])
            subplot2.set_title("Patient Diastolic Data")
            subplot2.set_xlabel("Patient Names")
            subplot2.set_ylabel("Diastolic Blood Pressure Values (mmHg)")
            self.practitioner.get_monitored_patients().attach(self.BP_graphical_monitor)

            for bar1 in bars1:
                yval1 = bar1.get_height()
                subplot1.text(bar1.get_x(), yval1 + 1, yval1)

            for bar2 in bars2:
                yval2 = bar2.get_height()
                subplot2.text(bar2.get_x(), yval2 + 1, yval2)

            blood_pressure_graphs = tk.Toplevel()
            blood_pressure_graphs.title("Blood Pressure Graphs")
            canvas = FigureCanvasTkAgg(self.BP_graphical_monitor, master=blood_pressure_graphs)
            canvas.get_tk_widget().grid()

        except ValueError:
            print("Can't compute this graph, as there is not enough data")

    def monitor_blood_pressure(self, event=None):
        """
        Displays the selected patient's latest systolic blood pressure observations in a pop-up window, gives the
        option to visually represent the data in the form of a line graph.
        """

        # Create a pop-up window to display latest blood pressure values
        info_window = tk.Toplevel()
        info_window.title("Blood Pressure Monitor")
        cols = ("Name", "Latest systolic blood pressure observations")
        patient_info = HistoricalSystolicMonitor(info_window, columns=cols, show='headings')
        for col in cols:
            patient_info.heading(col, text=col)
            if col == "Latest systolic blood pressure observations":
                patient_info.column(col, width=1000)
            else:
                patient_info.column(col, width=100)
        patient_info.grid(row=0, column=0)

        for item in self.blood_pressure_monitor.get_children():  # For each patient
            systolic_values = []
            values = self.blood_pressure_monitor.item(item, "values")
            systolic_value = values[1].split("m")[0]

            # If systolic value is not nothing
            if systolic_value != "-":
                if float(systolic_value) < float(self.systolic_limit):
                    continue  # Skip if systolic pressure does not exceed limit
            else:
                continue

            try:
                # Select patient from the list
                patient = self.practitioner.get_monitored_patients().select_patient(values[0])
            except AttributeError:
                return
            except IndexError:
                return
            if patient is None:
                return

            output = ""  # output string with latest observations and effective time
            for i in range(5):  # get the latest 5 systolic observations
                try:
                    current_data = patient.get_blood_pressure_data(i)
                    # append systolic value and effective date to output
                    output += str(current_data[0]) + " (" + current_data[-1] + "), "
                    systolic_values.append(current_data[0])
                except IndexError:
                    continue

            if output == "- (-), ":
                output = "No data"

            # Add new entry for the patient in the table
            new_entry = (patient.first_name + " " + patient.last_name, output)
            patient_info.insert("", "end", values=new_entry)

            # Add to observer list
            self.practitioner.get_monitored_patients().attach(patient_info)

        def monitored_blood_pressure_graph():

            for item in patient_info.selection():
                values = patient_info.item(item, "values")
                patient_name = values[0]
                systolic_data = values[1]
                if systolic_data != "No data":
                    data = systolic_data.rstrip()
                    data = data.split(", ")
                    # data = systolic_data.split(", ")
                    y_values = []
                    for value in data:
                        value = value.split(" ")[0]
                        y_values.append(float(value))

                    y_values.reverse()                  # gets the systolic values in chronological order
                    x_values = []
                    for i in range(len(y_values)):
                        x_values.append(i + 1)
                    X = x_values
                    Y = y_values

                    figure = GraphicalMonitor(figsize=(5, 5), dpi=100)
                    subplot = figure.add_subplot(1, 1, 1)
                    subplot.plot(X, Y)
                    subplot.set_title(patient_name + "'s Systolic Blood Pressure Data")
                    subplot.set_xlabel("Observations")
                    subplot.set_ylabel("Systolic Blood Pressure Values (mmHg)")
                    self.practitioner.get_monitored_patients().attach(figure)

                    systolic_graph = tk.Toplevel()
                    systolic_graph.title(patient_name + "'s Systolic Blood Pressure graph")
                    canvas = FigureCanvasTkAgg(figure, master=systolic_graph)
                    canvas.get_tk_widget().grid()

                else:
                    print("Can't compute this graph")

        graph_button = tk.Button(info_window, text="Graph Data", width=15, command=monitored_blood_pressure_graph)
        graph_button.grid(row=4, column=0)

    def update_monitor(self):
        """Updates the app's GUI display depending on the selected monitor type"""

        # If the selected monitor option is Cholesterol only
        if self.selected_monitor_option.get() == "Cholesterol":

            # Delete existing blood pressure display
            self.blood_pressure_monitor.delete(*self.blood_pressure_monitor.get_children())

            # Build the cholesterol display based on the practitioner's monitored patient list
            for patient in self.practitioner.get_monitored_patients().get_patient_list():
                values = format_data(patient)
                if not duplicate_item(self.cholesterol_monitor, values[:3]):
                    self.cholesterol_monitor.insert("", "end", values=values[:3])

        # If the selected monitor option is Blood Pressure only
        if self.selected_monitor_option.get() == "Blood Pressure":

            # Delete existing cholesterol display
            self.cholesterol_monitor.delete(*self.cholesterol_monitor.get_children())

            # Build the blood pressure display based on the practitioner's monitored patient list
            for patient in self.practitioner.get_monitored_patients().get_patient_list():
                values = format_data(patient)
                if not duplicate_item(self.blood_pressure_monitor, values[3:]):
                    self.blood_pressure_monitor.insert("", "end", values=values[3:])

        # If the selected monitor option is both cholesterol and blood pressure
        if self.selected_monitor_option.get() == "Both":

            # Delete both existing monitors
            self.cholesterol_monitor.delete(*self.cholesterol_monitor.get_children())
            self.blood_pressure_monitor.delete(*self.blood_pressure_monitor.get_children())

            # Rebuild the monitors based on the practitioner's monitored patient list
            for patient in self.practitioner.get_monitored_patients().get_patient_list():
                values = format_data(patient)
                if not duplicate_item(self.cholesterol_monitor, values[:3]):
                    self.cholesterol_monitor.insert("", "end", values=values[:3])
                if not duplicate_item(self.blood_pressure_monitor, values[3:]):
                    self.blood_pressure_monitor.insert("", "end", values=values[3:])

        # Highlight the abnormal values in each monitors
        self.highlight_patients()


def is_new_cholesterol_data(values, patient):
    """
    Check whether the new patient cholesterol data is different to the current values
    :param values: current cholesterol values being displayed by the app
    :param patient: a patient object which contains new patient data
    :return: True if data differs, False otherwise
    """
    patient_data = patient.get_cholesterol_data()
    cholesterol_level = str(patient_data[0]) + " " + patient_data[1]
    effective_time = patient_data[2]
    if values[1] == cholesterol_level and values[2] == effective_time:
        return False
    return True


def is_new_blood_pressure_data(values, patient):
    """
    Check whether the new patient blood pressure data is different to the current values
    :param values: current blood pressure values being displayed by the app
    :param patient: a patient object which contains new patient data
    :return: True if data differs, False otherwise
    """
    patient_data = patient.get_blood_pressure_data(0)
    systolic_level = str(patient_data[0]) + patient_data[2]
    diastolic_level = str(patient_data[1]) + patient_data[2]
    effective_time = patient_data[3]
    if values[0] == systolic_level and values[1] == diastolic_level and values[2] == effective_time:
        return False
    return True


def format_data(patient):
    """
    Return the patient data in a format which can be use by the display
    :param patient: a patient which contains patient data
    :return: a tuple of (patient_name, cholesterol_level, effective_time)
    """
    # Assign patient name
    patient_name = patient.first_name + " " + patient.last_name

    # Assign patient data values
    # Cholesterol
    patient_cholesterol_data = patient.get_cholesterol_data()
    cholesterol_level = str(patient_cholesterol_data[0]) + " " + patient_cholesterol_data[1]
    effective_time_cholesterol = patient_cholesterol_data[2]

    # Blood Pressure
    patient_blood_pressure_data = patient.get_blood_pressure_data(0)  # Display latest observation at index 0
    systolic = str(patient_blood_pressure_data[0]) + patient_blood_pressure_data[2]
    diastolic = str(patient_blood_pressure_data[1]) + patient_blood_pressure_data[2]
    effective_time_blood_pressure = patient_blood_pressure_data[3]

    # Assign new entry values
    new_entry = (patient_name, cholesterol_level, effective_time_cholesterol,
                 patient_name, systolic, diastolic, effective_time_blood_pressure)

    return new_entry


def format_historical_systolic_data(patient):
    """
    Return the historical systolic data in a format which can be used by the display
    :param patient:  patient which contains patient data
    :return: a tuple of the patient's name and the formatted data
    """
    output = ""  # output string with latest observations and effective time
    for i in range(5):  # get the latest 5 systolic observations
        try:
            current_data = patient.get_blood_pressure_data(i)
            # append systolic value and effective date to output
            output += str(current_data[0]) + " (" + current_data[-1] + "), "
        except IndexError:
            continue

    return patient.first_name + " " + patient.last_name, output


def duplicate_item(tree, item):
    """
    Checks whether an item already exists in the Treeview
    :param tree: tkinter Treeview
    :param item: an item to be added
    :return: True if item already in list of children, False otherwise
    """
    children = tree.get_children()
    for child in children:
        values = tree.item(child, "values")
        if values == item:
            return True
    return False


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


if __name__ == '__main__':
    app = App()
    cholesterol_client = CholesterolDataClient("https://fhir.monash.edu/hapi-fhir-jpaserver/fhir/")
    blood_pressure_client = BloodPressureDataClient("https://fhir.monash.edu/hapi-fhir-jpaserver/fhir/")
    app.set_cholesterol_client(cholesterol_client)
    app.set_blood_pressure_client(blood_pressure_client)
    app.run()
