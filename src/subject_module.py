from abc import abstractmethod
from src.patientdata_module import CholesterolData


class Subject:

    def __init__(self):
        self.observer_list = []

    def attach(self, observer):
        self.observer_list.append(observer)

    def detach(self, observer):
        self.observer_list.pop(observer)

    @abstractmethod
    def notify(self, message):
        for observer in self.observer_list:
            observer.update(message)


class PatientList:

    def __init__(self):
        self.patient_list = []
        self.average_cholesterol_level = 0

    def __len__(self):
        return len(self.patient_list)

    def __contains__(self, patient):
        for i in range(len(self)):
            current_patient = self.patient_list[i]
            if current_patient.first_name == patient.first_name and current_patient.last_name == patient.last_name:
                return True
        return False

    def add_patient(self, patient):
        self.patient_list.append(patient)
        self.calculate_avg_cholesterol()

    def remove_patient(self, patient):
        self.patient_list.pop(patient)

    def get_patient_list(self):
        return self.patient_list

    def select_patient(self, patient_name):
        first_name = patient_name.split(' ')[0]
        last_name = patient_name.split(' ')[1]
        for i in range(len(self)):
            selected_patient = self.patient_list[i]
            if selected_patient.first_name == first_name and selected_patient.last_name == last_name:
                return selected_patient
        return None

    def calculate_avg_cholesterol(self):
        total = 0
        for patient in self.patient_list:
            total = total + patient.get_data()[0]
        average = total/len(self.patient_list)
        self.average_cholesterol_level = average
        return average
