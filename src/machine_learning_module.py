import requests
from src.fhir_module import CholesterolDataClient, FHIRClient
import matplotlib.pyplot as plt
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LinearRegression
import csv


class MachineLearningClient:

    def __init__(self, root_url):
        self._root_url = root_url

    def get_all_patient_id(self):

        # Creating csv file with all the patient ids
        with open("patient_ids.csv", "w", newline="") as patient_id_file:
            fieldnames = ["PATIENT ID"]
            file_writer = csv.DictWriter(patient_id_file, fieldnames=fieldnames)
            file_writer.writeheader()

            next_page = True
            next_url = self._root_url + "?_getpages=f0e1480b-e93c-440f-b138-1667ddb84133&_getpagesoffset=50&_" \
                                        "count=50&_pretty=true&_bundletype=searchset"
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

                if page_count >= 30:
                    break

    def get_patient_data_codes(self):

        with open("patient_ids.csv", "r") as patient_id_file:
            read_id_file = csv.reader(patient_id_file, delimiter=",")
            patient_id_file.readline()
            useful_data_codes = []

            for patient_id in read_id_file:
                # Gets patients other diagnostics
                res = requests.get(self._root_url + "Observation?patient=" + str(patient_id))
                # Convert to json & extract relevant data
                data = res.json()

                for data_code in data["entry"]:
                    data_codes = data_code["resource"]["code"]["coding"]["code"]
                    if data_codes not in useful_data_codes:
                        useful_data_codes.append(data_codes)

            return useful_data_codes

    def data_chart(self):

        with open("patient_ids.csv", "r") as patient_id_file:
            read_id_file = csv.reader(patient_id_file, delimiter=",")
            patient_id_file.readline()
            patient_data = []
            data_codes = self.get_patient_data_codes()

            for patient_id in read_id_file:
                for data_code in data_codes:
                    res = requests.get(self._root_url + "Observation?patient=" + str(patient_id) +
                                       "&code=" + str(data_codes[data_code]))
                    data = res.json()

                    for value_quantity in data["entry"]:
                        data_value = value_quantity["resource"]["valueQuantity"]["value"]
                        data_description = value_quantity["resource"]["code"]["coding"]["display"]
                        patient_data_value = patient_id, data_description, data_value
                        patient_data.append(patient_data_value)

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
    client.get_all_patient_id()
    client.get_patient_data_codes()
    client.data_chart()
