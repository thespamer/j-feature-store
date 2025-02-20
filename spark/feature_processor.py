from pyspark.sql import SparkSession
from pyspark.sql.functions import *
from pyspark.sql.types import *
import json
import os

class FeatureProcessor:
    def __init__(self):
        self.spark = SparkSession.builder \
            .appName("FStore Feature Processor") \
            .config("spark.sql.warehouse.dir", "/tmp/spark-warehouse") \
            .getOrCreate()
        
        # Set log level
        self.spark.sparkContext.setLogLevel("WARN")
        
        # Initialize Postgres connection properties
        self.postgres_properties = {
            "url": os.getenv("POSTGRES_URI"),
            "driver": "org.postgresql.Driver"
        }

    def process_batch_features(self, feature_group, data, transformation):
        """Process batch features using Spark"""
        try:
            # Convert input data to Spark DataFrame
            input_df = self.spark.createDataFrame(data)
            
            # Register DataFrame as temp view
            input_df.createOrReplaceTempView("input_data")
            
            # Apply transformation
            if transformation.startswith("SQL:"):
                # SQL transformation
                sql = transformation.replace("SQL:", "").strip()
                result_df = self.spark.sql(sql)
            else:
                # Python transformation
                # Note: In production, you'd want to implement proper security measures
                transform_func = eval(transformation)
                result_df = transform_func(input_df)
            
            # Write results to Postgres
            result_df.write \
                .jdbc(url=self.postgres_properties["url"],
                     table=f"features_{feature_group}",
                     mode="append",
                     properties=self.postgres_properties)
            
            return {"status": "success", "rows_processed": result_df.count()}
            
        except Exception as e:
            return {"status": "error", "message": str(e)}

    def compute_feature_statistics(self, feature_group):
        """Compute statistics for features in a feature group"""
        try:
            # Read feature data from Postgres
            df = self.spark.read \
                .jdbc(url=self.postgres_properties["url"],
                     table=f"features_{feature_group}",
                     properties=self.postgres_properties)
            
            # Compute statistics
            stats = df.describe().collect()
            
            # Compute additional metrics
            numeric_cols = [f.name for f in df.schema.fields if isinstance(f.dataType, (IntegerType, DoubleType))]
            
            for col in numeric_cols:
                # Add additional statistics
                skewness = df.select(skewness(col)).collect()[0][0]
                kurtosis = df.select(kurtosis(col)).collect()[0][0]
                
                # Add to stats
                stats.append({
                    "metric": "skewness",
                    col: skewness
                })
                stats.append({
                    "metric": "kurtosis",
                    col: kurtosis
                })
            
            return {"status": "success", "statistics": stats}
            
        except Exception as e:
            return {"status": "error", "message": str(e)}

    def detect_drift(self, feature_group, window_size="7d"):
        """Detect feature drift over time"""
        try:
            # Read recent feature data
            df = self.spark.read \
                .jdbc(url=self.postgres_properties["url"],
                     table=f"features_{feature_group}",
                     properties=self.postgres_properties)
            
            # Add timestamp window
            df = df.withColumn("window", window("timestamp", window_size))
            
            # Compute statistics per window
            window_stats = df.groupBy("window") \
                .agg(*[
                    collect_list(c).alias(c)
                    for c in df.columns if c not in ["window", "timestamp"]
                ])
            
            # Compare windows to detect drift
            # This is a simplified implementation
            # In production, you'd want to use proper drift detection algorithms
            
            return {"status": "success", "drift_metrics": window_stats.collect()}
            
        except Exception as e:
            return {"status": "error", "message": str(e)}

if __name__ == "__main__":
    processor = FeatureProcessor()
    # Start processing loop or API server here
