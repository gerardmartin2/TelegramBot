## AP2 Poject: iGo 

## Description
The project consists in the creation of a telegram bot that helps users in Barcelona to get to their destination by car using the shortest path. This path is found taking into account the itime concept, which is based on traffic congestion of streets in real time.

The project is divided in two main parts:
- igo: Contains the required functions to get the information about the Barcelona graph, its streets and its congestions in order to compute the shortest path between two locations.
- bot: Allows a user to interact with a telegram bot and, among other funcionalities, helps the user to get the shortest path by car to a destination using the igo module.

## Visuals
![](<https://i.ibb.co/3m2DsFw/mapa.png">)
Example of a shortest route between Camp Nou and Campus Nord found with the igo module and provided by the bot. 


## Installation
To install the needed packages run the following command in your terminal:
```sh
pip install -r requirements.txt
```
This file is provided in the project zip folder and contains all the references to the packages needed to install them. 

## Usage

##### iGo
iGo module allows to download real time information about the streets of Barcelona and to compute the shortest path between two locations using the itime concept.

iGo has the necessary functions to:
 - Download and store data: Graph of Barcelona (from OSMNX Package) and the information of highways and its congestions (from [ajuntament de Barcelona](opendata-ajuntament.barcelona.cat))
 - Plot images: Plot Barcelona's Graph, streets of Barcelona, its congestions levels (detailed by colour) 
 - Create iGraph: A new graph version which adds itime as an edge attribute. The itime concept takes into account the real time congestions of the streets.
 - Compute shortest paths: Using the attribute time, is able to find and plot the shortest route between two locations.
##### Bot
The telegram bot can be found by searching its name on telegram : @iGoAP2_bot
The bot can be activated by writting in the chat this line:
```sh
/start
```
Besides, it has a support command that provides information about its usage and all the available functions that it have, the command:
```sh
/help
```
Its main functionality is plotting the shortest path from the users location to the desired destination. For instance, if the user wants to go to Badal, he would write the following line:
```sh
/go Badal
```
The bot would provide a picture with the best route. If, for example, the user is in Barceloneta, the bot will return the following image:
![](https://i.ibb.co/SnbgV4y/Screenshot-20210530-184115.png)

Other available commands are:
```sh
/pos Place  Fix the user location in a false provided Place
/where      Plots a map with the position of the user
/author     Gives information about the authors
```
## Contributing
We are open to any contribution that aims to improve the project. Please contact:
adria.dieguez@estudiantat.upc.edu
gerard.martin.pey@estudiantat.upc.edu

## Support
If you have any doubt about the bot's usage or any other related with the project contact the already mentioned mails. 

## Authors
Adrià Dièguez Moscardó
Gerard Martin Pey