import requests
from abc import ABC, abstractmethod


class FHIRClient(ABC):
    def __init__(self, root_url):
        self.root_url = root_url

    def get_patient_list(self, practitioner_id):
        next_page = True
        next_url = self.root_url+"Encounter?practitioner="+str(practitioner_id)+"&_count=10"
        page_count = 0
        patient_list = []

        while next_page:
            res = requests.get(next_url)
            data = res.json()
            for encounter in data["entry"]:
                patient_name = encounter["resource"]["subject"]["display"]
                if patient_name not in patient_list:
                    patient_list.append(patient_name)

            next_page = False
            links = data["link"]
            for i in range(len(links)):
                link = links[i]
                if link['relation'] == 'next':
                    next_page = True
                    next_url = link['url']
                    page_count += 1
            
        return patient_list

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
        cholesterol_value = data["entry"][0]["resource"]["valueQuantity"]["value"]
        effective_date_time = data["entry"][0]["resource"]["effectiveDateTime"]
        return cholesterol_value, effective_date_time


if __name__ == '__main__':
    client = CholesterolDataClient("https://fhir.monash.edu/hapi-fhir-jpaserver/fhir/")
    patients = client.get_patient_list(4821912)
    patient_cholesterol = client.get_patient_data(1840080)
    print(patients)
    print(patient_cholesterol)
