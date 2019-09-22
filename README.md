# Lyricis-based playlist generation
See the full post here: [**rohit11may.github.io/lyricist/**]()
---

Quite often I'd find myself listening to new music and not enjoying the melody too much, but then it 
just takes one or two lyrics to change my opinion about the whole song. After two years of using
Spotify exclusively and frequently, its weekly recommendation playlists on Mondays 
(_Discover Weekly_) began to become really good; gifting me 4-5 songs each week. It caught on to 
the vibe of the music I liked and also kept up with how my taste evolved.

However, I wondered whether Spotify's recommendation engine actually factored in lyrical content 
of the songs I liked, or whether it was possible that my 'taste' in lyrics even had detectable 
patterns. This was pretty much impossible to infer from the Discover Weekly playlist directly, nor
was there much help online, so I decided to investigate myself.

### Problem Statement
At the time I started, I had around **1000 songs** that were 'liked' in my library, giving me a good
sample to represent my taste in music. As the earliest songs were saved since early 2017, this
was a relatively recent and dense representation. If there exists a pattern/taste in the lyrics of
these songs then I should be able to classify new songs as _like_ or _dislike_. Thus I arrived at 
this question. 

> **Is it possible to predict whether I like a song based *purely* on its lyrics?**
