Load-Balancing-Distributed-Server
===
Course project in Intro. to Network Programming, Fall'18

# Goal
- Deploy social media servers according to number of logged-in users dynamically with AWS EC2 instances

# Methods
- Local version client `client.py` and server `server.py` without load balancing function has been implemented in previous homeworks
- `login_server.py` is responsible for acception and running up a new EC2 instance in `Launch_AS()` if number of users increase or shutting down extra instances if users decrease.
- Dynamic load balancing control is fulfilled by **Amazon Simple Systems Manager (SSM)** in AWS Python SDK `boto3`
- Clients and servers communicate using **ActiveMQ** server with **STOMP** protocol

# Other projects related to network programming
- [Project 1 - NPShell](https://github.com/yhyeh/NP_Project1)
- [Project 2 - Remote Working Ground (RWG) Server](https://github.com/yhyeh/NP_Project2)
- [Project 3 - Remote Batch System](https://github.com/yhyeh/NP_Project3)
- [Project 4 - SOCKS 4 Server](https://github.com/yhyeh/NP_Project4)
