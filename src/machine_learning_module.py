from src.fhir_module import CholesterolDataClient
import matplotlib.pyplot as plt
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LinearRegression


def get_cholesterol_values():

    client = CholesterolDataClient("https://fhir.monash.edu/hapi-fhir-jpaserver/fhir/")
    practitioner_id = int(input("Enter Practitioner ID: "))
    patients = client.get_patient_list(practitioner_id)

    patient_data = []
    patient_ids = []

    for patient in range(len(patients)):
        patient_ids.append(patients.get_patient_list()[patient][2])
        print(str(patients.get_patient_list()[patient][2]))

    for patient_id in patient_ids:
        patient_data.append(client.get_patient_data(patient_id)[0])

    return patient_data


def plot_cholesterol_values():

    cholesterol_values = get_cholesterol_values()
    y_axis = []
    for y_points in range(min(cholesterol_values), max(cholesterol_values) + 1):
        y_axis.append(y_points)

    plt.scatter(cholesterol_values, y_axis)

    # Using linear regression machine learning algorithm
    x = cholesterol_values
    y = y_axis
    x_train, x_test, y_train, y_test = train_test_split(x, y, test_size=0.2, random_state=10)

    clf = LinearRegression()
    clf.fit(x_train, y_train)
    clf.predict(x_test)
    clf.score(x_test, y_test)


if __name__ == '__main__':
    plot_cholesterol_values()
