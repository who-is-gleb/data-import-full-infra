# Quick note:
This is my own custom project that was done by myself. Originally, it was an exercise for one of the interviews, but I decided to add it to my portfolio. Please feel free to ask any questions regarding the code.

# Infrastructure schema: 

![Screen Shot 2022-09-05 at 1 19 06 AM](https://user-images.githubusercontent.com/49573287/188335583-495f8749-a1e9-424f-b0d4-7bd9e9d34fd9.png)
Done with Figma

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

