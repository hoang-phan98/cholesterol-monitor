from src import address_module
from src import fhir_module


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
        self.address = address_module.Address
        return self.address

    def update_data(self, person_id):
        self.patient_data = fhir_module.CholesterolDataClient.get_patient_data(person_id)
        return self.patient_data

