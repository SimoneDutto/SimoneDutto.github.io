---
layout: post
title: "How can logging impact a Golang backend?"
author: "Simone Dutto"
---

This article is the answer to a small question I have always asked myself developing a backend.
How much logging impact the performance? Is there a good reason why we keep the logging level to ERROR in production?

_Short Answer: very much YES._

# Analysis


## Backend Setup
Since I was already playing with my Golang backend for my hobby project [binary-duel](https://binary-duel.com/). 

I decided to add a simple route with two configurable parameters:
- number of logs
- number of characters in each log

In my backend I have used <https://github.com/sirupsen/logrus> as the logging library.

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

I used <https://www.npmjs.com/package/autocannon> to load test this route with different (number of logs, size) combination, and finally extract metrics. The idea is to send as many requests as possible in 10 seconds.

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
The backend is deployed into a Raspberry 2 Model B in my local network, and the load test is run using my PC.

# Results

## 0 Logs per Request

_Latency_


<table style="border: 1px solid black">
  <thead style="border-bottom: 1px solid black">
    <tr>
      <th style="border-right: 1px solid black">Stat</th>
      <th style="border-right: 1px solid black">2.5%</th>
      <th style="border-right: 1px solid black">50%</th>
      <th style="border-right: 1px solid black">97.5%</th>
      <th style="border-right: 1px solid black">99%</th>
      <th style="border-right: 1px solid black">Avg</th>
      <th style="border-right: 1px solid black">Stdev</th>
      <th>Max</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <td style="border-right: 1px solid black">Latency</td>
      <td style="border-right: 1px solid black">6 ms</td>
      <td style="border-right: 1px solid black">13 ms</td>
      <td style="border-right: 1px solid black">29 ms</td>
      <td style="border-right: 1px solid black">35 ms</td>
      <td style="border-right: 1px solid black">14.49 ms</td>
      <td style="border-right: 1px solid black">9.12 ms</td>
      <td>188 ms</td>
    </tr>
  </tbody>
</table>

_Req/s_


<table style="border: 1px solid black">
  <thead style="border-bottom: 1px solid black">
    <tr>
      <th style="border-right: 1px solid black">Stat</th>
      <th style="border-right: 1px solid black">1%</th>
      <th style="border-right: 1px solid black">2.5%</th>
      <th style="border-right: 1px solid black">50%</th>
      <th style="border-right: 1px solid black">97.5%</th>
      <th style="border-right: 1px solid black">Avg</th>
      <th style="border-right: 1px solid black">Stdev</th>
      <th>Min</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <td style="border-right: 1px solid black">Req/Sec</td>
      <td style="border-right: 1px solid black">586</td>
      <td style="border-right: 1px solid black">586</td>
      <td style="border-right: 1px solid black">662</td>
      <td style="border-right: 1px solid black">723</td>
      <td style="border-right: 1px solid black">666.6</td>
      <td style="border-right: 1px solid black">44.01</td>
      <td>586</td>
    </tr>
    <tr>
      <td style="border-right: 1px solid black">Bytes/Sec</td>
      <td style="border-right: 1px solid black">44 kB</td>
      <td style="border-right: 1px solid black">44 kB</td>
      <td style="border-right: 1px solid black">49.7 kB</td>
      <td style="border-right: 1px solid black">54.2 kB</td>
      <td style="border-right: 1px solid black">50 kB</td>
      <td style="border-right: 1px solid black">3.3 kB</td>
      <td>44 kB</td>
    </tr>
  </tbody>
</table>


# 5 Logs of 20 characters per Request

_Latency_

<table style="border: 1px solid black">
  <thead style="border-bottom: 1px solid black">
    <tr>
      <th style="border-right: 1px solid black">Stat</th>
      <th style="border-right: 1px solid black">2.5%</th>
      <th style="border-right: 1px solid black">50%</th>
      <th style="border-right: 1px solid black">97.5%</th>
      <th style="border-right: 1px solid black">99%</th>
      <th style="border-right: 1px solid black">Avg</th>
      <th style="border-right: 1px solid black">Stdev</th>
      <th>Max</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <td style="border-right: 1px solid black">Latency</td>
      <td style="border-right: 1px solid black">8 ms</td>
      <td style="border-right: 1px solid black">24 ms</td>
      <td style="border-right: 1px solid black">47 ms</td>
      <td style="border-right: 1px solid black">59 ms</td>
      <td style="border-right: 1px solid black">25.01 ms</td>
      <td style="border-right: 1px solid black">11.13 ms</td>
      <td>107 ms</td>
    </tr>
  </tbody>
</table>

_Req/s_

<table style="border: 1px solid black">
  <thead style="border-bottom: 1px solid black">
    <tr>
      <th style="border-right: 1px solid black">Stat</th>
      <th style="border-right: 1px solid black">1%</th>
      <th style="border-right: 1px solid black">2.5%</th>
      <th style="border-right: 1px solid black">50%</th>
      <th style="border-right: 1px solid black">97.5%</th>
      <th style="border-right: 1px solid black">Avg</th>
      <th style="border-right: 1px solid black">Stdev</th>
      <th>Min</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <td style="border-right: 1px solid black">Req/Sec</td>
      <td style="border-right: 1px solid black">334</td>
      <td style="border-right: 1px solid black">334</td>
      <td style="border-right: 1px solid black">392</td>
      <td style="border-right: 1px solid black">435</td>
      <td style="border-right: 1px solid black">391.7</td>
      <td style="border-right: 1px solid black">30.84</td>
      <td>334</td>
    </tr>
    <tr>
      <td style="border-right: 1px solid black">Bytes/Sec</td>
      <td style="border-right: 1px solid black">25.1 kB</td>
      <td style="border-right: 1px solid black">25.1 kB</td>
      <td style="border-right: 1px solid black">29.4 kB</td>
      <td style="border-right: 1px solid black">32.6 kB</td>
      <td style="border-right: 1px solid black">29.4 kB</td>
      <td style="border-right: 1px solid black">2.31 kB</td>
      <td>25.1 kB</td>
    </tr>
  </tbody>
</table>

# 5 Logs of 100 characters per Request

_Latency_

<table style="border: 1px solid black">
  <thead style="border-bottom: 1px solid black">
    <tr>
      <th style="border-right: 1px solid black">Stat</th>
      <th style="border-right: 1px solid black">2.5%</th>
      <th style="border-right: 1px solid black">50%</th>
      <th style="border-right: 1px solid black">97.5%</th>
      <th style="border-right: 1px solid black">99%</th>
      <th style="border-right: 1px solid black">Avg</th>
      <th style="border-right: 1px solid black">Stdev</th>
      <th>Max</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <td style="border-right: 1px solid black">Latency</td>
      <td style="border-right: 1px solid black">10 ms</td>
      <td style="border-right: 1px solid black">30 ms</td>
      <td style="border-right: 1px solid black">59 ms</td>
      <td style="border-right: 1px solid black">70 ms</td>
      <td style="border-right: 1px solid black">31.54 ms</td>
      <td style="border-right: 1px solid black">13.62 ms</td>
      <td>142 ms</td>
    </tr>
  </tbody>
</table>

_Req/s_

<table style="border: 1px solid black">
  <thead style="border-bottom: 1px solid black">
    <tr>
      <th style="border-right: 1px solid black">Stat</th>
      <th style="border-right: 1px solid black">1%</th>
      <th style="border-right: 1px solid black">2.5%</th>
      <th style="border-right: 1px solid black">50%</th>
      <th style="border-right: 1px solid black">97.5%</th>
      <th style="border-right: 1px solid black">Avg</th>
      <th style="border-right: 1px solid black">Stdev</th>
      <th>Min</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <td style="border-right: 1px solid black">Req/Sec</td>
      <td style="border-right: 1px solid black">251</td>
      <td style="border-right: 1px solid black">251</td>
      <td style="border-right: 1px solid black">304</td>
      <td style="border-right: 1px solid black">351</td>
      <td style="border-right: 1px solid black">311.61</td>
      <td style="border-right: 1px solid black">30.41</td>
      <td>251</td>
    </tr>
    <tr>
      <td style="border-right: 1px solid black">Bytes/Sec</td>
      <td style="border-right: 1px solid black">18.8 kB</td>
      <td style="border-right: 1px solid black">18.8 kB</td>
      <td style="border-right: 1px solid black">22.8 kB</td>
      <td style="border-right: 1px solid black">26.3 kB</td>
      <td style="border-right: 1px solid black">23.4 kB</td>
      <td style="border-right: 1px solid black">2.28 kB</td>
      <td>18.8 kB</td>
    </tr>
  </tbody>
</table>

# 20 Logs of 5 characters per Request

_Latency_

<table style="border: 1px solid black">
  <thead style="border-bottom: 1px solid black">
    <tr>
      <th style="border-right: 1px solid black">Stat</th>
      <th style="border-right: 1px solid black">2.5%</th>
      <th style="border-right: 1px solid black">50%</th>
      <th style="border-right: 1px solid black">97.5%</th>
      <th style="border-right: 1px solid black">99%</th>
      <th style="border-right: 1px solid black">Avg</th>
      <th style="border-right: 1px solid black">Stdev</th>
      <th>Max</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <td style="border-right: 1px solid black">Latency</td>
      <td style="border-right: 1px solid black">20 ms</td>
      <td style="border-right: 1px solid black">58 ms</td>
      <td style="border-right: 1px solid black">130 ms</td>
      <td style="border-right: 1px solid black">142 ms</td>
      <td style="border-right: 1px solid black">62.09 ms</td>
      <td style="border-right: 1px solid black">26.08 ms</td>
      <td>182 ms</td>
    </tr>
  </tbody>
</table>

_Req/s_

<table style="border: 1px solid black">
  <thead style="border-bottom: 1px solid black">
    <tr>
      <th style="border-right: 1px solid black">Stat</th>
      <th style="border-right: 1px solid black">1%</th>
      <th style="border-right: 1px solid black">2.5%</th>
      <th style="border-right: 1px solid black">50%</th>
      <th style="border-right: 1px solid black">97.5%</th>
      <th style="border-right: 1px solid black">Avg</th>
      <th style="border-right: 1px solid black">Stdev</th>
      <th>Min</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <td style="border-right: 1px solid black">Req/Sec</td>
      <td style="border-right: 1px solid black">111</td>
      <td style="border-right: 1px solid black">111</td>
      <td style="border-right: 1px solid black">166</td>
      <td style="border-right: 1px solid black">202</td>
      <td style="border-right: 1px solid black">159.31</td>
      <td style="border-right: 1px solid black">28.4</td>
      <td>111</td>
    </tr>
    <tr>
      <td style="border-right: 1px solid black">Bytes/Sec</td>
      <td style="border-right: 1px solid black">8.33 kB</td>
      <td style="border-right: 1px solid black">8.33 kB</td>
      <td style="border-right: 1px solid black">12.5 kB</td>
      <td style="border-right: 1px solid black">15.2 kB</td>
      <td style="border-right: 1px solid black">11.9 kB</td>
      <td style="border-right: 1px solid black">2.13 kB</td>
      <td>8.32 kB</td>
    </tr>
  </tbody>
</table>


# Conclusion

![Requests per second](/assets/images/binary-duel/reqs_logging.png)

The results are conclusive:
- logs can impact the performance of your backend
- log the less you can!
- it is way better to log a long message instead of logging multiple small messages


---

Do you have any ideas or comments? 

Leave them under this HK post or email me via _simonedutto8+binaryduel_at_gmail.com_

If you are interested in other articles: read [You don't need a database, a queue, a distributed system: Go is enough.](https://simonedutto.github.io/2024-03-09/binary-duel)