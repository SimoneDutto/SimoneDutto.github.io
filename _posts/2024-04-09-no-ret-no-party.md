---
layout: post
title: "No Database No Retention No Party"
author: "Simone Dutto"
---

One month ago I wrote this article [You don't need a database, a queue, a distributed system: Go is enough.](https://simonedutto.github.io/2024-03-09/binary-duel) and I posted it on HackerNews.

The result was *interesting*: it generated quite a bit of discussion and a lot of people decided to play with [Binary Duel](https://binary-duel.com).

# The Good

![Number of games](/assets/images/binary-duel/bn-number-of-games.png)

At a certain point, there were from 80 to 150 contemporary games and everything was good: no errors, the Golang backend was behaving in the best way. ( 🎉 wohooo 🎉)

I was right, what an engineer!

# The Bad

After this initial boom, only a few people decided to revisit the game (approx 10 a day).

# The solution

The solution is quite trivial: we need a db, need login, need a leaderboard, we need a way to incentivize competition between users, and a ranking system.  
And that is exactly what we have done!
And again, Golang comes with a special treat:

_You don't actually need any dependency to do what you want, you can just code it._

### We needed a way to cache the leaderboard since it is quite expensive to build.
Building a leaderboard is expensive and difficult to maintain it updated.  
So once we get it, we need to cache it.
So, here is how you can implement a simple route cache (in memory) with TTL:

```golang
type CacheEntry struct {
    cachedResponse interface{}
    t0             time.Time
}
var routeCache map[string]CacheEntry
if cEnt, ok := routeCache["<cache-key>"]; ok && time.Since(cEnt.t0) < TTL {
    // return response cached
} else {
    // produce response
    routeCache["<cache-key>"] = value
}
```

### We needed a way to bulk write operations to save precious free tier operations.

So here is how you can implement a ticker to bulk save games and assign points in the database
```golang
go func() {
    for {
        PersistGamesAndAssignPoints()
        time.Sleep(CLEANING_WINDOW_SECONDS * time.Second)
    }
}()

```

I am having so much fun using this stack and implementing it all in this artisanal way. And I am looking forward to the moment the scale will force me to rewrite it all!


_Will all of this manage to increase retention?_
  
Do you have any ideas or comments to improve [Binary Duel](https://binary-duel.com)? 

Leave them under this HK post or email me via _simonedutto8+binaryduel_at_gmail.com_

Stay tuned!