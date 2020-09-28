# sonnets
Uses bert and GPT-2 to create sonnets. Let's start with some bragging:

```
It has no effect on him or the LORD
and he cannot harm him but he must go
and sing the praises i love hoho
and all the world shall sing it thee acord

and i love that man and all aboard
and i will not hurt him and miss crepeau
i shall go with my life with fecteau
and all my family will be award

and sing to my God i will sing the praise
and my song I shall be a god in thy
and all of you will be the kings and priests

and the earth i have made thy priests
and my children shall sing their own kansai
and sing their name as monsieur delhaize
```

The code is not (yet?) refactored but it hopefully will, at some point, maybe.
If you're going to use this I'll appreciate if you could let me know (I'm @ImCaedmon on Twitter) because I'd be really curious to see how (and if) people are going to use this. Thanks.


To make this code run you will need to **install** tensorflow, probably torch, and a bunch of other libraries. Please find a possibly not-comprehensive list of stuff to install.

```
pip install transformers
pip install syllapy
pip install phyme
pip install tweepy
pip install keras_gpt_2
```

Now (don't do it exactly now because you'll need to change the config first) please note that in order to run this whole thing the first thing you need to do is to run the **download_models** file which will download the GPT-2 model from their repository, but it is based on your config file... so let's change the config first

The **Config file** is in json. It is in json because of reasons (hopefully there will be a GUI to play with it, at some point, maybe, maybe not. Most probably not) so you have to live with it.
It is splitted in 3 nodes:

The **Twitter** node is there because this code originally was supposed to post the generated poems directly on the twitter feed of my beloved son @ImCaedmon (https://twitter.com/ImCaedmon). You can fill in your credentials if you want to post shit on Twitter or you can remove the twitter node and the program should be able to just return a finished poem. I did not need it so it's something I did not try. The last parameter is just a text which gets prepended to your poem, you can leave it empty or put an hashtag or whatever.

The **Generator** node contains some settings for the text generator: which model should it use (1558M, 774M, 355M, 345M, 124M, or 117M), the top_k parameter for GPT2 (if you care, on this page https://github.com/openai/gpt-2/issues/27 it is explained what it is. If you don't care, put 10 there) and the exclusion list for words and characters we don't want in our poem.

The **structures** node is the coolest one. It is an array of structures. If you look at the config file, it has only one element. In this case, it is the structure of a sonnet.
The struture itself is an array of verses. Let's go through them.

'rime_with' indicates with which verse our current verse should rhyme. If I put it like that, though, you'll probably not understand what I mean. Probably in school you studiet that the structure of a sonnet is ABBA ABBA CDE EDC. It means that all the verses A will rhyme with all other verses A, B with B and so on. 

'syllables' is the count of syllables that should be in a verse

'end_with' is added at the end of the verse. I'm putting my punctuation there, but if you can leave it empty or do whatever.

If a verse has a node **separator**, whatever its value, an empty row will be added to your poem. If there are other nodes, they will be ignored. It is meant to separate the parts of your poem. It may seem a pretty useless parameter but it's important because if you are using this to create a twitter bot it also indicates when the strophe has to be published - in fact if you use this for a twitter bot each strophe is published in a separate tweet (in a thread) so don't forget to put at the very least one separator at the end



If everything is configured well, when you **run the program** you will see the poem published on your twitter (if you configured it) or just printed to your screen (together with A LOT of rubbish - I should clean the logs and maybe this will be done, at some point, hopefully).

If you don't care about twitter I think you can also import poem and use the function make_poem directly passing a structure to it (by structure I mean one element of the structures array in config, e.g.


```
thePoem = make_poem( structure )
```














