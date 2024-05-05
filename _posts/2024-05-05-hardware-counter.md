---
layout: post
title: "Backend Engineer tries to build a hardware counter for its side project."
author: "Simone Dutto"
---

I am building a game called [Binary Duel](https://binary-duel.com), and since we are committed to staying as simple as possible we don't have a nice admin panel with all fancy stats.

So, in an urge to build something in C (ty for the psyops to all HN), I decided to build a cute little box to show the number of games currently being played!

Here I briefly describe the project.

# The Result

![Counter](/assets/images/binary-duel/counter.jpg)

_Here is the counter in all its glory.
My decoupage skills are as good as it gets, sue me (don't)._

# The process
> For the impatient here is the code: [Github repo](https://github.com/SimoneDutto/hardware-counter)

## Hardware

### Components

- Node MCU Amica (ESP8266): similar to Arduino but with Wifi Module, smaller and cheaper
- 7-digit display
- 3x 660Ω resistor
- a bunch of jumper wires 
- old metal box
- *hopes*

### Wiring

We tend to love to copy others when doing something, however I would not copy the wiring of a backend engineer!

![Wiring](/assets/images/binary-duel/wiring.jpg)
_However, here is the photo if you are interested._

After making sure everything work is time to use a smaller board and a lot of tape to crawl of this mess inside the box (very painful).

![Inside Wiring](/assets/images/binary-duel/inside_wiring.jpg)

## Software

The code is fairly simple, we just need to:
- create an API in our service to expose the number of games being played
- fetch this number
- update the counter

However, there are things that we take for granted, that are not in a microcontroller development environment:

### Debugging
with my setup at least, it is not possible to debug the code, and for some reason, the serial output was not showing correctly with all the pins connected.

So I trusted the process and used the 7digits display to show HTTP status codes or errors.

### Sending an HTTP request and parsing the JSON
Even with using the libraries, this is the code to perform and HTTP request and parsing the response.
```c
int httpGETRequest(const char* serverName) {
  std::unique_ptr<BearSSL::WiFiClientSecure>client(new BearSSL::WiFiClientSecure);
  client->setInsecure();
  HTTPClient https;
  String payload = "{}";

  if (https.begin(*client, serverName)) {
    https.setAuthorization("username", "password");
    int httpCode = https.GET();
    if (httpCode > 0) {
      if (httpCode == HTTP_CODE_OK || httpCode == HTTP_CODE_MOVED_PERMANENTLY) {
        payload = https.getString();
        Serial.println(payload);
        https.end();
        JSONVar myObject = JSON.parse(payload);
        if (JSON.typeof(myObject) == "undefined") {
          return 999;
        }
        return int(myObject["num_games"]);
      }
    }
    return httpCode;
  }
  return -1;
}
```

### HTTP-S

We take for granted to have certificates in all of our machines that just work without setting them up.  
In a board, you don't have any certificate authority, so you need to either import them or `client->setInsecure();`

> It is not good to disable SSL verification in general, so be careful.

### Laws of physic
Usually, when a backend engineer pulls up laws of physics, it is time to pack it up and go.

However, the first time I finished this box, everything was working, so I decided to close the lid.

All of a sudden nothing was working anymore.

Can you guess why?

I guess I built a [Faraday Cage](https://en.wikipedia.org/wiki/Faraday_cage). So the Wi-Fi signal was not able to reach my board anymore.

After poking some holes in the lid, everything was working smoothly again.