from abc import abstractmethod
from src.subject_module import PatientList


class Observer:
    def __init__(self, name):
        self.name = name

    @abstractmethod
    def update(self, message):
        print("{} got message {}".format(self.name, message))


class DataDisplay:

    def __init__(self):
        self.patient_list = PatientList()

    # def update(self):
    #     self.patient_list = PatientList()
    #     for patients in range(len(self.patient_list)):
    #         patients.get_patient_data







