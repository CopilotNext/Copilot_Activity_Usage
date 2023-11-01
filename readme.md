# Copilot_Activity_Usage_Report

quick report for Github Copilot for business usage in organizations.

It is a quick usage report of copilot for busienss within Github Organizations.
Since there is API to get the latest activity, like 'https://api.github.com/orgs/{org}/copilot/billing/seats?per_page=200'
    
By calling the API periodlly- it is 6 hours by default in hard code in refresh_orgs_job.py now. 
We save the return as .csv, then extract it by dropping dupliate/split the IDE column to more column. finally, generate report. it supports daily active users analysis/Non Active users/Used by IDE/Used by Copilot Features/Develper who used copilot most often.
And More report will be generated based on feedback, thanks.

## Features

- support multi-organizaiton management, inlucing add/remove organization for this tool.
- This is a Flask web application that displays seat usage data for different organizations. 
The app reads organization names from a CSV file and displays them on the homepage. 
Users can select an organization and view seat usage reports and charts. 
The app also has a configuration page where new organizations can be added. 
The app runs a background thread that periodically fetches the latest seat usage data from an API.


## Installation
- Run Locally
    - pip install -r requirements.txt
    - open app.py, run it
    - then visit http://localhost:5000, select config to add your organizations.
 - Run in Docker
    - docker build -t copilot-usage-report .
    - docker run -d -p 5000:5000 copilot-usage-report
    - then visit http://localhost:5000, select config to add your organizations.
 - Run in Azure (both Rerpot and sync-refresh job)
    - docker build -t copilot-usage-report .
    - docker build -t copilot-usage-job -f Dockerfile-job .
    - docker tag copilot-usage-report <your-registry-name>.azurecr.io/copilot-usage-report:v1
    - docker tag copilot-usage-job <your-registry-name>.azurecr.io/copilot-usage-job:v1
    - docker push <your-registry-name>.azurecr.io/copilot-usage-report:v1
    - docker push <your-registry-name>.azurecr.io/copilot-usage-job:v1

    - deploy copilot-usage-report and copilot-usage-job to Azure App Service/Container Apps.
    - config the App Service/Container Apps to use Azure File Share for /data and /static folder, so that the data can be shared between App Service and Container Apps. Form More,please visit:https://docs.microsoft.com/en-us/azure/app-service/configure-connect-to-azure-storage?pivots=container-linux#mount-file-share; and https://learn.microsoft.com/en-us/azure/container-apps/storage-mounts?pivots=azure-portal
    - add a orgs.csv file to Azure File Share, and add the orgs you want to monitor.
## Usage

- Provide instructions for using your project.
- 
![alt text](static/active_users_byday.png "Activy report by Day")

![alt text](static/main.png "Main (Index) Page")

![alt text](static/config-orgs.png "Config (Add/Remove) Orgs")

![alt text](static/Copilot-Feature_Bar.png "Copilot-Feature_Bar")


## Examples

- Provide examples of how to use your project.
- To check more report locally, please access http://localhost:5000/active_report
- To check more report, please access https://copilot-usage-report.azurewebsites.net/



## API Reference

- If your project includes an API, provide documentation for the API here.
-  https://api.github.com/orgs/{org}/copilot/billing/seats?per_page=200

## Contributing

- Provide guidelines for contributing to your project.

## License

- Provide information about the license for your project.

## Authors

- [DevOps_Zhuang](https://github.com/DevOps-zhuang)
- [Daniel Wang](https://github.com/nikawang)
- [JumpStarX](https://github.com/JumpXStar)

## Acknowledgments

- Thank any contributors or open source projects that your project depends on.