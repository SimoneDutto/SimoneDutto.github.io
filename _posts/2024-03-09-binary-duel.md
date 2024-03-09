---
layout: post
title: "You don't need a database, a queue, a distributed system: Go is enough."
author: "Simone Dutto"
---
This article is a reminder to me and you all that you probably don't need to make things harder for yourself. 

Reading all these articles about software architectures and scalability has influenced me to think that before shipping an idea we need to have it all figured out.

##  The Scalability Tale

We need to choose a *database*: so, let's start with that. We need to choose a db with a generous free tier, set it up, secure it, check the client API, and debug obscure network thingy (VPC, security group, TLS, etc.).

After that, we need to choose a scalable application deployment: so we need to check the pricing on that, set the scalability metric, check if it works, see the supported runtime, etc.  
At a certain point, we asked ourselves self "Do I need to learn K8?".

Finally, we are gonna write our first character of code, right? No, we need to set up the CI/CD pipeline. So let's start the fight to make it work with a secret key and permission model (I Love IAM).

By the end of this process the magic, the sparkle is lost and the will to ship the thing is gone away.

Been there, done that.

So with this new project: [Binary Duel](https://binary-duel.com/) ← shameless plug, I decided to go with a completely different approach.

## My Current Project
Binary Duel is a simple quiz game to compete with friends, it even has matchmaking, and it is all handled by a single half-CPU Golang Server.  
And I love it.

Incredible features:
- The quiz state machine is full in memory
- The queue system for the matchmaking is in memory
- The questions are stored in a sqlite database
- There is no auth, no login, no SSO, no nothing
- It is deployed on an App Engine from the CLI of my personal PC

## FAQ

### Does it scale?
No.

### What if someone decides to DoS your application?
Well, the attack will work. See the article of the frontend guy who "friendly fired" my backend. [Article](link)

## Numbers for engineers
The backend can handle approximately 100 concurrent games. Since each game is expected to last 1-3 minutes. It means that scalability would become an issue if and when Binary Duel is used by more than 4k people an hour.  
In that case, I promise I will host the infrastructure on a K8 cluster with autoscaling, self-healing, a distributed database, a Redis server and so on.

## Final Thoughts
Let the scalability be a consequence of the success, not something that holds you back.

