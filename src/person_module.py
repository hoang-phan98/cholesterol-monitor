from src import address_module


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
        return self.address

    def update_data(self, patient_data):
        self.patient_data = patient_data
        return

    def get_data(self):
        return self.patient_data.get_data()


class HealthPractitioner(Person):
    def __init__(self, first_name, last_name, practitioner_id, patient_list=None,
                 monitored_patient=None, update_interval=None):
        super().__init__(first_name, last_name, practitioner_id)
        self.patient_list = patient_list
        self.monitored_patients = monitored_patient
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
