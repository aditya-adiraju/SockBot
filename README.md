# SockBot
## An interactive Discord Bot for UBC A Cappella's Annual Sock Wars written with PyCord and SQLite3

### What is Sock(appella) Wars?
Sockappella wars is an assassin-based game played around the city where participants attempt to "sock" *(gently tap with a clean sock)* their targets and eliminate them from the game. The last person standing wins. 

Throughout the game period, a variety of "safety items" are introduced ranging from moving around with two different shoes to dancing the "Macarena". When a player is in possession of a safety item, they cannot be socked. 

When you eliminate your target, you are reassigned to your target's target.

The game ends after a period of 4 weeks. 

To see more rules: read [rules](./rules.md)

### Technical Implementation
The main tech stack can be broken down into the following categories:

- **Development**: 
    - [*PyCord*](https://pycord.dev/): A library to interact with the discord API to create bot commands. 
    - [*SQLite3*](https://www.sqlite.org/): The database storage option of choice for this project. It holds information regarding the game state such as the Player information, their targets, and a log of all eliminations.
- **CI/CD**:
    - [*Google Cloud*](https://cloud.google.com/): Cloud Provider of choice. The project leverages its artifact registry and compute instances to deploy the bot 24/7. 
    - [*Docker & Docker Compose*](https://www.docker.com/): Used a containerized workflow to create portable bot images. 
    - [*Github Actions*](https://github.com/features/actions): CI/CD framework to automatically build, push and deploy a docker image to a GCloud CE Instance.

### Fun Stuff
- **Efficient Data Recovery (Point In Time restore):** Designed and implement an efficient method to rollback game eliminations, and assigned targets to any point in time (dictated by an elimination ID).
- **Statiscal views**: Created several database views to effectively display table information.



### Get Started

To get started developing locally simply run 
```sh
$ docker build . -t sockbot:latest
$ docker run sockbot:latest
```

