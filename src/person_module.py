from src import address_module
from src.subject_module import PatientList


class Person:

    def __init__(self, first_name, last_name, person_id):
        self.first_name = first_name
        self.last_name = last_name
        self.id = person_id


class Patient(Person):

    def __init__(self, first_name, last_name, person_id, birth_date, gender, address, patient_data=None):
        super().__init__(first_name, last_name, person_id)
        self.birth_date = birth_date
        self.gender = gender
        self.address = address
        self.patient_data = patient_data

    def get_address(self):
        return self.address.line[0]+", "+self.address.city+", "+self.address.state+", "+self.address.country

    def update_data(self, patient_data):
        self.patient_data = patient_data
        return

    def get_data(self):
        return self.patient_data.get_data()


class HealthPractitioner(Person):
    def __init__(self, first_name, last_name, practitioner_id, patient_list=None,
                 update_interval=None):
        super().__init__(first_name, last_name, practitioner_id)
        self.patient_list = patient_list
        self.monitored_patients = PatientList()
        self.update_interval = update_interval

    def get_patient_list(self, client):
        self.patient_list = client.get_patient_list(self.id)

    def get_patient_data(self, client):
        for patient in self.monitored_patients.get_patient_list():
            patient.update_data(client.get_patient_data(patient.id))

    def get_all_patients(self):
        return self.patient_list

    def get_monitored_patients(self):
        return self.monitored_patients

    def add_patient_monitor(self, patient_name):
        first_name = patient_name.split(' ')[0]
        last_name = patient_name.split(' ')[1]
        for patient in self.patient_list.get_patient_list():
            if first_name==patient.first_name and last_name==patient.last_name:
                self.monitored_patients.add_patient(patient)

    def remove_patient_monitor(self, patient_name):
        self.monitored_patients.remove_patient(patient_name)
