from pyspark.sql import SparkSession
from pyspark.sql.functions import *
from pyspark.sql.types import StructType, StructField, StringType, LongType, DoubleType

KAFKA_BROKER = "localhost:29092,localhost:30092,localhost:49092"
SOURCE_TOPIC = "financial_transactions"
AGGREGATES_TOPIC = "transactions_aggregates"
ANOMALIES_TOPIC = "transactions_anomalies"
CHECKPOINT_DIR = "/mnt/spark_checkpoint"
STATES_DIR = "/mnt/spark_states"

spark = (SparkSession.builder
         .appName('FinancialTransactionsProcessor')
         .config('spark.jars.packages', 'org.apache.spark:spark-sql-kafka-0-10_2.12:3.5.0')
         .config('spark.sql.streaming.checkpointLocation', CHECKPOINT_DIR)
         .config('spark.sql.streaming.stateStore.stateStoreDir', STATES_DIR)
         .config('spark.sql.shuffle.partitions', )
         
).getOrCreate()

spark.sparkContext.setLogLevel("WARN")

transaction_schema = StructType([
    StructField(name:'transactionId', StringType(), nullable:True),
    StructField(name:'userId', StringType(), nullable:True),
    StructField(name:'merchantId', StringType(), nullable:True),
    StructField(name:'amount', DoubleType(), nullable:True),
    StructField(name:'transactionTime', LongType(), nullable:True),
    StructField(name:'transactionType', StringType(), nullable:True),
    StructField(name:'location', StringType(), nullable:True),
    StructField(name:'paymentMethod', StringType(), nullable:True),
    StructField(name:'isInternational', StringType(), nullable:True),
    StructField(name:'currency', StringType(), nullable:True),
])
