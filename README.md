# Cisco DNA Center Bot

DNA Center is a complete management and control platform that simplifies and streamlines network operations. This single, extensible software platform includes integrated tools for NetOps, SecOps, DevOps and IoT connectivity with AI/ML technology integrated throughout.

### Benefits

* **Simplify Management:** Operate your local and branch networks over a centralized dashboard.
* **Increase Security:** Translate business intent into zero-trust policies and dynamic segmentation of endpoints based on usage behavior.
* **Lower Costs:** Policy-driven provisioning and guided remediation increase network uptime and reduce time spent managing network operations.
* **Transform your network:** Deploy cloud services and applications that benefit from the intelligent network optimization delivered by Cisco DNA Center.
* **Ensure network and application performance:** AI/ML network insights reduce time spent managing network operations and improve user experience.
* **Facilitate offsite IT teams:** Optimized for remote access, a clean, organized dashboard with single-button workflows makes remote management easy.

Webex Teams Bots give users access to outside services right from their Webex spaces. Bots help users automate tasks, bring external content into the discussions, and gain efficiencies. Bots come in different shapes and sizes such as notifiers, controllers, and assistants.

The ability to integrate Cisco DNA Center Platform API's into Webex Bots provides us a powerful way to manage and get insights into whats happing within our network.

# What are we going to do?

We are going to create 2 different Webex Bots that use the DNA Center APIs.

### Admin Mode:
This mode is intended for network admins to interact with network devices and accomplish the following tasks:
  * List Devices
  * Show Device Details
  * Get Device Configuration
  * Run Commands
  * Get P1 Issues

### User Mode:
This mode is intended for end users within the company to chat with the bot and gain an understanding of their network state without making a call to the helpdesk.

  * List devices authenticated with the Webex user's email
  * Show the device health, status, and issues for each device
  * Open a helpdesk ticket for a device (psuedo code - add your own code for your ticketing system API)

# Prerequisites

If you don't already have a [Webex Teams](https://www.webex.com/team-collaboration.html) account, go ahead and register for one. They are free!

1. You'll need to start by adding your bot to the Webex Teams website

    [https://developer.webex.com/my-apps](https://developer.webex.com/my-apps)

2. Click **Create a New App**

    ![image](https://user-images.githubusercontent.com/57721193/153505468-f3fd294f-8092-455b-bf3e-b2ae697c2a08.png)

3. Click **Create a Bot**

    ![image](https://user-images.githubusercontent.com/57721193/153505687-5838f4cd-d1b4-4f8d-9920-39c830a4fc7b.png)

4. Fill out all the details about your bot.

    ![image](https://user-images.githubusercontent.com/57721193/153505852-faeb09c2-a0a3-474e-aaa2-ef877b1cdf3b.png)

5. Click **Add Bot**

6. ### **On the Congratulations screen, make sure to copy the Bot's Access token, you will need this!!**

# Azure Functions

[Azure Functions](https://azure.microsoft.com/en-us/services/functions/#overview) are serverless functions meant to be short-lived and stateless. They remove the limitations of a fully managed server without provisioning more resources, just by coding your workflow definitions. Build and debug locally without additional setup, deploy, and operate at scale in the cloud.

We are using an HttpTrigger Azure function for interaction with the Webex Bot. We have two ways of running this code:

* Option 1: Use Ngrok and Flask to run it local on your PC/VM (recommended for learning/testing).

* Option 2: Deploy the app to Azure Functions and run it in the Azure cloud.

# Ngrok / Flask

[ngrok](https://ngrok.com/) makes it easy for you to develop your code with a live bot. Ngrok exposes local servers behind NATs and firewalls to the public internet over secure tunnels. It instantly creates a public HTTPS url for a website running locally on your development machine. Ngrok offloads TLS, so you don't have to worry about your configuration.

[flask](https://flask.palletsprojects.com/en/2.0.x/) is a web framework that provides you with the tools, libraries and technologies that allow you to build a web application.

# Config File

Rename (or make a copy) the "local.settings_template.json" file to "local.settings.json".

This file is in the Azure Functions format, but will be parsed and used for Ngrok/Flask as well.  Change the settings to reflect your environment.

    {
      "IsEncrypted": false,
      "Values": {
        "logging_level": "INFO",
        "other_modules_logging_level": "WARNING",
        "WEBEX_TEAMS_ACCESS_TOKEN": "ACCESS-TOKEN",
        "WEBEX_TEAMS_WEBHOOK_URL": "Azure URL or Flask/Ngrok endpoint (this should have the /webexbot route at the end)",
        "WEBEX_ALLOWED_DOMAINS": "yourdomain.com (comma separated list of domains to allow, leave empty/blank to allow all)",
        "DNA_CENTER_BASE_URL": "https://ip_address:443",
        "DNA_CENTER_USERNAME": "admin_username",
        "DNA_CENTER_PASSWORD": "admin_password",
        "DNA_CENTER_VERIFY": "False",
        "ADMIN_OR_USER_MODE": "admin"
      }
    }

Note: The "ADMIN_OR_USER_MODE" setting can be set to "admin" or "user" depending on which mode we want.

# Webex Bot Script

The flask_app.py is leveraging the Flask web service [micro-framework](http://flask.pocoo.org/). We are using ngrok to be used to tunnel traffic back to your local machine sites. Run the flask_app.py to run the bot locally from your machine. When interacting with the Bot, we are calling functions in the HTTPWebexBot\\__init__.py script. You can also have the option to install and setup the Azure Functions tools and run this as an Azure Function locally.

Execute the flask_app.py script to start the bot locally.  Make sure you install the necessary Python modules in the requirements.txt file (pip install -r requirements.txt).  **This code was developed using Python 3.9**

# Admin Mode Bot Interaction
Below are some example interactions with the Admin Bot.

![image](https://user-images.githubusercontent.com/57721193/153507499-8202d70b-81d5-4f5a-a1ed-6a3ad64332b7.png)

![image](https://user-images.githubusercontent.com/57721193/153507669-5d4efc11-192c-4c8a-b39b-cfc196adffaa.png)

![image](https://user-images.githubusercontent.com/57721193/153507747-2c036dc7-e78a-4f1c-a6d9-0c0cdc1e046c.png)

![image](https://user-images.githubusercontent.com/57721193/153507837-00ba2b87-d33f-4ff8-9d49-5b76eae046f3.png)

![image](https://user-images.githubusercontent.com/57721193/153507882-ac6b2bfa-a412-4f73-a39a-9ac46eb78bf0.png)

![image](https://user-images.githubusercontent.com/57721193/153507941-978500ad-3e40-466f-8dab-f8f714c30b91.png)

# User Mode Bot Interaction
Below are some example interactions with the Admin Bot.

![image](https://user-images.githubusercontent.com/57721193/153508057-cec94968-332e-4427-95c5-25da94f437ef.png)

![image](https://user-images.githubusercontent.com/57721193/153508137-69ef961d-d78a-4164-baa0-3060dba74c3f.png)

![image](https://user-images.githubusercontent.com/57721193/153508175-c57d24a5-61af-4aaa-b07e-ad7c72f283cb.png)

# Links to DevNet Learning Labs

Here is a link to the Cisco DNA Center Devnet Learning Lab to learn how to leverage the Cisco DNA Center API's.

[Introduction to Cisco DNA Center REST APIs](https://developer.cisco.com/learning/modules/dnac-rest-apis)

# License

This project is licensed to you under the terms of the [Cisco Sample Code License.](https://github.com/cisco-code-projects/DNAC-Webex-Chatbot/blob/main/LICENSE)
