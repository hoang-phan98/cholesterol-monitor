import numpy as np
import pandas as pd
import requests
import csv
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LinearRegression


class MachineLearningClient:

    def __init__(self, root_url):
        self._root_url = root_url

    def patient_id_csv(self):
        """
        Writes a CSV file containing roughly 2000 patient ids, so the data is stored persistently.
        :return: None
        """

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
        """
        Obtains the data codes from the patients, using their ids.
        :return: List of data codes.
        """

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
        """
        Writes the data codes into a CSV, so the data is stored persistently.
        :return:
        """

        with open("Machine Learning Data/data_codes.csv", "w", newline="") as data_code_file:
            fieldnames = ["DATA CODES"]
            file_writer = csv.DictWriter(data_code_file, fieldnames=fieldnames)
            file_writer.writeheader()

            data_codes = self.get_patient_data_codes()
            for data_code in data_codes:
                file_writer.writerow({"DATA CODES": data_code})

    def read_id_csv(self):
        """
        Puts all the used patient ids into a list so it can be accessed easier.
        :return: List of patient ids
        """

        with open("Machine Learning Data/patient_ids.csv", "r") as patient_id_file:
            read_id_file = csv.reader(patient_id_file, delimiter=",")
            patient_id_file.readline()
            patient_list = []
            for patient_ids in read_id_file:
                for patient_id in patient_ids:
                    patient_list.append(patient_id)
            return patient_list

    def read_data_csv(self):
        """
        puts all the used data codes in a list so it can be accessed easier.
        :return: List of data codes.
        """

        with open("Machine Learning Data/data_codes.csv", "r") as data_codes_file:
            read_data_code_file = csv.reader(data_codes_file, delimiter=",")
            data_codes_file.readline()
            all_data_codes = []
            for data_codes in read_data_code_file:
                for data_code in data_codes:
                    all_data_codes.append(data_code)
            return all_data_codes

    def data_chart(self):
        """
        Writes a CSV file containing the most useful data codes and the value that is respective
        to the patient, using their patient id.
        :return: List of the patient data.
        """

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
                                       "&code=" + str(data_code) + "&_sort=-date")
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

                        elif data_code == "72166-2":  # Smoking status
                            data_description = data["entry"][0]["resource"]["code"]["coding"][0]["display"]
                            data_value = data["entry"][0]["resource"]["valueCodeableConcept"]["coding"][0]["code"]

                        else:
                            data_description = "No Data"
                            data_value = "0"

                    patient_data_value = patient_id, data_description, data_value
                    patient_data.append(patient_data_value)

                    file_writer.writerow({"PATIENT ID": patient_data_value[0],
                                          "DIAGNOSTIC DESCRIPTION": patient_data_value[1],
                                          "VALUE": patient_data_value[2]})
            return patient_data

    def set_data_values_array(self):
        """
        Sets the data into a more readable view, and so that the data is organised in columns.
        :return: List of data values.
        """

        with open("Machine Learning Data/patient_data.csv", "r") as patient_data_file:
            read_patient_data_file = csv.reader(patient_data_file, delimiter=",")
            patient_data_file.readline()
            data_values = []

            for data in read_patient_data_file:
                data_values.append(data[2])

            data_values_array = np.array(data_values).reshape((-1, 7))
            return data_values_array

    def get_data_values_array(self):
        """
        Writes the data values out respective to the patient, using their patient id, to a CSV file.
        :return: None
        """

        with open("Machine Learning Data/patient_data_set.csv", "w", newline="") as patient_values_file:
            fieldnames = ["PATIENT ID", "BLOOD PRESSURE", "GLUCOSE", "TOBACCO INTAKE",
                          "BMI", "SODIUM", "WEIGHT", "CHOLESTEROL"]
            file_writer = csv.DictWriter(patient_values_file, fieldnames=fieldnames)
            file_writer.writeheader()

            patient_values = self.set_data_values_array()
            patient_ids = self.read_id_csv()

            check_id = True
            while check_id:
                for patient_value in patient_values:
                    for patient_id in patient_ids:
                        file_writer.writerow({"PATIENT ID": patient_id,
                                              "BLOOD PRESSURE": patient_value[0],
                                              "GLUCOSE": patient_value[1],
                                              "TOBACCO INTAKE": patient_value[2],
                                              "BMI": patient_value[3],
                                              "SODIUM": patient_value[4],
                                              "WEIGHT": patient_value[5],
                                              "CHOLESTEROL": patient_value[6]})
                        patient_ids.pop(0)
                        check_id = False
                        if not check_id:
                            break

    def machine_learning_LR(self):
        """
        Predicts whether the a set of inputs respective to the data codes used can predict
        a patients cholesterol level.
        :return: data set.
        """

        # Loading Data Set
        data = pd.read_csv("Machine Learning Data/patient_data_set.csv")
        data.head()

        # Exploratory Analysis
        # Total percentage of missing data
        missing_data = data.isnull().sum()
        total_percentage = (missing_data.sum()/data.shape[0]) * 100
        print(f"the total percentage of missing data is {round(total_percentage, 2)}%")

        # Prediction
        X = data.drop(["PATIENT ID", "CHOLESTEROL"], 1)
        # X = preprocessing.scale(X)
        y = data["CHOLESTEROL"]

        X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=100)
        clf = LinearRegression()
        clf.fit(X_train, y_train)

        # Checking the tests
        # print(clf.predict(X_test))
        # print(y_test)

        # Putting all the predicted cholesterol values into a list
        predicted_cholesterol = []
        for predicted_values in clf.predict(X_test):
            predicted_cholesterol.append(predicted_values)

        high_cholesterol_array = []
        for value in predicted_cholesterol:
            if value > 175:
                # if value is higher than 175 mg/dl, patient is labelled with 1
                high_cholesterol_array.append(1)
            else:
                # if value is lower than 175 mg/dl, patient is labelled with 0
                high_cholesterol_array.append(0)

        # prints the accuracy of the accuracy of the model
        print("The accuracy of the model is " + str(clf.score(X_test, y_test)) + " out of 1.0\n")
        # prints the data set
        print(data)

        # creating new data set to show if patients have a high cholesterol level
        new_data = X_test
        df = pd.DataFrame(new_data)

        # creating new column in the new data set to indicate which patients have a high cholesterol
        # from the tested patients
        df["PREDICTED CHOLESTEROL"] = y_test
        df["HIGH_CHOLESTEROL"] = high_cholesterol_array
        print(df)


if __name__ == '__main__':
    client = MachineLearningClient("https://fhir.monash.edu/hapi-fhir-jpaserver/fhir/")
    # client.patient_id_csv()
    # client.data_codes_csv()
    # print(client.read_data_csv())
    # print(client.data_chart())
    # print(client.get_data_values_array())
    # print(client.set_data_values_array())
    print(client.machine_learning_LR())
