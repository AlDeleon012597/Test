# Social Vulnerability Index Web App
Web Application for SVI using Dash.

Dash Docs:https://dash.plot.ly/  
Flask Docs: https://flask.palletsprojects.com/en/1.1.x/  
Adding CSS & JS and Overriding the Page-Load Template: https://dash.plot.ly/external-resources  

Development Version:https://dev1-hazard-vulnerability.herokuapp.com/   
Production Version: https://svi-dash-app.herokuapp.com/   

## Development
Instructions for developers and contributors to this project. 

### Set-up

Create a local development environment using conda or virtualenv from the requirements.txt file. 

For Conda:

where <env_name> is the name of your virtual environment.

`conda create --name <env_name> ` 

Activate your new environment

`conda activate <env_name>`

Install pip to manage python specific requirements (important for Heroku deployment)

`conda install pip`

Install requirements.txt dependencies
` pip install -r requirements.txt`

### Project Directory Structure
<pending>

### Repository Procedures 
The Master branch represents the current production version of the app and is protected.
All code is pulled into the current Development branch. Branches should represent specific features and issues.  
Open a branch to work on new features or issues. If an issue does not exist for the feature then create the issue and then assign it to yourself. This will ensure issues can be attached to branches and be closed during pull requests. 
 
 
