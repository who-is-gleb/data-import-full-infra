# Source code for the project

This is a project for Altenar's interview exercise

# Infrastructure schema: 

![Screen Shot 2022-09-05 at 1 19 06 AM](https://user-images.githubusercontent.com/49573287/188335583-495f8749-a1e9-424f-b0d4-7bd9e9d34fd9.png)
Done with Figma

# Important notes from me:

_What was achieved:_
- Airflow was configured and used to extract data daily.
- Clickhouse (CH) was configured as the data warehouse.
- Grafana was used as a real-time dashboard.
- They all work with each other successfully.
- Daily fetching works properly.
- Point 2 is visualized in Grafana.
- Other metrics are delivered as views in CH (4 views for all 4 metrics except number 4).
- Metric 4 could not be calculated because the archive does not have any info about gender.
- Few minor tests that can be run locally. They are by no means comprehensive, but they give a basis for further enhancements.
- Different docker-compose files for different deployment environments. They might lack some detailed precise configurations, but they serve their purpose of varying configs for varying environments.

# _Additional questions:_

Number 2. If the archive grows significantly, in order for us to evolve in terms of architecture, we would need to do the following (in the order of simplicity):
  - Use more generators then simple returns
  - Stop using XCom and start saving data to the filesystem directly, and share paths to data between tasks
  - Write a cleanup DAG for metadata database to save memory/disk space
  - Increase the number of and tune the Airflow workers (add more workers, reduce parallelism, increase timeouts, etc)
  - Connect Airflow to EFS (for example) and use that as the filesystem to have more storage scalability for Airflow metadata/data
  - Deploy Airflow to Kubernetes as cluster to have multiple nodes to gain more computing power and high availability

Number 3. The third question refers to the distributed systems topic. Basically, any distributed system should utilize high availability and have as minimal idle time as possible. That can be achieved by using an architecture that has 1 master node and multiple replicas. The process of leader election should be implemented as well. Leader becomes a master node that is responsible for processing requests, while the replicas serve as "computing" power. Whenever a leader fails, replicas should detect that quickly and elect a new leader. After that, the should syncronize and continue working with a new leader. <br>
_As for Airflow in particular_, scaling Airflow can have few options:
First, increase the number of worker nodes. A cluster could have multiple worker nodes to have more computing resources.
Second, increase the number of master nodes (web-server nodes). This can come in handy when there are a lot of requests that a web-server should process.
There can only be one scheduler, though. As well as single metastore that all workers, servers and a scheduler would access.

# How to start everything up, run, fetch the archive and so on:

1. Create python virtual env and run `install-deps.sh` to install all libs and modules locally (for testing as an example)
2. Install Docker and Docker Compose (I use DockerDesktop). Configure appropriate resources (6 CPUs and 8GB memory was not enough for me)
3. Run `docker-compose -f docker-compose.<desired_environment>.yaml up` to run the application, `docker-compose -f docker-compose.<desired_environment>.yaml down` to shut it down
4. Navigate to *localhost:8080*, login by *airflow/airflow*, then turn both DAGs on (they will execute in the right order by themselves)
5. Access Clickhouse if you want to. Either by navigating to *http://localhost:8123/play* or via Datagrip (*localhost:8123*, empty user/password for dev/stage). Clickhouse would have a "raw" data table and few views that calculate metrics
6. Access Grafana by navigating to *localhost:3000/*. Use admin/admin for prod. Not needed for dev/stage. Use this guide to create a connection to our Clickhouse DB: _https://clickhouse.com/docs/en/connect-a-ui/grafana-and-clickhouse/_. Create a dashboard with the following query:
`select count(actor_id) as dev_number, events_date from github_data.devs_less_than_one_commit_daily
group by events_date` to see Point 2 metric in real-time
7. Other exercise metrics are available as views in Clickhouse

