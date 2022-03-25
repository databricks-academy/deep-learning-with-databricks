# Databricks notebook source
spark.conf.set("com.databricks.training.module-name", "deep-learning")
spark.conf.set("com.databricks.training.expected-dbr", "9.1")

import warnings
warnings.filterwarnings("ignore")

import numpy as np
np.set_printoptions(precision=2)

import logging
logging.getLogger("tensorflow").setLevel(logging.ERROR)

displayHTML("Preparing the learning environment...")
None # Suppress output

# COMMAND ----------

# MAGIC %run "./Class-Utility-Methods"

# COMMAND ----------

username = getUsername()
userhome = getUserhome()
course_dir = getCourseDir()
datasets_dir = f"{course_dir}/datasets"

#source_path = f"wasbs://courseware@dbacademy.blob.core.windows.net/scalable-deep-learning-with-tensorflow-and-apache-spark/v01"
source_path = f"wasbs://courseware@dbacademy.blob.core.windows.net/deep-learning-with-databricks/v01"

working_dir = getWorkingDir()

dbutils.fs.mkdirs(userhome)
dbutils.fs.mkdirs(course_dir)
dbutils.fs.mkdirs(working_dir)
None # Suppress output

# COMMAND ----------

def path_exists(path):
    try:
        return len(dbutils.fs.ls(path)) >= 0
    except Exception:
        return False

def install_datasets(reinstall=False):
    min_time = "3 min"
    max_time = "10 min"

    # You can swap out the source_path with an alternate version during development
    # source_path = f"dbfs:/mnt/work-xxx/{course_name}"
    print(f"The source for this dataset is\n{source_path}/\n")

    # Change the final directory to another name if you like, e.g. from "datasets" to "raw"
    target_dir = f"{datasets_dir}"
    print(f"Your dataset directory is\n{target_dir}\n")
    existing = path_exists(target_dir)

    if not reinstall and existing:
        print(f"Skipping install of existing dataset.")
        return 

    # Remove old versions of the previously installed datasets
    if existing:
        print(f"Removing previously installed datasets from\n{target_dir}")
        dbutils.fs.rm(target_dir, True)

    print(f"""Installing the datasets to {target_dir}""")

    print(f"""\nNOTE: The datasets that we are installing are located in Washington, USA - depending on the
          region that your workspace is in, this operation can take as little as {min_time} and 
          upwards to {max_time}, but this is a one-time operation.""")

    print("""\nInstalling the dataset...""")
    dbutils.fs.cp(source_path, target_dir, True)

    print(f"""\nThe install of the datasets completed successfully.""")  

def list_r(path, prefix=None, results=None):
    if prefix is None: prefix = path
    if results is None: results = list()
    
    files = dbutils.fs.ls(path)
    for file in files:
        data = file.path[len(prefix):]
        results.append(data)
        if file.isDir(): list_r(file.path, prefix, results)
        
    results.sort()
    return results

def validate_datasets():
    import time
    start = int(time.time())
    print(f"\nValidating the local copy of the datsets", end="...")
    
    local_files = list_r(datasets_dir)
    remote_files = list_r(source_path)

    for file in local_files:
        if file not in remote_files:
            print(f"\n  - Found extra file: {file}")
            print(f"  - This problem can be fixed by reinstalling the datasets")
            raise Exception("Validation failed - see previous messages for more information.")

    for file in remote_files:
        if file not in local_files:
            print(f"\n  - Missing file: {file}")
            print(f"  - This problem can be fixed by reinstalling the datasets")
            raise Exception("Validation failed - see previous messages for more information.")
        
    print(f"({int(time.time())-start} seconds)")

# COMMAND ----------

try:
    reinstall = dbutils.widgets.get("reinstall").lower() == "true"
    install_datasets(reinstall=reinstall)
except:
    install_datasets(reinstall=False)
    
validate_datasets()

None # Suppress output

# COMMAND ----------

# Used to initialize MLflow with the job ID when ran under test
def init_mlflow_as_job():
    import mlflow
    job_experiment_id = sc._jvm.scala.collection.JavaConversions.mapAsJavaMap(
        dbutils.entry_point.getDbutils().notebook().getContext().tags()
      )["jobId"]

    if job_experiment_id:
        mlflow.set_experiment(f"/Curriculum/Test Results/Experiments/{job_experiment_id}")
    
init_mlflow_as_job()

None # Suppress output

# COMMAND ----------

courseAdvertisements = dict()
courseAdvertisements["username"] =     ("v", username,     "No additional information was provided.")
courseAdvertisements["userhome"] =     ("v", userhome,     "No additional information was provided.")
courseAdvertisements["working_dir"] =  ("v", working_dir,  "No additional information was provided.")
allDone(courseAdvertisements)
None # Suppress output

