db = db.getSiblingDB('feature_store');

// Create collections if they don't exist
db.createCollection('feature_groups');
db.createCollection('features');
db.createCollection('pipelines');

// Create indexes
db.feature_groups.createIndex({ "name": 1 }, { unique: true });
db.features.createIndex({ "name": 1, "feature_group_id": 1 }, { unique: true });
db.features.createIndex({ "feature_group_id": 1 });
db.pipelines.createIndex({ "name": 1 }, { unique: true });
db.pipelines.createIndex({ "feature_group_id": 1 });

// Create TTL index for pipeline runs
db.pipeline_runs.createIndex({ "created_at": 1 }, { expireAfterSeconds: 604800 }); // 7 days
