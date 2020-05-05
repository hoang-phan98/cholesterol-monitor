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

    def remove_patient(self, patient_name):
        first_name = patient_name.split(' ')[0]
        last_name = patient_name.split(' ')[1]
        for i in range(len(self)):
            selected_patient = self.patient_list[i]
            if selected_patient.first_name == first_name and selected_patient.last_name == last_name:
                self.patient_list.pop(i)
                self.calculate_avg_cholesterol()
                return True
        return False

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
        no_of_valid_patients = 0
        for patient in self.patient_list:
            if isinstance(patient.get_data()[0], float):
                total += patient.get_data()[0]
                no_of_valid_patients += 1
        average = total/no_of_valid_patients
        self.average_cholesterol_level = average
        return average