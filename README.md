# Cisco DNA Center Bot

DNA Center is a complete management and control platform that simplifies and streamlines network operations. This single, extensible software platform includes integrated tools for NetOps, SecOps, DevOps and IoT connectivity with AI/ML technology integrated throughout. 

#### Benefits

* **Simplify Management.** Operate your local and branch networks over a centralized dashboard.
* **Increase Security.** Translate business intent into zero-trust policies and dynamic segmentation of endpoints based on usage behavior.
* **Lower Costs.** Policy-driven provisioning and guided remediation increase network uptime and reduce time spent managing network operations.
* **Transform your network.** Deploy cloud services and applications that benefit from the intelligent network optimization delivered by Cisco DNA Center.
* **Ensure network and application performance:** AI/ML network insights reduce time spent managing network operations and improve user experience.
* **Facilitate offsite IT teams:** Optimized for remote access, a clean, organized dashboard with single-button workflows makes remote management easy.

Webex Teams Bots gives users access to outside services right from their Webex spaces. Bots help users automate tasks, bring external content into the discussions, and gain efficiencies. Bots come in all different shapes and sizes such as notifiers, controllers, and assists. 

The ability to integrate Cisco DNA Center Platform API's into Webex Bots provides us a powerful way to manage and get insights into whats happing within our network. 

# What are we going to do? 

We are going to create a Webex Bot that uses the DNA Center API's to do the following tasks. 

* List Devices 
* Show Device Details 
* Get Device Configuration 
* Run Commands 
* Get P1 Issues 
* Alerting For Assurance Issues 

# Prerequisites 

If you don't already have a [Webex Teams](https://www.webex.com/team-collaboration.html) account, go ahead and register for one. They are free! 

1. You'll need to start by adding your bot to the Webex Teams website 
    
    [https://developer.webex.com/my-apps](https://developer.webex.com/my-apps)
    
2. Click **Create a New App** 
    
    ![Screen Shot 2021-09-17 at 11 01 15 AM](https://user-images.githubusercontent.com/80418373/133818934-1b084325-8d37-471c-82f6-0e23971794d0.png)
    
3. Click **Create a Bot**
    
    ![Screen Shot 2021-09-17 at 11 02 41 AM](https://user-images.githubusercontent.com/80418373/133819125-0e231885-99b0-4708-b021-28fc2878bd06.png)
    
4. Fill out all the details about your bot. 
    
    ![Screen Shot 2021-09-17 at 11 04 27 AM](https://user-images.githubusercontent.com/80418373/133819329-9f9d1bf4-76ed-4c25-960b-d2d2ef524e61.png)
    
5. Click **Add Bot**

6. On the Congratulations screen, make sure to copy the Bot's Access token, you will need this. 

# Azure Functions 

[Azure Functions](https://azure.microsoft.com/en-us/services/functions/#overview) are serverless functions meant to be short-lived and stateless. They remove the limitations in fully managed way without provisioning more resources, just by coding your workflow definitions. Build and debug locally without additional setup, deploy, and operate at scale in the cloud.   

We are using the HttpRequest and HttpResponse Azure functions for interaction with the Webex Bot. In this BOT we have two was of executing the code. 

Option 1: Use the Azure Functions to run it statless in azure.

Option 2: Use Ngrok and Flask to run it local on your PC/VM.


# Ngrok / Flask 

[ngrok](https://ngrok.com/) makes it easy for you to develop your code with a live bot. Ngrok exposes local servers behind NATs and firewalls to the public internet over secure tunnels. It instantly creates a public HTTPS url for a website running locally on your development machine. Ngrok offloads TLS, so you don't have to worry about your configuration. 

[flask](https://flask.palletsprojects.com/en/2.0.x/) is a web framework that provides you with the tools, libraries and technologies that allow you to build a web application. 
        
# Config File 

Update environmental variables to run against your BOT and DNAC. 

Update local.settings.json to run via Azure Function

    {
      "IsEncrypted": false,
      "Values": {
        "FUNCTIONS_WORKER_RUNTIME": "python",
        "logging_level": "INFO",
        "other_modules_logging_level": "WARNING",
        "WEBEX_TEAMS_ACCESS_TOKEN": "Webex_Access_Token",
        "WEBEX_TEAMS_WEBHOOK_URL": "Webex_BOT_URL",
        "DNA_CENTER_BASE_URL": "https://sandboxdnac.cisco.com:443",
        "DNA_CENTER_USERNAME": "devnetuser",
        "DNA_CENTER_PASSWORD": "Cisco123!",
        "DNA_CENTER_VERIFY": "False",
      }
    }

Update Flask_Config_Env.json to run locally via Flask and Ngrok

    {
      "logging_level": "INFO",
      "other_modules_logging_level": "WARNING",
      "WEBEX_TEAMS_ACCESS_TOKEN": "BOT_ACCESS_TOKEN",
      "WEBEX_TEAMS_WEBHOOK_URL": "BOT_URL",
      "DNA_CENTER_BASE_URL": "https://sandboxdnac.cisco.com:443",
      "DNA_CENTER_USERNAME": "devnetuser",
      "DNA_CENTER_PASSWORD": "Cisco123!",
      "DNA_CENTER_VERIFY": "False"
    }

# Webex Bot Script 

The flask_app.py is leveraging the Flask web service [micro-framework](http://flask.pocoo.org/). We are using ngrok to be used to tunnel traffic back to your local machine sites. Run the flask_app.py to run the bot locally from your machine. When interacting with the Bot, we are calling functions in the HTTPWebexBOT/__init__.py script. You can also have the options to setup your Azure Functions and add your settings to local.settings and run this as an Azure Function. 

Below are the example interactions with the Bot. 

![Screen Shot 2021-10-25 at 12 41 08 PM](https://user-images.githubusercontent.com/80418373/138743926-773c5802-9cb6-4e6a-bfa3-5249343b92a7.png)

![Screen Shot 2021-10-25 at 12 42 01 PM](https://user-images.githubusercontent.com/80418373/138744062-85485d11-f26c-4c92-a1a5-a11b1ed78865.png)

![Screen Shot 2021-10-25 at 12 42 47 PM](https://user-images.githubusercontent.com/80418373/138744158-cf43d5d8-e94d-4d78-9b3b-bb9713aba14a.png)


# Cisco DNA Center Real Time Event Alerts to Webex Teams Bot 

Cisco DNA Center has a powerful issue correlation engine for wired and wireless networks. Real time feeds of network telemetry is able to identify issues and provide context for resolution. We now have the ability to send those notifications to a Webex Team Rooms in 2.2.3.0 release. 

1.) In Cisco DNA Center navigate to Platform -> Developer Toolkit and the Events Tab.

![Screen Shot 2021-09-20 at 2 55 19 PM](https://user-images.githubusercontent.com/80418373/134066574-61efac9b-fbda-4f51-a5a8-ed001d69fffe.png)

2.) Select the events you want to be notified about to your Webex Teams Room then click "Subscribe". 

3.) Create a Name for the subscription then select Webex for the Subscription Type.  

![Screen Shot 2021-09-20 at 2 57 27 PM](https://user-images.githubusercontent.com/80418373/134066822-27516f03-364c-479a-bd34-11ed13266167.png)

4.) Enter the Webex URL along with the Webex Room ID where you want the alerts to be posted and your Webex Access Bot Token. (You can find your webex room id's at [developer.webex.com](https://developer.webex.com/docs/api/v1/rooms/get-room-meeting-details))

![Screen Shot 2021-09-20 at 3 01 57 PM](https://user-images.githubusercontent.com/80418373/134067388-9e484b6b-55f8-4382-bb36-3f24099df4d6.png)

![Screen Shot 2021-09-20 at 3 01 06 PM](https://user-images.githubusercontent.com/80418373/134067277-7414dac6-9360-4726-ad7d-7626b803b50a.png)

5.) You can now test your integration by selecting "Try it" 

![Screen Shot 2021-09-20 at 3 03 34 PM](https://user-images.githubusercontent.com/80418373/134067606-b322bee0-a765-4578-abfe-73d69e5cd247.png)

6.) If you setup everything correctly you will see the notification in your Cisco Webex Team Room. 

![Screen Shot 2021-09-20 at 3 04 06 PM](https://user-images.githubusercontent.com/80418373/134067679-1caac760-b9ae-41e8-acca-ddfd7b62391e.png)

# Links to DevNet Learning Labs

Here is a link to the Cisco DNA Center Devnet Learning Lab to learn how to leverage the Cisco DNA Center API's.

[Introduction to Cisco DNA Center REST APIs](https://developer.cisco.com/learning/modules/dnac-rest-apis)

# License

This project is licensed to you under the terms of the [Cisco Sample Code License.](https://github.com/brfriedr/DNAC_Better_Together/blob/master/LICENSE)