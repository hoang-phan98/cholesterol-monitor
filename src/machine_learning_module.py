import requests

from src.fhir_module import CholesterolDataClient, FHIRClient
import matplotlib.pyplot as plt
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LinearRegression
import csv

class MachineLeraningClient():

    def __init__(self):
        self._root_url = "https://fhir.monash.edu/hapi-fhir-jpaserver/fhir"

    def get_all_patient_id(self):

        # Creating csv file with all the patient ids
        with open("patient_ids.csv", "w", newline="") as patient_id_file:
            fieldnames = ["PATIENT ID"]
            file_writer = csv.DictWriter(patient_id_file, fieldnames=fieldnames)
            file_writer.writeheader()

            next_page = True
            next_url = self._root_url + "?_getpages=12f58cf4-e0b7-41db-b929-3287f1573dec&_getpagesoffset=50&" \
                                        "count=50&_pretty=true&_bundletype=searchset"
            page_count = 1
            patient_ids_array = []

            while next_page:
                # returns all the patients
                res = requests.get(next_url)
                # Convert to json & extract relevant data
                data = res.json()

                for patients in data["entry"]:
                    patient_ids = patients["resource"]["id"]
                    if patient_ids not in patient_ids_array:
                        file_writer.writerow({"PATIENT ID": patient_ids})

                next_page = False
                links = data["link"]
                for i in range(len(links)):
                    link = links[i]
                    if link["relation"] == "next":
                        next_page = True
                        next_url = link["url"]
                        page_count += 1

                if page_count >= 3:
                    break

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
    client = MachineLeraningClient()
    client.get_all_patient_id()
