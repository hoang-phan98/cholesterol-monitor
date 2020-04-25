class Subject:

    def __init__(self):
        self.observer = []

    def attach(self, observer):
        self.observer = observer
        return observer

    #def detach(self, observer):

    #def notify():

class PatientList:

    def __init__(self):
        self.patient_list = []
        self.average_cholesterol_level = 0

    def add_patient(self, patient):
        self.patient_list.append(patient)

    def remove_patient(self, patient):
        self.patient_list.pop(patient)

    def __contains__(self, patient_name):
        for patient in self.patient_list:
            if (patient.first_name in patient_name) and (patient.last_name in patient_name):
                return True
        return False

    #def select_patient(self):

    def calculate_avg_cholesterol(self):
        n = len(self.patient_list)
        average = self.average_cholesterol_level // n
        return average

    #def get_patient_data(self):





