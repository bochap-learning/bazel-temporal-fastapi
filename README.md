# About The Project   

This project showcases the development of a robust and efficient data pipeline. It demonstrates the ability to seamlessly integrate with external APIs to retrieve data, efficiently process and store this data in a PostgreSQL database, and expose it through user-friendly FastAPI endpoints.

The project leverages Docker for containerization, ensuring consistent and reliable deployment across different environments.  Furthermore, it employs Bazel as a build tool for configurable bundling, optimized builds, and comprehensive code testing.

To enhance data processing capabilities, the project utilizes Temporal for workflow orchestration. This enables asynchronous ETL (Extract, Transform, Load) processes with features like queuing and automatic retries, ensuring data reliability.  Finally, it integrates Minio as a scalable and efficient blob storage backend for handling large datasets and facilitating data processing.

This project effectively combines these technologies to create a comprehensive data solution that is scalable, maintainable, and fault-tolerant.

## Architecture

![Architecture Diagram](docs/design/images/architecture.gif)

## Getting Started

### Prequisites

To make it easier to run the application, an `.env` file is used to supply environment variables for running the application and also Docker compose

### Running

#### Standalone

Running via Docker compose (**Doesn't work yet due to imaging issues**)
```
docker compose --env-file .env -f config/docker/docker-compose.yml up -d
```

#### Development (Requires Bazel)

1. Running supporting services including Temporal Cluster, Postgres Databases and Minio

```
docker compose --env-file .env -f config/docker/docker-compose.yml up -d
```

2. Start FastAPI
```
IS_LOCAL=1 bazel run //service/api:service_api_run
```

3. Start Temporal Worker
```
IS_LOCAL=1 bazel run //service/zipcode:service_zipcode_workflow_worker
```

## Technologies

| Technology | Required | Usage |
|---|---|---|
| FastAPI | Required | Exposes data using REST style. Possible improvements include adding security and making patient and observation endpoints call microservices for scability. |
| PostgreSQL | Required | Uses SQLModel to handle CRUD operations for REST calls. Makes use of COPY from blob storage and Merge commands that reduces computation during the Zipcode ETL process. |
| Docker | Required | Makes use of Docker compose of setting up the required supporting services. Application code imaging was unfortunately unsuccessful due to complexities introduced by Bazel  |
| Bazel | Optional | Provided an easy way to perform bundling and dependency management. It allowed domain based code structuring. Unfortunately due to upgrades caused issues that fails the Docker containization test.  |
| Temporal | Optional | Orchestrates asynchronous ETL processes, ensuring data reliability. The workflow management ablities provide some of the more impressive features of this applicaiton |
| Minio | Optional | Provides scalable and efficient blob storage for handling large datasets |
| Jupyter Notebook with Pandas | Optional | Used during prototyping to explore the HAPI FHIR api data and allowed testing code for implementation |

#### Directory Structure

```bash
.
├── LICENSE
├── MODULE.bazel
├── MODULE.bazel.lock
├── README.md
├── WORKSPACE
├── config
│   └── docker         # docker related files 
├── docs
│   ├── design
│   │   └── images     # images usded by documentation
│   └── research
│       └── patients_and_observations.ipynb # notebook used for research
├── library
│   ├── converter
│   │   └── memory.py               # shared code to convert data into memory streams
│   ├── meta
│   │   ├── env.py                  # shared code for accessing environment variables
│   │   └── metaclass.py            # shared code for example to deal with Singleton
│   ├── orchestration               # shared temporal activities
│   ├── storage
│   │   ├── blob_minio.py           # code to manipulate minio blob storage
│   │   └── postgres.py             # code to manipulate postgre storage
│   └── webclient                   # code to manipulate external serivces like calling rest apis
├── service
│   ├── api                         # fast api code
│   ├── observation                 # extracting and manipulating observation data including temporal activities
│   ├── patient                     # extracting and manipulating patient data including temporal activities
│   └── zipcode                     # temporal activites and workflows to handle patient and observation data
├── third_party                     # requirements for allowing bazel to build code with python dependencies

└── tools
    └── runner                      # helper function to run tests
```

### Benefits

- SQLModel allowed reducing the boilerplate for data access in Postgres. The ORM allow handles security features like SQL injection automatically. The models can also return directly as FastAPI responses with fields remove easily.
- Jupyter Notebook Pandas allowed initial research of the API data allowing implementation code to be broken into smaller parts with unit tests.
- Minio allowed storage of processed data in CSVs which provides ability to accumulate records to be populated in a batch instead of running multiple queries that incur both latency and processing requirements on the server. This is especially beneficial for observation data which requires 1 API call per patient. This benefit is increased give that the population of a zipcode can be anywhere from 0 to more than 100,000 with an average of 9,000. Just taking an average of 10% at 1,000  will impact performance and latency. Refer to the footnote [^1]
- Bazel allow structuring files togather in their domain folders for easily management due to code proximity. Bunding and dependency management is also easier with a single command once setup is completed.
- Temporal is the prized Jewel of this implementation. The ability to manage workflow state allows automatic recovery if conditions are fulfil. Certain code bugs can be rerun from the failed step conserving resources to rerun from start.
![Rerun from failed task](docs/design/images/retry-from-failure.png)
- Temporal's workflow and activity code seperation while maintaining relationships allow the ability for queueing up tasks and running them in a concurrent manner safely. Code like the following improves performance while also allowing easy handling of rate limits. While the relationships allowed multiple complex tasks to be managd easily and also scaled by just adding more workers. Paging of results can also be easily managed by related workflows.
 ```python
         while patient_ids:
            subtasks = []
            for _ in range(min(len(patient_ids), 5)):
                patient_id = patient_ids.pop()
                # process mini batches                  

 ```
 <table>
    <tr>
        <td><img src="docs/design/images/temporal-concurrent.png" alt="Rerun from failed task"/> </td>
        <td><img src="docs/design/images/data-persistent.png" alt="Inserted data" /> </td>
    </tr>
 </table>

### Tradeoffs

- Bazel introduces complexity that requires time and resources to learn. A successful framework like Bazel has its flaws with changes that documentation has not caught up with that resulted in the failure to produce Docker images.
- Temporal and Minio with all its benefits introduce new systems that required efforts to upkeep and maintain. Although Minio can be easily replaced by S3, GCP Cloud Storage or Azure Blobs.
- Temporal also requires an understanding in order to make use of its benefits fully. It also requires the developer to have the ability to create Idimpotent workflows. 

### Asssumptions and missing tasks
- Docker compose and also Docker file creation is covered with teh Postgres image creation. But the FastAPI and Temporal could not be packaged due to issues understanding teh changes in Bazel rules.
- All data manipulation is assumed to be addition and updates. Deletions are not supported in teh implementation.
- 
### Footnotes

[^1]: [ZIP Code General Demographic Characteristics](https://proximityone.com/zip16dp1.htm)