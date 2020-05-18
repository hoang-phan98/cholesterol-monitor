import requests
from src.fhir_module import CholesterolDataClient, FHIRClient
import matplotlib.pyplot as plt
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LinearRegression
import csv


class MachineLearningClient:

    def __init__(self, root_url):
        self._root_url = root_url

    def patient_id_csv(self):

        # Creating csv file with all the patient ids
        with open("Machine Learning Data/patient_ids.csv", "w", newline="") as patient_id_file:
            fieldnames = ["PATIENT ID"]
            file_writer = csv.DictWriter(patient_id_file, fieldnames=fieldnames)
            file_writer.writeheader()

            next_page = True
            next_url = self._root_url + "Patient"
            page_count = 1
            patient_ids_array = []

            while next_page:
                # returns all the patients
                res = requests.get(next_url)
                # Convert to json & extract relevant data
                data = res.json()

                for patient in data["entry"]:
                    patient_ids = patient["resource"]["id"]
                    if patient_ids not in patient_ids_array:
                        patient_ids_array.append(patient_ids)
                        file_writer.writerow({"PATIENT ID": patient_ids})

                next_page = False
                links = data["link"]
                for i in range(len(links)):
                    link = links[i]
                    if link["relation"] == "next":
                        next_page = True
                        next_url = link["url"]
                        page_count += 1

                if page_count >= 40:
                    break

    def get_patient_data_codes(self):

        with open("Machine Learning Data/patient_ids.csv", "r") as patient_id_file:
            read_id_file = csv.reader(patient_id_file, delimiter=",")
            # Skips first line of the csv file
            patient_id_file.readline()
            useful_data_types = ["Glucose", "Diastolic Blood Pressure", "Systolic Blood Pressure",
                                 "Body Mass Index", "Tobacco smoking status NHIS"]
            useful_data_codes = []

            for patient_id in read_id_file:
                # Gets patients other diagnostics
                res = requests.get(self._root_url + "Observation?patient=" + str(patient_id[0]))
                # Convert to json & extract relevant data
                data = res.json()

                for observation in data["entry"]:
                    data_type = observation["resource"]["code"]["coding"][0]["display"]
                    data_code = observation["resource"]["code"]["coding"][0]["code"]
                    if data_type in useful_data_types:
                        useful_data_codes.append(data_code)

            return useful_data_codes

    def data_codes_csv(self):

        with open("Machine Learning Data/data_codes.csv", "w", newline="") as data_code_file:
            fieldnames = ["DATA CODES"]
            file_writer = csv.DictWriter(data_code_file, fieldnames=fieldnames)
            file_writer.writeheader()

            data_codes = self.get_patient_data_codes()
            for data_code in data_codes:
                file_writer.writerow({"DATA CODES": data_code})

    def read_id_csv(self):
        with open("Machine Learning Data/patient_ids.csv", "r") as patient_id_file:
            read_id_file = csv.reader(patient_id_file, delimiter=",")
            patient_id_file.readline()
            patient_list = []
            for patient_ids in read_id_file:
                for patient_id in patient_ids:
                    patient_list.append(patient_id)
            return patient_list

    def read_data_csv(self):
        with open("Machine Learning Data/data_codes.csv", "r") as data_codes_file:
            read_data_code_file = csv.reader(data_codes_file, delimiter=",")
            data_codes_file.readline()
            all_data_codes = []
            for data_codes in read_data_code_file:
                for data_code in data_codes:
                    all_data_codes.append(data_code)
            return all_data_codes

    def data_chart(self):
        with open("Machine Learning Data/patient_data.csv", "w", newline="") as patient_data_file:
            fieldnames = ["PATIENT ID", "DIAGNOSTIC DESCRIPTION", "VALUE"]
            file_writer = csv.DictWriter(patient_data_file, fieldnames=fieldnames)
            file_writer.writeheader()

            patient_ids = self.read_id_csv()
            data_codes = self.read_data_csv()
            patient_data = []

            for patient_id in patient_ids:
                for data_code in data_codes:
                    res = requests.get(self._root_url + "Observation?patient=" + str(patient_id) +
                                       "&code=" + str(data_code)+"&_sort=-date")
                    data = res.json()

                    try:
                        data_description = data["entry"][0]["resource"]["code"]["coding"][0]["display"]
                        data_value = data["entry"][0]["resource"]["valueQuantity"]["value"]
                    except KeyError:

                        if data_code == "55284-4":  # Blood pressure
                            components = data["entry"][0]["resource"]["component"]
                            for component in components:
                                if component["code"]["coding"][0]["code"] == "8480-6":  # Systolic Blood Pressure
                                    data_description = component["code"]["coding"][0]["display"]
                                    data_value = component["valueQuantity"]["value"]
                                    break

                        elif data_code == "72166-2":    # Smoking status
                            data_description = data["entry"][0]["resource"]["code"]["coding"][0]["display"]
                            data_value = data["entry"][0]["resource"]["valueCodeableConcept"]["coding"][0]["code"]

                        else:
                            data_description = "No Data"
                            data_value = "No Data"

                    patient_data_value = patient_id, data_description, data_value
                    patient_data.append(patient_data_value)

                    file_writer.writerow({"PATIENT ID": patient_data_value[0],
                                          "DIAGNOSTIC DESCRIPTION": patient_data_value[1],
                                          "VALUE": patient_data_value[2]})
            return patient_data

    # def plot_cholesterol_values(self):
    #
    #     cholesterol_values = get_cholesterol_values()
    #     y_axis = []
    #     for y_points in range(min(cholesterol_values), max(cholesterol_values) + 1):
    #         y_axis.append(y_points)
    #
    #     plt.scatter(cholesterol_values, y_axis)
    #
    #     # Using linear regression machine learning algorithm
    #     x = cholesterol_values
    #     y = y_axis
    #     x_train, x_test, y_train, y_test = train_test_split(x, y, test_size=0.2, random_state=10)
    #
    #     clf = LinearRegression()
    #     clf.fit(x_train, y_train)
    #     clf.predict(x_test)
    #     clf.score(x_test, y_test)


if __name__ == '__main__':
    client = MachineLearningClient("https://fhir.monash.edu/hapi-fhir-jpaserver/fhir/")
    # client.patient_id_csv()
    # client.data_codes_csv()
    # print(client.read_data_csv())
    print(client.data_chart())
