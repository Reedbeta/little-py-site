Title: Macro Test
Date: 2016-09-14 20:34:33 -0700
Categories: Test
Files: hardware.jpg

This is a test of using Jinja macros from inside Markdown.

<!--more-->

Image with a caption:

{{ macros.imgcaption(
	src="hardware.jpg",
	caption="This image from the 1990 film [_Hardware_](http://www.imdb.com/title/tt0099740/) was tweeted by [Archillect](https://twitter.com/archillect).",
	alt="Creepy robot from Hardware (1990)")
}}

Here is an audio-embedding macro:

{{ macros.audio("http://www.noiseaddicts.com/samples_1w72b820/2244.mp3") }}

Here's a video-embedding one:

{{ macros.video("https://media.giphy.com/media/mIZ9rPeMKefm0/giphy.mp4", style="max-height:20em") }}

That's all for now!
