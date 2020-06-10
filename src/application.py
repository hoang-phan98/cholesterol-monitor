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


class GraphicalMonitor(Observer, FigureCanvasTkAgg):

    def update(self):
        if self._subject is not None:  # If subject has not been specified, do nothing
            self.get_tk_widget().grid()


class CholesterolMonitorTreeview(Observer, ttk.Treeview):
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


class BloodPressureMonitorTreeview(Observer, ttk.Treeview):
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
                patient_name = values[-1]
                current_patient = self._subject.select_patient(patient_name)
                if is_new_blood_pressure_data(values, current_patient):  # Check if the new values are different
                    self.item(item, values=format_data(current_patient)[3:])  # update the display with new data


class GraphicalMonitor(Observer, Figure):
    def update(self):
        return


class App:
    """
    Driver class which contains the logged in practitioner, client and UI components
    """

    def __init__(self):
        self.practitioner = None
        self.cholesterol_client = None
        self.blood_pressure_client = None
        self.update_interval = 30
<<<<<<< HEAD
        self.systolic_limit = '125'
        self.diastolic_limit = '80'
=======
        self.systolic_limit = "130"
        self.diastolic_limit = "80"
>>>>>>> 26de348d2b270bc84525d21f162568b3c7e23227
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
        systolic_limit = self.systolic_limit_field.get()
        self.systolic_limit = int(systolic_limit)
        self.systolic_limit_label.destroy()
        self.systolic_limit_label = tk.Label(self.main_UI, text="Systolic BP Limit: " + str(self.systolic_limit))
        self.systolic_limit_label.grid(row=0, column=4, rowspan=2)
        self.highlight_patients()

    def set_diastolic_limit(self, event=None):
        diastolic_limit = self.diastolic_limit_field.get()
        self.diastolic_limit = int(diastolic_limit)
        self.diastolic_limit_label.destroy()
        self.diastolic_limit_label = tk.Label(self.main_UI, text="Diastolic BP Limit: " + str(self.diastolic_limit))
        self.diastolic_limit_label.grid(row=0, column=6, rowspan=2)
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
        self.cholesterol_monitor = CholesterolMonitorTreeview(self.main_UI, columns=cols, show='headings')
        for col in cols:
            self.cholesterol_monitor.heading(col, text=col)
            self.cholesterol_monitor.column(col, width=150)
        self.cholesterol_monitor.grid(row=2, column=1, columnspan=3)
        self.cholesterol_monitor.bind("<Double-1>", self.display_patient_info)
        self.cholesterol_monitor.bind("<Delete>", self.remove_monitored_patient)

        # create blood pressure monitor treeview
        cols = ('Systolic Blood Pressure', 'Diastolic Blood Pressure', 'Time')
        self.blood_pressure_monitor = BloodPressureMonitorTreeview(self.main_UI, columns=cols, show='headings')
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
            update_monitor_button = tk.Button(self.main_UI, text="Update Monitor", width=15)
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
        Request new patient data from server and update display every N seconds
        """
        while True:
            # Execute if there's at least one patient being monitored
            if len(self.practitioner.get_monitored_patients()) > 0:
                # Request data from server
                self.practitioner.get_patient_data(self.cholesterol_client)
                self.practitioner.get_patient_data(self.blood_pressure_client)

                # Notify Treeview observer of data changes
                try:
                    self.practitioner.get_monitored_patients().notify()
                except AttributeError:
                    time.sleep(1)

                self.highlight_patients()
<<<<<<< HEAD
=======
                # self.cholesterol_graph_data()
                # self.blood_pressure_graph_data()
>>>>>>> 26de348d2b270bc84525d21f162568b3c7e23227

                # Sleep
                time.sleep(self.update_interval)

    def add_monitored_patient(self, event=None):
        """
        Add a patient from the list of all patients to the list of monitored patients
        also add the patient to the practitioner's monitored patients list object
        """
        selected = self.all_patients.selection()
        values = None
        for item in selected:
            try:
                values = self.all_patients.item(item, "values")
                if not duplicate_item(self.cholesterol_monitor, values):
                    # Add patient to treeview
                    self.cholesterol_monitor.insert("", "end", values=values[:3])
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
            selected = self.cholesterol_monitor.selection()
            if len(selected) == 0:
                selected = self.blood_pressure_monitor.selection()
            for item in selected:
                values = self.cholesterol_monitor.item(item, "values")
                # Remove item from practitioner's monitored patient list
                self.practitioner.remove_patient_monitor(values[0])
                # Remove item from treeviews
                self.cholesterol_monitor.delete(item)
                self.blood_pressure_monitor.delete(item)
            self.highlight_patients()
        except IndexError:
            return

    def display_patient_info(self, event=None):
        """
        Display the selected patient's personal info in a pop-up window
        """
        for item in self.cholesterol_monitor.selection():
            values = self.cholesterol_monitor.item(item, "values")
            try:
                # Select patient from the list
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
        Check the cholesterol level of each monitored patient
        If the level is higher than the average of all monitored patients, highlight this patient in red
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
                patient_systolic_blood_pressure = values[0].split('mm')[0]
                patient_diastolic_blood_pressure = values[1].split('mm')[0]
                try:
                    if int(patient_systolic_blood_pressure) > int(self.systolic_limit) or \
                            int(patient_diastolic_blood_pressure) > int(self.diastolic_limit):
                        self.blood_pressure_monitor.item(child, tags=['high blood pressure'])
                    else:
                        self.blood_pressure_monitor.item(child, tags=['normal'])
                    self.blood_pressure_monitor.tag_configure('normal', foreground=None)
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
                    else:
                        patient_data.append(0)
                        patient_name = values[0]
                        patients.append(patient_name)
                X = patients
                Y = patient_data
                return X, Y

        except KeyError:
            messagebox.showinfo("Error", "No practitioner identifier given")

    def cholesterol_graph(self, event=None):

        graph_data = self.cholesterol_graph_data()
        figure = Figure(figsize=(10, 5), dpi=100)
        subplot = figure.add_subplot(1, 1, 1)
        subplot.bar(graph_data[0], graph_data[1], bottom=0)
        subplot.set_title("Patient Cholesterol Data (mg/dL)")
        subplot.set_xlabel("Patient Names")
        subplot.set_ylabel("Cholesterol Values")

        cholesterol_graph = tk.Toplevel()
        cholesterol_graph.title("Cholesterol Graph")
        self.cholesterol_graphical_monitor = GraphicalMonitor(figure, master=cholesterol_graph)
        self.practitioner.get_monitored_patients().attach(self.cholesterol_graphical_monitor)
        self.practitioner.get_monitored_patients().notify()
        # canvas = FigureCanvasTkAgg(figure, master=cholesterol_graph)
        # canvas.get_tk_widget().grid()

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
                    patient_systolic_blood_pressure = values[0].split('m')[0]
                    patient_diastolic_blood_pressure = values[1].split('m')[0]
                    if patient_systolic_blood_pressure != "-" and patient_diastolic_blood_pressure != "-":
                        patient_systolic_data.append(int(patient_systolic_blood_pressure))
                        patient_diastolic_data.append(int(patient_diastolic_blood_pressure))

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

        graph_data = self.blood_pressure_graph_data()
        figure = Figure(figsize=(15, 5), dpi=100)
        subplot = figure.add_subplot(1, 2, 1)
        subplot.plot(graph_data[0], graph_data[1])
        subplot.set_title("Patient Systolic Data (mgHg)")
        subplot.set_xlabel("Patient Names")
        subplot.set_ylabel("Systolic Blood Pressure Values")

        subplot = figure.add_subplot(1, 2, 2)
        subplot.plot(graph_data[0], graph_data[2])
        subplot.set_title("Patient Diastolic Data (mgHg)")
        subplot.set_xlabel("Patient Names")
        subplot.set_ylabel("Diastolic Blood Pressure Values")

        blood_pressure_graphs = tk.Toplevel()
        blood_pressure_graphs.title("Blood Pressure Graphs")
        self.BP_graphical_monitor = GraphicalMonitor(figure, master=blood_pressure_graphs)
        self.practitioner.get_monitored_patients().attach(self.BP_graphical_monitor)
        self.practitioner.get_monitored_patients().notify()
        # canvas = FigureCanvasTkAgg(figure, master=blood_pressure_graphs)
        # canvas.get_tk_widget().grid()

    def monitor_blood_pressure(self, event=None):
        """
        Displays the selected patient's latest systolic blood pressure observations in a pop-up window, gives the
        option to visually represent the data in the form of a line graph.
        """

        # Create a pop-up window to display latest blood pressure values
        info_window = tk.Toplevel()
        info_window.title("Blood Pressure Monitor")
        cols = ("Name", "Latest systolic blood pressure observations")
        patient_info = ttk.Treeview(info_window, columns=cols, show='headings')
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
            systolic_value = values[0].split("m")[0]

            if int(systolic_value) < int(self.systolic_limit):
                continue  # Skip if systolic pressure does not exceed limit

            try:
                # Select patient from the list
                patient = self.practitioner.get_monitored_patients().select_patient(values[-1])
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
                    output += str(current_data[0]) + " (" + current_data[-1] + "), "
                    systolic_values.append(current_data[0])
                except IndexError:
                    continue

            if output == "- (-), ":
                output = "No data"

            # Add new entry for the patient in the table
            new_entry = (patient.first_name + " " + patient.last_name, output)
            patient_info.insert("", "end", values=new_entry)

            x_values = []
            for i in range(len(systolic_values)):
                x_values.append(i + 1)
            X = x_values
            Y = systolic_values

        def monitored_blood_pressure_graph():
            figure = Figure(figsize=(5, 5), dpi=100)
            subplot = figure.add_subplot(1, 1, 1)
            subplot.plot(X, Y)
            subplot.set_title(patient.first_name + " " + patient.last_name + "'s Systolic Blood Pressure Data (mgHg)")
            subplot.set_xlabel("Patient Names")
            subplot.set_ylabel("Diastolic Blood Pressure Values")

            systolic_graph = tk.Toplevel()
            systolic_graph.title(patient.first_name + " " + patient.last_name + "'s Systolic Blood Pressure graph")
            canvas = FigureCanvasTkAgg(figure, master=systolic_graph)
            canvas.get_tk_widget().grid()

        graph_button = tk.Button(info_window, text="Graph Data", width=15, command=monitored_blood_pressure_graph)
        graph_button.grid(row=4, column=0)


def is_new_cholesterol_data(values, patient):
    """
    Check whether the new patient data is different to the current values
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
    Check whether the new patient data is different to the current values
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
                 systolic, diastolic, effective_time_blood_pressure, patient_name)

    return new_entry


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
