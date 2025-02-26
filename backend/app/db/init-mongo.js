db = db.getSiblingDB('feature_store');

// Criar coleção features se não existir
if (!db.getCollectionNames().includes('features')) {
    db.createCollection('features');
    print("Coleção 'features' criada com sucesso!");
}

// Criar coleção feature_groups se não existir
if (!db.getCollectionNames().includes('feature_groups')) {
    db.createCollection('feature_groups');
    print("Coleção 'feature_groups' criada com sucesso!");
}

// Criar alguns índices úteis
db.features.createIndex({ "name": 1 }, { unique: true });
db.feature_groups.createIndex({ "name": 1 }, { unique: true });
