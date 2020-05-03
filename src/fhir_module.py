from datetime import *
import requests
from abc import ABC, abstractmethod
from src.patientdata_module import CholesterolData
from src.person_module import Patient, HealthPractitioner
from src.address_module import Address
from src.subject_module import PatientList


class FHIRClient(ABC):
    def __init__(self, root_url):
        self.root_url = root_url

    def get_patient_list(self, practitioner_id):
        next_page = True
        next_url = self.root_url+"Encounter?practitioner="+str(practitioner_id)+"&_count=10"
        page_count = 1
        patient_list = PatientList()

        while next_page:
            res = requests.get(next_url)
            data = res.json()
            for encounter in data["entry"]:
                patient_id = encounter["resource"]["subject"]["reference"].split("/")[1]
                patient = self.get_basic_patient_info(patient_id)
                if patient not in patient_list:
                    patient_list.add_patient(patient)

            next_page = False
            links = data["link"]
            for i in range(len(links)):
                link = links[i]
                if link["relation"] == "next":
                    next_page = True
                    next_url = link["url"]
                    page_count += 1

        return patient_list

    def get_practitioner_info(self, practitioner_id):
        res = requests.get(self.root_url + "Practitioner/" + str(practitioner_id))
        data = res.json()
        name = data["name"][0]
        first_name = "".join(x for x in name["given"][0] if not x.isdigit())
        last_name = "".join(x for x in name["family"] if not x.isdigit())
        return HealthPractitioner(first_name, last_name, practitioner_id)

    def get_basic_patient_info(self, patient_id):
        res = requests.get(self.root_url + "Patient/" + str(patient_id))
        data = res.json()

        # Assign first and last name
        name = data["name"]
        for i in range(len(name)):
            if name[i]["use"] == "official":
                first_name = "".join(x for x in name[i]["given"][0] if not x.isdigit())
                last_name = "".join(x for x in name[i]["family"] if not x.isdigit())

        # Assign gender and birth date
        gender = data["gender"]
        birth = data["birthDate"]
        birth_date = datetime.strptime(birth, '%Y-%m-%d').date()
        # Assign address object
        address = data["address"][0]
        patient_address = Address(address["line"], address["city"], address["state"], address["country"])
        patient_data = self.get_patient_data(patient_id)
        # Return patient object
        return Patient(first_name, last_name, patient_id, birth_date, gender, patient_address, patient_data)

    @abstractmethod
    def get_patient_data(self, patient_id):
        pass


class CholesterolDataClient(FHIRClient):
    def get_patient_data(self, patient_id):
        # Sort by decreasing date, only need 1 entry for latest value
        res = requests.get(self.root_url + "Observation?patient=" +
                           str(patient_id) +
                           "&code=2093-3&_sort=-date&_count=1")

        # Convert to json & extract relevant data
        data = res.json()

        # Check if response contains cholesterol data
        if data["total"] == 0:
            return None

        # Assign cholesterol data
        cholesterol_value = data["entry"][0]["resource"]["valueQuantity"]["value"]
        cholesterol_unit = data["entry"][0]["resource"]["valueQuantity"]["unit"]
        effective_date_time = data["entry"][0]["resource"]["effectiveDateTime"]
        return CholesterolData(cholesterol_value, cholesterol_unit, effective_date_time)


if __name__ == '__main__':
    client = CholesterolDataClient("https://fhir.monash.edu/hapi-fhir-jpaserver/fhir/")
    patients = client.get_patient_list(1840082)
    patient = client.get_basic_patient_info(1840080)
    patient_cholesterol_data = client.get_patient_data(1840080)
    patient.update_data(patient_cholesterol_data)
    for i in range(len(patients)):
        print(str(patients.get_patient_list()[i].first_name)+" "+patients.get_patient_list()[i].last_name)
    print(str(patient.first_name)+" "+str(patient.last_name))
