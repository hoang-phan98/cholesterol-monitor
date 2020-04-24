import requests


class FHIRClient:
    def __init__(self, root_url):
        self.root_url = root_url

    def get_patient_list(self, practitioner_id):
        res = requests.get(self.root_url+"Encounter?practitioner="+str(practitioner_id)+"&_count=100")
        data = res.json()
        return data


if __name__ == '__main__':
    client = FHIRClient("https://fhir.monash.edu/hapi-fhir-jpaserver/fhir/")
    encounters = client.get_patient_list(4821912)
    patient_list = []
    for encounter in encounters["entry"]:
        patient_name = encounter["resource"]["subject"]["display"]
        if patient_name not in patient_list:
            patient_list.append(patient_name)

    print(patient_list)
