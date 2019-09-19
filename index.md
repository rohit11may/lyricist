---
title: Lyrics-based Playlist Generation
layout: index
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

### Approach

To prove my hypothesis I needed to:

1. Have samples of *songs I like* and *songs I don't like*. 
2. Extract lyrical features for all songs.
3. Scatter plot lyrical features.

If the liked songs **clustered** in the space of all songs, it would imply that there were 
similarities in their lyrics compared to the rest and therefore it would be possible to predict
whether I liked one based on it's lyrics!

## Using the Spotify API

What was it specifically about the lyrics that made me like a song?

 - meaning of a line, verse or the song overall
 - overall theme of song
 - rhyme scheme (if any)

{% highlight js %}
// Example can be run directly in your JavaScript console

// Create a function that takes two arguments and returns the sum of those arguments
var adder = new Function("a", "b", "return a + b");

// Call the function
adder(2, 6);
subtracter(3,6);
// > 8
{% endhighlight %}

# Scraping
## Lyrics
Some lyrics
## Songs
Some songs
# Preparation
## t-SNE
TSNE
## PCA
PCA
# Model
# Deploy
