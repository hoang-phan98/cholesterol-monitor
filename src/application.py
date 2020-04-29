from src.fhir_module import *


def add_monitor_patient(new_patient):
    current_practitioner.monitored_patients.add_patient(new_patient)


if __name__ == '__main__':
    practitioner_id = input("Enter your Practitioner ID: ")
    client = CholesterolDataClient("https://fhir.monash.edu/hapi-fhir-jpaserver/fhir/")
    try:
        current_practitioner = client.get_practitioner_info(practitioner_id)
    except KeyError:
        exit("Invalid practitioner ID")

    current_practitioner.get_patient_list()
    current_practitioner.monitored_patients = current_practitioner.patient_list
    current_practitioner.get_patient_data()

    print("Dr. " + current_practitioner.first_name + " " + current_practitioner.last_name)
    for patient in current_practitioner.get_monitored_patients().get_patient_list():
        print(patient.first_name+" "+patient.last_name+" "+patient.id)
        if patient.patient_data is not None:
            print(patient.get_data())
        else:
            print("No cholesterol data found for this patient")

