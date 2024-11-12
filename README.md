# About The Project   

This project showcases the development of a robust and efficient data pipeline. It demonstrates the ability to seamlessly integrate with external APIs to retrieve data, efficiently process and store this data in a PostgreSQL database, and expose it through user-friendly FastAPI endpoints.

The project leverages Docker for containerization, ensuring consistent and reliable deployment across different environments.  Furthermore, it employs Bazel as a build tool for configurable bundling, optimized builds, and comprehensive code testing.

To enhance data processing capabilities, the project utilizes Temporal for workflow orchestration. This enables asynchronous ETL (Extract, Transform, Load) processes with features like queuing and automatic retries, ensuring data reliability.  Finally, it integrates Minio as a scalable and efficient blob storage backend for handling large datasets and facilitating data processing.

This project effectively combines these technologies to create a comprehensive data solution that is scalable, maintainable, and fault-tolerant.

This application, built in less than a week, serves as a proof-of-concept, showcasing enterprise-level techniques for data processing and application development. While not production-grade, it offers valuable insights into these practices.

## Requirements

### Functional Requirements

1. Ingesting data for patients and observation from `HAPI FHIR API endpoints`
   1. /zipcodes
      1. POST /zipcodes {zipcode: 12345}
2. Retrieving data for patients and observation
   1. /patients
      1. /patients/[patient_id]
      2. /patient?first_name=[first_name]
   2. /observations
      1. GET /observations?patient_id=[patient_id]

### Non-Functional Requirements

1. Performance
   1. Low response time
   2. High throughput
   3. Low Latency
2. Scalability
   1. Ability to handle increasing traffic
   2. Ability to handle increasing data volumne
3. Portability
   1. Ease of moving application between environments
   2. Reversible techonology and implementation decisions
4. Reliablilty
   1. Fault tolerance
   2. Data integrity
   3. Data consistency
   4. Monitoring and logging   
5. Security
   1. Authentication and Authorization
   2. Data Protection
   3. Input Validation
   4. Output Encoding
   5. Rate Limiting
   6. Audting and logging
6. Availablity
   1. Infrastructure redundancy
   2. Error handling and fault tolerance
   3. Deployment and Maintenance
7. Maintainablity and Usability
   1. Code organization and structure
   2. API Design and documentation
   3. Versioning
   4. Testing
   5. Logging and Monitoring

## Architecture

![Architecture Diagram](docs/design/images/architecture.gif)

### Code Structure
```bash
.
├── config
│   └── docker                   # docker confirguration files for running a standalone cluster and also local development cluster
│       ├── postgres-with-curl   # docker build files for building postgres image with curl
│       ├── temporal             # docker configuration files used form temporal
│       ├── vault-seed           # docker build files and code for application to seed vault connection and access control data
├── docs
│   ├── design
│   │   └── images               # images used by documentation
│   └── research
│       └── patients_and_observations.ipynb   # notebook used for research
├── library
│   ├── client
│   │   └── factory.py           # shared code to construct clients for minio, postgres, and vault for used in the services
│   ├── converter
│   │   └── memory.py            # shared code to convert data into memory streams
│   ├── meta
│   │   ├── config.py            # shared code to obtained enviroment values (vault or local running flags)
│   │   └── metaclass.py         # shared code for meta classes like Singleton
│   ├── orchestration
│   │   ├── activity.py          # shared code for generic temporal activities with no business specific logic. (example: custom sql execution)
│   │   └── model.py             # shared code for model used by generic temporal activitie. (example: input or output parameters)
│   ├── storage
│   │   ├── blob_minio.py        # shared code to manipulate minio blob storage
│   │   ├── postgres.py          # shared code to manipulate postgres storage
│   │   └── vault.py             # shared code to manipulate vault storage
│   └── webclient
│       └── rest.py              # shared code to interact with external rest api services
├── service
│   ├── api
│   │   ├── run.py               # entry point to run fast api server with ASGI (Asynchronous Server Gateway Interface) framework
│   │   └── server.py            # fast api server code
│   ├── observation
│   │   ├── data                 # data use for testing observation
│   │   ├── activity.py          # code for temporal actvity code to work with observation data
│   │   ├── extractor.py         # code to extract observation data from raw data provided by HAPI FHIR API
│   │   ├── model.py             # code for models used in temporal activites, persistent storage or FastAPI
│   │   └── shared.py            # code for constant values or generic functions used for processing observation data
│   ├── patient                  
│   │   ├── data                 # data use for testing patient
│   │   ├── activity.py          # code for temporal actvity code to work with patient data
│   │   ├── extractor.py         # code to extract patient data from raw data provided by HAPI FHIR API
│   │   ├── model.py             # code for models used in temporal activites, persistent storage or FastAPI
│   │   └── shared.py            # code for constant values or generic functions used for processing patient data
│   └── zipcode
│       ├── model.py             # code for models used in temporal workflow, FastAPI
│       ├── shared.py            # code for constant values or generic functions used for processing zipcode data
│       ├── worker.py            # code for temporal workers
│       └── workflow.py          # code for temporal workflow processing patient and observation data related to provided zipcode
├── tools
│   └── runner
│       ├── defs.bzl             # rule file to provide customizations to support pytesting
│       └── pytest_runner.py     # code wrapper to allow bazel to run pytest directly
├── README.md
├── py_layer.bzl                 # rule file to provide layering support for Python applications built as OCI images
├── requirements.in              # pip dependency declaration used by application
└── requirements_lock.txt        # lock file pip dependency declaration used by application used by imaging
```
<sub>Non critical file like `xx_test.py`, `__init__.py` or `Bazel` related files are obmitted unless it details a complex or custom detail of the application</sub>

## Getting Started

### Prerequisites

The application makes use of supporting services for relational data (Postgres), blob (Minio), secrets (Vault) and workflow management (Temporal/ Postgres). Configuration and access information used for setting up the services are provided in an `.env` file. The format and variables required can be found in [.env.template](.env.template). The `.env` file should be placed in [config/docker/vault-seed](config/docker/vault-seed)


### Building

The application is broken into 3 different parts during the build process. The 3 parts are

1. External dependencies used by application code
This part generates the `requirements_lock.txt` and `MODULE.bazel.lock` file, this is platform dependant since the packages used in Linux and MacOS is different and are not compatible. Currently building of Open Container Intiative (OCI) compatible images is supported on linux hosts since the images used a linux base during runtime.
```
bazel run //:requirements.update
```
2. Shared code used by all application services
```
bazel build //library/...
```
3. Application services (API and Temporal workers)
```
bazel build //service/...
```

### Running

#### Standalone

Running via Docker compose (**Actively working to resolve imaging issues that are preventing deployment through Docker Compose. This feature will be available soon.**)
```
docker compose --env-file config/docker/vault-seed/.env -f config/docker/docker-compose.yml -f config/docker/docker-compose.overrides.yml up -d
```

#### Development on local (Requires Bazel)

1. Running supporting services (Temporal Cluster, Postgres Databases and Minio)

```
docker compose --env-file config/docker/vault-seed/.env -f config/docker/docker-compose.local.yml -f config/docker/docker-compose.local.overrides.yml up -d
```

2. Start FastAPI
```
VAULT_HOST=[YOUR_HOST] VAULT_PORT=[YOUR_PORT] VAULT_TOKEN=[YOUR_TOKEN] VAULT_PATH=[YOUR_PATH] IS_LOCAL=1 bazel run //service/api:service_api_run
```

3. Start Temporal Worker
```
VAULT_HOST=[YOUR_HOST] VAULT_PORT=[YOUR_PORT] VAULT_TOKEN=[YOUR_TOKEN] VAULT_PATH=[YOUR_PATH] IS_LOCAL=1 bazel run //service/zipcode:service_zipcode_workflow_worker
```

<sub>* `bazel run` doesn't provide options to provide enviroment variables as arguments. So we need to set the environment variables via the shell before runnning</sub>


#### Testing on local (Requires Bazel)

1. library tests
```
bazel test //library/... --action_env VAULT_HOST=[YOUR_HOST] --action_env VAULT_PORT=[YOUR_PORT] --action_env VAULT_TOKEN=[YOUR_TOKEN] --action_env VAULT_PATH=[YOUR_PATH]  --action_env IS_LOCAL=1
```
2. service tests
```
bazel test //service/... --action_env VAULT_HOST=[YOUR_HOST] --action_env VAULT_PORT=[YOUR_PORT] --action_env VAULT_TOKEN=[YOUR_TOKEN] --action_env VAULT_PATH=[YOUR_PATH]  --action_env IS_LOCAL=1
```

<sub>* `bazel test` allows the use of `action_env` to provide enviroment variables as arguments to run the command with the enviroment variables set.</sub>

### Swagger

Once the FastAPI server is running the Swagger UI can be used to view or test the endpoints at http://HOSTNAME:PORT/docs.

![Swagger UI](docs/design/images/swagger.png)

## Technologies

| Technology | Requirement | Level of Usage |
|---|---|---|
|FastAPI| Required|☀️|
|PostgreSQL| Required|☀️|
|Docker| Required|⛅️|
|HashiCorp Vault| Optional|⛅️|
|Bazel| Optional|⛅️|
|Temporal| Optional|☀️|
|Minio| Optional|☀️|
|Jupyter Notebook with Pandas| Optional|☀️|

<sub>Legend: ☀️ - Fulfils requirements specified or planned usage, ⛅️ - Partially fulfils requirements specified or planned usage</sub>

### Decision making process

This application leverages a combination of essential and optional technologies to achieve its core functionality and offer enhanced features. This section explores the some of the technology choices or implementation details and tradeoffs associated with these details.

#### Technology choices and implementation Details

- **FastAPI**: application adheres to RESTful principles, employing standard GET and POST requests for intuitive resource access. This familiar design, well-suited to FastAPI's framework,  ensures easy comprehension for consumers and facilitates future enhancements.  FastAPI's built-in features further enhance the developer experience by auto-generating Swagger documentation and providing an interactive playground for API exploration.
- **Docker**: This project successfully containerized Postgres using Docker Compose and Dockerfiles, enabling `curl` within the Postgres container for easier deployment and standalone execution of supporting services. However, containerization of the core FastAPI application and Temporal worker is restricted to only Linux hosts due to challenges with Bazel rules. Addressing this containerization gap is a high priority for future development.
- **SQLModel**: streamlined database interactions by minimizing boilerplate code for Postgres access. Its built-in ORM capabilities automatically address security concerns such as SQL injection vulnerabilities. Additionally, SQLModel offers seamless integration with FastAPI, allowing models to be returned directly as API responses with effortless field filtering.
- **Jupyter Notebook and Pandas**: instrumental in the initial exploration and analysis of the HAPI FHIR API data. This facilitated a modular approach to implementation, allowing the code to be broken down into smaller, testable units with comprehensive unit tests for efficient implementation.
- **Minio**: efficient blob storage facilitates batch processing of data by storing processed records in CSVs. This approach significantly reduces the server load and latency associated with individual API calls, particularly for observation data which requires fetching information per patient. Considering the wide range of population sizes per zip code (from 0 to over 100,000, with an average of 9,000. Refer to the footnote [^1]), retrieving observation data individually could severely impact performance. By leveraging Minio and batch processing, we optimize data ingestion and minimize the overhead of numerous API calls. This is further enhanced by using efficient database loading techniques like `COPY` and `MERGE`.
- **Bazel**: facilitates a domain-driven code structure by enabling the organization of files within their respective domain folders. This enhances code manageability and improves developer understanding through proximity. Bazel also streamlines dependency management, allowing for easy bundling with a single command once the initial setup is complete.
- **PostgreSQL**: implementation  employs a hybrid approach to database interaction. SQLModel, an ORM, simplifies common CRUD operations, schema management, and query execution while mitigating security risks like SQL injection. This significantly reduces boilerplate code and ensures efficient data access. For the ETL pipeline, which handles data extracted from the HAPI FHIR API, we opted for custom SQL statements leveraging `COPY` and `MERGE` commands. This strategic choice optimizes bulk data loading and ensures idempotent operations for robust error handling and reliable execution.  The use of custom SQL in this context is considered safe due to the pre-processing of data within the application code, minimizing vulnerabilities like SQL injection.
- **Temporal**: the powerhouse behind this application's robust ETL processes. Its advanced workflow orchestration capabilities provide:
    - **Asynchronous Operations and Reliability**: Temporal manages ETL tasks asynchronously, ensuring efficient resource utilization and reliable execution even with interruptions.
    - **Fault Tolerance and Recovery**: Temporal's state management allows automatic recovery from failures, enabling seamless continuation from the point of failure and preventing unnecessary resource consumption.
    - **Concurrency and Scalability**: Temporal's clear separation of workflow and activity logic facilitates safe concurrent execution of tasks. This enables efficient handling of rate limits and simplifies scaling by adding more workers.
    - **Simplified Complex Workflow Management**: Temporal excels at managing complex, multi-step workflows, including those requiring paging through large datasets. This also allows paging data in the Patient API to be implemented easily
    - **Intuitive Dashboards and Visualizations**: A well-designed UI with informative dashboards and visualizations can provide a clear overview of system health, resource utilization, and key performance indicators (KPIs). This empowers operations teams to proactively monitor and manage the application.
    - **Alerting and Notification System**: Implementing an alerting and notification system within the UI can help operations teams stay informed about critical events, potential issues, and performance anomalies. This ensures timely intervention and prevents escalations.
    - **Support for optional 3rd party integrations**: allows optional integrations with Elasticsearch, Grafana, and Prometheus to enhance production operations. These tools provide robust logging, monitoring, and visualization capabilities, enabling efficient troubleshooting, performance optimization, and proactive issue identification.
    - The included images illustrate Temporal's ability to:
        - Retry from Failure: Visualizing how Temporal automatically restarts workflows from the failed step. ![Rerun from failed task](docs/design/images/retry-from-failure.png)
        - Maintain Data Persistence: Highlighting Temporal's ability to preserve workflow data, ensuring reliability and recoverability. ![Inserted data](docs/design/images/data-persistent.png)
        - Enable Concurrent Execution: Showcasing Temporal's capability to manage concurrent tasks efficiently. ![Concurrent execution](docs/design/images/temporal-concurrent.png)
        The code snippet uses a BFS-inspired approach to efficiently process API requests in micro-batches. By grabbing a small set of IDs, making concurrent API calls, and waiting for responses before repeating, it prevents API overload while maximizing efficiency. This method also simplifies the implementation of rate limiting logic.
         ```python
        # BFS technique
         while patient_ids:
            subtasks = []
            for _ in range(min(len(patient_ids), 5)):
                patient_id = patient_ids.pop()
                # process mini batches by making non blocking api calls asynchronously
            # await subtasks to be completed
        
        # process results for all patients
        ```
- **Vault**: offers a secure and streamlined approach to managing connections and credentials for inter-process communication. By centralizing this sensitive information, Vault eliminates the need to embed it directly in application code or package images. This approach not only enhances security but also simplifies management by providing a single, centralized platform for controlling access to and updating these critical details, separate from the code repository.

### Tradeoffs
- While the application provides a Swagger interface generated from custom defaults, the current user experience could be improved for better API comprehension.  Although not implemented here, customization of the Swagger documentation is readily achievable, offering an opportunity to enhance the consumer experience.
- This implementation prioritizes a clear data processing workflow and efficient RDBMS interaction over comprehensive security. To maintain simplicity, security measures are streamlined, focusing on mitigating potential latency and request volume issues. Future enhancements could include stronger security with JWT and decoupling database access through microservices.
- This implementation prioritizes straightforwardness over extreme scalability for the Get API calls. While current performance is adequate thanks to SQL indexes,  it could be further enhanced to handle very high loads.  Options include migrating resources to dedicated microservices or introducing caching mechanisms and database replicas.
- Bazel offers compelling advantages, but its complexity and rapidly evolving nature, coupled with occasional documentation gaps, demands a significant upfront investment in learning and knowledge sharing within development teams. This project faced challenges in Docker image creation due to recent Bazel changes. However, mastering Bazel can unlock streamlined containerization across diverse platforms, including ARM and AMD architectures.
- While Temporal and Minio offer compelling advantages, they introduce new systems requiring ongoing maintenance. Minio's compatibility with S3, GCP Cloud Storage, or Azure Blobs provides flexibility.  Temporal's cloud-managed solution for clusters (excluding workers) offers an alternative to self-hosting, trading higher operating expenses for reduced staffing costs associated with complex on-premise deployments.
- To fully leverage Temporal's capabilities, developers need a solid understanding of its concepts and best practices, including the crucial ability to design idempotent workflows. This requires developers to adopt Temporal's opinions and patterns, but in return, they gain a significant reduction in writing and maintaining boilerplate code for features like state management, retry logic, and durability, which Temporal handles automatically.
- SQLModel simplifies CRUD operations with its ORM features, but it presents challenges when dealing with streaming or micro-batching data processing.  Leveraging SQLModel's advanced features for such tasks can introduce complexities, as encountered with session table cleanup.  A workaround involving an extra TRUNCATE call effectively addressed this specific issue, though it highlights potential quirks when pushing the framework beyond basic use cases.
- This project focuses on unit testing core application logic, but acknowledges that full code coverage isn't achieved.  Testing of external packages is skipped, relying on the stability of well-established open-source tools.  While Temporal activities are unit tested, workflow tests are temporarily disabled due to previously encountered issues with Temporal's auto-retry mechanism and network resolving complexities. Integration and end-to-end tests are limited to manage the inherent complexity of this distributed proof-of-concept.
-  Implementing Vault introduces another system to manage, incurring additional costs for infrastructure, personnel training, and ongoing maintenance.  However, these costs can be offset by reduced security risks and improved operational efficiency, especially for larger organizations with complex infrastructure.  Furthermore, integrating Vault requires adding code to your applications for secrets retrieval, potentially introducing latency. This performance impact can be minimized with careful implementation and optimization techniques like caching. Finally, while the initial setup for small applications might seem complex, Vault's automation features and templating capabilities can streamline the process and ultimately save time by preventing future security headaches and manual secret management.

## Asssumptions
- This implementation focuses solely on data addition and updates.  Delete operations are not currently supported.
 
## Areas of Improvement

### Docker
Currently, the development process relies on Docker Compose to orchestrate the application's services. This setup requires the application related Docker images to be pre-built and published to Github Packages. This is necessary due to the complexities involved in building the images directly, which stem from:
1. Third-party Python dependencies: The application relies on external Python libraries that need to access libraries present on the host machine. This creates challenges in packaging these dependencies within the Docker image.
2. Build environment restrictions: The current build process is limited to Linux hosts with the same CPU architecture as the host machine. This limits the flexibility and portability of the build process.
To improve this process, we should explore building the Docker images directly within the CI/CD pipeline using a Linux-based Docker container in rules_oci. This approach offers several benefits:
1. Platform independence: Building within a container removes the dependency on the host machine's operating system and architecture, allowing for consistent builds across different environments.
2. Simplified dependency management: Building within a container can help manage the complex third-party Python dependencies more effectively.

This investigation can leverage the following resources:
1. Existing discussions and issues related to rules_oci and cross-compilation on GitHub and Bazel Slack channels.
   - https://github.com/aspect-build/bazel-examples/issues/351
   - https://bazelbuild.slack.com/archives/C04281DTLH0/p1725588762519239?thread_ts=1725513935.581289&cid=C04281DTLH0
   - https://bazelbuild.slack.com/archives/CA306CEV6/p1655823709083759
2. Tools like rules_pycross and dazel that may simplify cross-compilation and dependency management.
   - https://github.com/jvolkman/rules_pycross
   - https://github.com/nadirizr/dazel

### Testing
Automated workflow testing is currently disabled due to the complexity of setting up and managing access to the minio service. The current setup requires accessing minio via both its hostname (minio) and localhost, which is considered too complex and hacky for a production environment.

### Security
1. API Access: The API is currently open to the public. Implementing proper authentication and authorization mechanisms is a complex task that requires the use of proven and tested systems. This aspect has been deferred to simplify the initial development and proof-of-concept phase.
2. Service-to-Service Communication: Communication between services has minimal access control. This simplification was chosen to reduce the complexity of certificate management and programmatic access control rule creation in this proof-of-concept stagees.
   
## Footnotes

[^1]: [ZIP Code General Demographic Characteristics](https://proximityone.com/zip16dp1.htm)