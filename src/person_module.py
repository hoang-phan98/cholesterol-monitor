from src.patientdata_module import CholesterolData, BloodPressureData


class Person:
    def __init__(self, first_name, last_name, person_id):
        self.first_name = first_name
        self.last_name = last_name
        self.id = person_id


class Patient(Person):
    def __init__(self, first_name, last_name, person_id, birth_date, gender, address,
                 cholesterol_data=None, blood_pressure_data=None):
        super().__init__(first_name, last_name, person_id)
        self.birth_date = birth_date
        self.gender = gender
        self.address = address
        self.cholesterol_data = cholesterol_data
        self.blood_pressure_data = blood_pressure_data

    def get_address(self):
        """
        Formats and returns patient's address
        :return: address string
        """
        return self.address.line[0]+", "+self.address.city+", "+self.address.state+", "+self.address.country

    def update_data(self, data):
        if isinstance(data, CholesterolData):
            self.cholesterol_data = data
        elif isinstance(data, BloodPressureData):
            self.blood_pressure_data = data
        return

    def get_cholesterol_data(self):
        return self.cholesterol_data.get_data()

    def get_blood_pressure_data(self):
        return self.blood_pressure_data.get_data()


class HealthPractitioner(Person):
    def __init__(self, first_name, last_name, practitioner_id, patient_list=None):
        super().__init__(first_name, last_name, practitioner_id)
        self._patient_list = patient_list
        self._monitored_patients = PatientList()

    def get_patient_list(self, client):
        """
        Query client to get the practitioner's patient list
        :param client: FHIR Client
        :return: None
        """
        self._patient_list = client.get_patient_list(self.id)

    def get_patient_data(self, client):
        """
        For each patient in the practitioner's monitored patient list, retrieve their data from the server
        :param client: FHIR Client
        :return: None
        """
        for patient in self._monitored_patients.get_patient_list():
            print("Requesting data for " + patient.first_name+" "+patient.last_name+"...")
            patient.update_data(client.get_patient_data(patient.id))

    def get_all_patients(self):
        """
        :return: list of all patients
        """
        return self._patient_list

    def get_monitored_patients(self):
        """
        :return: list of monitored patients
        """
        return self._monitored_patients

    def add_patient_monitor(self, patient_name):
        """
        Add patient to the monitor list from the all patients list
        :param patient_name: full name of patient to be added
        :return: None
        """
        for patient in self._patient_list.get_patient_list():
            if patient_name == patient.first_name + " " + patient.last_name:
                self._monitored_patients.add_patient(patient)

    def remove_patient_monitor(self, patient_name):
        """
        Remove patient from monitor list
        :param patient_name: full name of patient to be removed
        :return: None
        """
        self._monitored_patients.remove_patient(patient_name)

    def clear_monitor(self):
        """
        Reset the monitored patients list
        :return: None
        """
        self._monitored_patients = PatientList()


class PatientList:

    def __init__(self):
        self._patient_list = []
        self.average_cholesterol_level = 0
        self._observers = []

    def __len__(self):
        return len(self._patient_list)

    def __contains__(self, patient):
        for i in range(len(self)):
            current_patient = self._patient_list[i]
            if current_patient.first_name == patient.first_name and current_patient.last_name == patient.last_name:
                return True
        return False

    def add_patient(self, patient):
        """
        Add the patient to the patient list and recalculate avg cholesterol
        :param patient: Patient Object
        :return: None
        """
        if isinstance(patient, Patient):
            self._patient_list.append(patient)
            self.calculate_avg_cholesterol()

    def remove_patient(self, patient_name):
        """
        Remove patient with the given name
        :param patient_name: Full name of the patient to be removed
        :return: None
        """
        for i in range(len(self)):
            selected_patient = self._patient_list[i]
            if patient_name == selected_patient.first_name + " " + selected_patient.last_name:
                self._patient_list.pop(i)
                self.calculate_avg_cholesterol()
                return True
        return False

    def get_patient_list(self):
        """
        Getter method for the list of patients
        :return: array of patients
        """
        return self._patient_list

    def select_patient(self, patient_name):
        """
        Find patient with the given name
        :param patient_name: name of the patient
        :return: Patient object if matching patient found, None otherwise
        """
        for i in range(len(self)):
            selected_patient = self._patient_list[i]
            if patient_name == selected_patient.first_name + " " + selected_patient.last_name:
                return selected_patient
        return None

    def calculate_avg_cholesterol(self):
        """
        Calculate average cholesterol of all patients
        If patient has no cholesterol data, they are ignored
        :return: avg cholesterol
        """
        total = 0
        no_of_valid_patients = 0
        for patient in self._patient_list:
            try:
                total += patient.get_cholesterol_data()[0]
                no_of_valid_patients += 1
            except AttributeError:
                continue
            except TypeError:
                continue
        if no_of_valid_patients == 0:
            return 0
        average = total/no_of_valid_patients
        self.average_cholesterol_level = average
        return average

    def attach(self, observer):
        self._observers.append(observer)
        observer.set_subject(self)

    def detach(self, observer):
        self._observers.remove(observer)
        observer.set_subject(None)

    def notify(self):
        for observer in self._observers:
            observer.update()


class Address:
    def __init__(self, line, city, state, country):
        self.line = line
        self.city = city
        self.state = state
        self.country = country
