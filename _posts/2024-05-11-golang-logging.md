---
layout: post
title: "How can logging impact a Golang webserver?"
author: "Simone Dutto"
---

This article is the answer to a small question I have always asked myself developing a webserver.
How much logging impact the performance? Is there a good reason why we keep the logging level to ERROR in production?

_Short Answer: very much YES._

# Analysis


## Backend Setup
Since I was already playing with my Golang backend for my hobby project [binary-duel](https://binary-duel.com/). 

I decided to add a simple route with two configurable parameters:
- number of logs
- number of characters in each log

In my webserver I have used https://github.com/sirupsen/logrus as the logging library.

```go
func Logging(c *gin.Context) {
	var json struct {
		NumLogs int
		Size    int
	}
	if err := c.ShouldBindJSON(&json); err != nil {
		c.JSON(http.StatusBadRequest, gin.H{"error": err.Error()})
		return
	}
	for i := 0; i < json.NumLogs; i++ {
		logString := randStringRunes(json.Size) // generate a random string of fixed size
		utils.Log.Debug(logString) // utils function to log, using logrus
	}
	c.Status(http.StatusOK)
}
```

## Load Test setup

I used https://www.npmjs.com/package/autocannon to load test this route with different (number of logs, size) combination, and finally extract metrics. The idea is to send as much requests as possible in 10 seconds.

Here is the configuration.
```js
const autocannon = require('autocannon')

const instance = autocannon({
    url: 'http://ubuntucore:8080/logging',
    method: 'POST',
    headers: {
        'Content-Type': 'application/json'
    },
    body: JSON.stringify({
        "NumLogs": "<num>",
        "Size": "<size>"
    }),
    connections: 10, 
    pipelining: 1,
    duration: 10, // seconds
}, console.log)

// this is used to kill the instance on CTRL-C
process.once('SIGINT', () => {
    instance.stop()
})

// just render results
autocannon.track(instance, { renderProgressBar: true })
```

## Hardware Setup
The WebServer is deployed into a Raspberry 2 Model B in my local network, and the load test is run using my PC.

# Results

## 0 Logs per Request

_Latency_
| Stat    | 2.5% | 50%  | 97.5% | 99%  | Avg      | Stdev  | Max   |
|---------|------|------|-------|------|----------|--------|-------|
| Latency | 6 ms | 13 ms| 29 ms | 35 ms| 14.49 ms | 9.12 ms| 188 ms|

_Req/s_
| Stat     | 1%   | 2.5% | 50%   | 97.5% | Avg    | Stdev  | Min   |
|----------|------|------|-------|-------|--------|--------|-------|
| Req/Sec  | 586  | 586  | 662   | 723   | 666.6  | 44.01  | 586   |
| Bytes/Sec| 44 kB| 44 kB| 49.7 kB| 54.2 kB| 50 kB  | 3.3 kB | 44 kB |


# 5 Logs of 20 characters per Request
_Latency_
| Stat    | 2.5% | 50%   | 97.5% | 99%   | Avg      | Stdev    | Max    |
|---------|------|-------|-------|-------|----------|----------|--------|
| Latency | 8 ms | 24 ms | 47 ms | 59 ms | 25.01 ms | 11.13 ms | 107 ms |

_Req/s_
| Stat      | 1%      | 2.5%     | 50%     | 97.5%   | Avg     | Stdev   | Min     |
|-----------|---------|----------|---------|---------|---------|---------|---------|
| Req/Sec   | 334     | 334      | 392     | 435     | 391.7   | 30.84   | 334     |
| Bytes/Sec | 25.1 kB | 25.1 kB  | 29.4 kB | 32.6 kB | 29.4 kB | 2.31 kB | 25.1 kB |


# 5 Logs of 100 characters per Request
_Latency_
| Stat    | 2.5%  | 50%   | 97.5% | 99%   | Avg      | Stdev    | Max    |
|---------|-------|-------|-------|-------|----------|----------|--------|
| Latency | 10 ms | 30 ms | 59 ms | 70 ms | 31.54 ms | 13.62 ms | 142 ms |

_Req/s_
| Stat      | 1%      | 2.5%    | 50%     | 97.5%   | Avg     | Stdev   | Min     |
|-----------|---------|---------|---------|---------|---------|---------|---------|
| Req/Sec   | 251     | 251     | 304     | 351     | 311.61  | 30.41   | 251     |
| Bytes/Sec | 18.8 kB | 18.8 kB | 22.8 kB | 26.3 kB | 23.4 kB | 2.28 kB | 18.8 kB |

# 20 Logs of 5 characters per Request
_Latency_
| Stat    | 2.5%  | 50%   | 97.5% | 99%   | Avg      | Stdev    | Max    |
|---------|-------|-------|-------|-------|----------|----------|--------|
| Latency | 20 ms | 58 ms | 130 ms| 142 ms| 62.09 ms | 26.08 ms | 182 ms |

_Req/s_
| Stat      | 1%      | 2.5%    | 50%     | 97.5%   | Avg     | Stdev   | Min     |
|-----------|---------|---------|---------|---------|---------|---------|---------|
| Req/Sec   | 111     | 111     | 166     | 202     | 159.31  | 28.4    | 111     |
| Bytes/Sec | 8.33 kB | 8.33 kB | 12.5 kB | 15.2 kB | 11.9 kB | 2.13 kB | 8.32 kB |


# Conclusion
The results are conclusive:
- logs can impact the performance of your backend
- log the less you can!
- it is way better to log a long message instead of logging multiple small messages


---

Do you have any ideas or comments? 

Leave them under this HK post or email me via _simonedutto8+binaryduel_at_gmail.com_

If you are interested in other articles: read [You don't need a database, a queue, a distributed system: Go is enough.](https://simonedutto.github.io/2024-03-09/binary-duel)