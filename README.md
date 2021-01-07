# Deep Watermarker Flask backend

This project holds all of the api backends for the deep vidio watermarker

## Docker

made up of jgalante97/deep-vidio-service-web, jgalante97/deep-vidio-service-worker, and redis

Build all docker containers:
```
docker-compose build
```

Run via docker:
```
Docker-compose up
```

## Elastic Beanstalk

Initialize eb:
```
eb init
```

Build all docker containers:
```
docker-compose build
```

Run via eb:
```
eb local run
```

SSH init docker containers:
```
eb ssh DeepVidioService
cd /var/app/current/
```

## Useful links
https://testdriven.io/blog/asynchronous-tasks-with-flask-and-redis-queue/

https://testdriven.io/blog/asynchronous-tasks-with-flask-and-redis-queue/ 

## Deployed with Travis ci

https://travis-ci.com/github/Galante97/VidioService

Every push to github will redeploy the application to docker and aws:
```
git add .
git commit -m ""
git push -u origin master
```