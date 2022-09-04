# Source code for the project

This is a project for Altenar's interview exercise

# Infrastructure schema: 

![Screen Shot 2022-09-05 at 1 19 06 AM](https://user-images.githubusercontent.com/49573287/188335583-495f8749-a1e9-424f-b0d4-7bd9e9d34fd9.png)
Done with Figma

# Important notes from me:

_What was achieved successfully:_
- Airflow was configured and used to extract data daily.
- Clickhouse (CH) was configured as the data warehouse.
- Grafana was used as a real-time dashboard.
- They all work with each other successfully.
- Point 2 is visualized in Grafana.
- Other exercise points are delivered as views in CH.
- Daily fetching works properly.

_What was not fully achieved and why:_
- I was not able to fully implement the "Environments" section. However, hypothetically, in order to do that I would need to configure various docker-compose files and environments. For example, for prod env I would need to configure security and authorization more strictly. Give proper authorization to CH instance. And so on.

_Additional questions:_
2. If the archive grows significantly, in order for us to evolve in terms of architecture, we would need to do the following (in the order of simplicity):
  - Use more generators then simple returns
  - Stop using XCom and start saving data to the filesystem directly, and share paths to data between tasks
  - Write a cleanup DAG for metadata database to save memory/disk space
  - Increase the number of and tune the Airflow workers (add more workers, reduce parallelism, increase timeouts, etc)
  - Deploy Airflow to Kubernetes as cluster to gain more computing power
  - Connect Airflow to EFS (for example) and use that as the filesystem to have more storage scalability for Airflow metadata/data
3. I personally think the third question is about distributed systems topic. Basically, any distributed system should utilize high availability and have as minimal idle time as possible. That can be achieved by using an architecture that has 1 master node and multiple replicas. The process of leader election should be implemented as well. Leader becomes a master node that is responsible for processing requests, while the replicas serve as "computing" power. Whenever a leader fails, replicas should detect that quickly and elect a new leader. After that, the should syncronize and continue working with a new leader. I can discuss this question in more details if needed.

# How to start everything up, run, fetch the archive and so on:

1. Create python virtual env and run `install-deps.sh` to install all libs and modules locally (for testing as an example)
2. Install Docker and Docker Compose (I use DockerDesktop). Configure appropriate resources (6 CPUs and 8GB memory was not enough for me)
3. Run `docker-compose up airflow-init` (not necessary but I do this anyway)
4. Run `docker-compose up`
5. Navigate to *localhost:8080*, login by *airflow/airflow*, then turn both DAGs on (they will execute in the right order by themselves)
6. Access Clickhouse if you want to. Either by navigating to *http://localhost:8123/play* or via Datagrip (*localhost:8123*, empty user/password). Clickhouse would have a "raw" data table and few views that calculate metrics.
7. Access Grafana by navigating to *localhost:3000/*. Use admin/admin. Use this guide to create a connection to our Clickhouse DB: _https://clickhouse.com/docs/en/connect-a-ui/grafana-and-clickhouse/_. Create a dashboard with the following query:
`select count(actor_id) as dev_number, events_date from github_data.devs_less_than_one_commit_daily
group by events_date` to see Point 2 metric in real-time.
8. Other exercise points are available as views in Clickhouse.

