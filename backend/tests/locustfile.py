from locust import HttpUser, task, between
from faker import Faker

fake = Faker()

class FeatureStoreUser(HttpUser):
    wait_time = between(1, 3)  # tempo entre requisições

    def on_start(self):
        """Executado quando um usuário inicia"""
        # Login (se necessário)
        pass

    @task(3)
    def get_feature(self):
        """Consulta uma feature"""
        feature_id = fake.uuid4()
        self.client.get(f"/api/v1/features/{feature_id}")

    @task(2)
    def create_feature(self):
        """Cria uma nova feature"""
        feature_data = {
            "name": fake.word(),
            "description": fake.sentence(),
            "type": fake.random_element(["numeric", "categorical", "temporal"]),
            "metadata": {
                "owner": fake.name(),
                "team": fake.company(),
                "tags": fake.words(3)
            }
        }
        self.client.post("/api/v1/features", json=feature_data)

    @task(1)
    def update_feature(self):
        """Atualiza uma feature existente"""
        feature_id = fake.uuid4()
        update_data = {
            "description": fake.sentence(),
            "metadata": {
                "updated_by": fake.name(),
                "update_reason": fake.sentence()
            }
        }
        self.client.put(f"/api/v1/features/{feature_id}", json=update_data)

    @task(2)
    def get_feature_value(self):
        """Consulta o valor de uma feature"""
        feature_id = fake.uuid4()
        entity_id = fake.uuid4()
        self.client.get(f"/api/v1/features/{feature_id}/values/{entity_id}")

    @task(1)
    def create_feature_value(self):
        """Cria um novo valor de feature"""
        feature_id = fake.uuid4()
        entity_id = fake.uuid4()
        value_data = {
            "value": fake.random_number(digits=3),
            "timestamp": fake.iso8601(),
            "metadata": {
                "source": fake.company(),
                "confidence": fake.random.uniform(0, 1)
            }
        }
        self.client.post(f"/api/v1/features/{feature_id}/values/{entity_id}", json=value_data)
