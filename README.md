# little-py-site

Little static site builder, made in Python 3.5 for easy customizability. You write posts in
[Markdown](https://daringfireball.net/projects/markdown/) and the script renders them, using
[Jinja templates](http://jinja.pocoo.org/) to produce the HTML output. [Disqus](https://disqus.com/)
is integrated for comments.

This is a fairly raw project without a lot of polish. I wrote it for [my personal site](http://reedbeta.com),
and you're welcome to use it as a starting point for yours, but you'll need to be comfortable with
editing Python to customize the script for your needs, and with editing HTML/CSS to customize the theme.

## Features

* Basic responsive theme.
* Syntax highlighting via [Pygments](http://pygments.org/).
* [MathJax](https://www.mathjax.org/) built-in. Math code gets passed through Markdown,
  without needing to be escaped.
* RSS feed generation.
* Apache `.htaccess` file included to create HTTP 301 redirects, for compatibility with typical
  Wordpress URI structure. Useful for not breaking links if you're migrating from Wordpress.
* Unicode-safe; all input and output text files are assumed to be UTF-8.

## Setup

Requires Python 3.5 as well as some packages. You can install the packages with:

    sudo pip install -r requirements.txt

Then open up `build_the_site.py` and edit the site domain, title, and Disqus code in the
configuration section near the top. You'll also want to open up `templates/base.html` and edit the
site author, description, and keywords in the meta tags near the top.

For previewing your site locally, you'll need a web server. [XAMPP](https://www.apachefriends.org/index.html)
is the easiest way I've found to get a local Apache instance up and running. (It comes with a bunch
of extra stuff like MySQL and PHP, but at least you can turn most of that off in the installer.)

## Usage

Run `build_the_site.py` to render everything to the `output/` directory. By default it will run in
"dev" mode, which can have a different domain, title, etc. to the production site. Use command-line
option `--prod` to build the production site, and `--clean` to destroy the output directory first
and recreate it from scratch.

## Directory Structure

* `content/`---All your posts go in here, as `.md` (Markdown) files. Each `.md` file has some
  metadata at the top to set its title, date, and how it gets rendered. See below for more.

  The script searches this directory recursively, so you can organize things in subdirectories as you like.
  The first subdirectory under `content/` is used to specify the "type" of the post (analogous to Hugo
  "sections"). So, for instance, anything under `content/blog/` will be of type `blog`. The type can
  be overridden through a post's metadata, too.

  You can also put other files, such as images, under the `content/` tree. You can reference such
  files in a post's metadata and they'll get copied to the output alongside the post.

* `output/`---The output directory, where the generated HTML will be stored by the script.

* `static/`---Static files such as CSS and images. They'll get copied to the output.

* `templates/`---Jinja template files, called by the script to render the site's pages.

## Post Metadata

Metadata uses the [Python-Markdown Meta-Data extension](http://pythonhosted.org/Markdown/extensions/meta_data.html)
syntax. Supported fields are:
* `Title`---the title of the post.
* `Slug`---the URL slug, i.e. `my-cool-post` in `http://domain.com/blog/my-cool-post/`. Generated
  automatically from the title, but can be overridden here.
* `Date`---the publication date/time and timezone of the post. Run `now.py` to print the current
  date/time in the format for this field.
* `Categories`---list of categories for the post (one per line).
* `Files`---list of files that should be copied alongside the post in the output (one per line).
  Wildcards work here, e.g. `*.png`.
* `Hidden`---yes/no. Hidden posts get rendered, but don't show up on the index page or in any lists
  of posts, so the only way to get to them is by typing in or linking to their URL.
* `Comments`---yes/no, whether comments are enabled on the post. Defaults to yes.
* `Type`---overrides the post type inferred from the directory structure.

  There are two special types:
  * `test` posts appear only in the dev version of the site, but are left out in production.
  * `page` posts are standalone, top-level entries that don't appear under any "section". Their URL
    will be simply `http://domain.com/post-slug/` rather than `http://domain.com/type/post-slug/`.

## Macros

Jinja macros defined in `templates/macros.html` can be called from Markdown source. This can be
used for bits of HTML that aren't expressible in Markdown alone. For example, the `imgcaption` macro
produces an image with a caption below it, which can optionally be floated left or right so that the
article text flows around it.

## Future Work

On my part, future development of this project is only going to consist of what I need/want for my
personal site. However, bug reports and pull requests are welcome!

Possible enhancements:
* Markdown caching. Most of the execution time of the script is in Markdown parsing/rendering, so
  caching it to avoid re-rendering unchanged posts should improve performance.
* Static LaTeX rendering to avoid the MathJax load time hit for math-heavy pages.
