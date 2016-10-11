#!/usr/bin/python3
#coding: utf-8

# Check Python version
import sys
if sys.hexversion < 0x03050000:
	sys.exit('You need at least Python 3.5. (You have %s.)' % sys.version.split()[0])

import argparse, codecs, collections, datetime, glob, html, itertools, \
       jinja2, markdown, os, pathlib, re, shutil, time, xml.etree.ElementTree

clockStart = time.clock()

# Command-line args
parser = argparse.ArgumentParser(description="Build the website's HTML from content/ and templates/, writing to output/.")
parser.add_argument('--clean', action='store_true', help="Clean the output/ directory and rebuild from scratch.")
parser.add_argument('--prod', action='store_true', help="Build production version of site (defaults to dev version).")
args = parser.parse_args()

# Set up site config options (these are also exposed as Jinja variables later)
if args.prod:
	siteDomain		= 'http://example.com'
	siteTitle		= 'My Awesome Blog'
	siteDisqusName	= 'example'
else:
	siteDomain		= 'http://dev.example.com'
	siteTitle		= '(Dev) My Awesome Blog'
	siteDisqusName	= 'example-dev'
siteAuthor = 'Your Name Here'

# Set up paths
sourceDir		= os.path.dirname(os.path.abspath(sys.argv[0]))
templatesDir	= os.path.join(sourceDir, 'templates')
contentDir		= os.path.join(sourceDir, 'content')
staticDir		= os.path.join(sourceDir, 'static')
outDir			= os.path.join(sourceDir, 'output')

# ----------------------------------------
# Clean the output directory, if requested
# ----------------------------------------

# Retry up to three times to work around Windows jankiness
def Retry3x(fn):
	for tries in reversed(range(3)):
		try: fn(); break
		except OSError:
			if tries == 0:	raise
			else:			time.sleep(1)	# Wait a moment before trying again...

if args.clean and os.path.exists(outDir):
	Retry3x(lambda: shutil.rmtree(outDir))

# ----------------------------
# Configure Markdown rendering
# ----------------------------

# Define a Markdown extension to passthrough LaTeX math code without applying any formatting.
# Based on python-markdown-mathjax extension by Rob Mayoff:
# https://github.com/mayoff/python-markdown-mathjax

class LatexMathPattern(markdown.inlinepatterns.Pattern):
	def __init__(self, md):
		super().__init__(r'(?<!\\)((\$\$?).+?\3)', md)
	def handleMatch(self, m):
		# Pass the math code through, unmodified except for basic entity substitutions needed for
		# XHTML compliance. Stored in htmlStash so it doesn't get further processed by Markdown.
		# Note that group numbering is off-by-1 because superclass gloms extra stuff onto our regex.
		text = html.escape(m.group(2))
		return self.markdown.htmlStash.store(text)

# Define a Markdown extension to traverse the HTML after it's rendered and tweak a couple things.
class HTMLPostprocessor(markdown.treeprocessors.Treeprocessor):
	def run(self, root):
		# For images, copy alt text to title text (if it's not already there) so it appears as a tooltip.
		for img in root.iter('img'):
			altText = img.get('alt')
			if altText and not img.get('title'):
				img.set('title', altText)

class OurExtensions(markdown.Extension):
	def extendMarkdown(self, md, md_globals):
		# Needs to come before escape matching because \ is pretty important in LaTeX
		md.inlinePatterns.add('mathjax', LatexMathPattern(md), '<escape')
		md.treeprocessors.add('htmlpost', HTMLPostprocessor(md), '_end')

# Configure Markdown with all the extensions we want
md = markdown.Markdown(
		extensions=[
			'markdown.extensions.attr_list',
			'markdown.extensions.codehilite',
			'markdown.extensions.fenced_code',
			'markdown.extensions.meta',
			'markdown.extensions.sane_lists',
			'markdown.extensions.smarty',
			'markdown.extensions.smart_strong',
			'markdown.extensions.toc',
			OurExtensions(),
		],
		extension_configs = {
			'markdown.extensions.smarty': {
				# Use Unicode characters instead of HTML entities for substitutions
				'substitutions': {
					'left-single-quote': '‘',
					'right-single-quote': '’',
					'left-double-quote': '“',
					'right-double-quote': '”',
					'ellipsis': '…',
					'ndash': '–',
					'mdash': '—',
				},
			},
		},
	)

# ------------------------------------------------------------------------------------------
# Gather all the .md files in content/, render Jinja macros and Markdown, and build metadata
# ------------------------------------------------------------------------------------------

# Configure Jinja to load templates from the templates/ directory
j = jinja2.Environment(
		loader = jinja2.FileSystemLoader(templatesDir),
		trim_blocks = True,
		lstrip_blocks = True,
		extensions=['jinja2.ext.do'],
	)

# Provide Markdown rendering as a Jinja filter so macros can apply it e.g. to captions.
# This is needed because Markdown doesn't apply formatting to text inside inline <div>s and such.
j.filters['md'] = md.convert

# Set up Jinja for rendering macros inside posts. This is done before Markdown rendering, to avoid
# Markdown adding extra <p> tags around macro invocations.
templateMacros = j.get_template('macros.html')
j.globals['macros'] = templateMacros.module

# Convert a title to a URL slug, e.g. "My Awesome Post!!" -> 'my-awesome-post'
def slugify(title):
	return '-'.join(re.sub(r'[^-\w<>]|<.*?>', '', s.lower()) for s in title.split())

# Class for storing a rendered post and its metadata
class Post:
	def __init__(self, sourcePath, postHtml, meta):
		self.sourcePath = sourcePath
		self.html = postHtml

		# Extract summary (for index page) by reading up to the <!--more--> marker in the HTML.
		# Note: if the marker isn't present this will return the entire HTML.
		self.summary = postHtml.split('<!--more-->')[0].strip()

		# Allow post type to be specified by the name of the subdirectory under content/,
		# but this can be overridden by metadata.
		if 'type' in meta:
			self.type = meta['type'][0]
		else:
			subdir = os.path.dirname(os.path.relpath(sourcePath, contentDir))
			if subdir:
				self.type = pathlib.PurePath(subdir).parts[0]
			else:
				self.type = 'blog'

		# Normalize the other metadata parsed out of the source file.
		self.title		= meta['title'][0] if 'title' in meta else 'Untitled Post'
		self.slug		= meta['slug'][0] if 'slug' in meta else slugify(self.title)
		self.date		= datetime.datetime.strptime(meta['date'][0], '%Y-%m-%d %H:%M:%S %z') if 'date' in meta else None
		self.categories	= meta.get('categories', [])
		self.files		= meta.get('files', [])
		self.hidden		= markdown.util.parseBoolValue(meta['hidden'][0]) if 'hidden' in meta else False
		self.comments	= markdown.util.parseBoolValue(meta['comments'][0]) if 'comments' in meta else True

		# Version of date used for a sort key, where None is replaced by MAXYEAR so that undated
		# posts will sort to the top (in descending chronological order).
		self.sortDate = self.date if self.date else datetime.datetime(datetime.MAXYEAR, 1, 1, tzinfo=datetime.timezone.utc)

		# Canonical link to the post will be like: http://server/type/slug/
		# Unless it's the special "page" type, in which case just http://server/slug/.
		if self.type == 'page':
			self.url = '/%s/' % self.slug
		else:
			self.url = '/%s/%s/' % (self.type, self.slug)

# Store the rendered posts indexed various ways.
allPosts		= []
postsByType		= collections.defaultdict(list)
postsByCategory	= collections.defaultdict(list)

# Find the markdown files in the content directory.
for sourcePath in glob.iglob(os.path.join(contentDir, '**', '*.md'), recursive=True):
	with codecs.open(sourcePath, mode='r', encoding='utf-8') as f:
		sourceText = f.read()

	# Render Jinja macros
	mdText = j.from_string(sourceText).render()

	# Render Markdown and extract metadata
	postHtml = md.convert(mdText)
	post = Post(sourcePath, postHtml, md.Meta)
	md.reset()

	# When building the production site, skip posts of type "test"
	if args.prod and post.type == 'test':
		continue

	# Add to the lists of posts
	allPosts.append(post)
	postsByType[post.type].append(post)
	for c in post.categories:
		postsByCategory[c].append(post)

# Sort posts by date starting from most recent
mostRecent = { 'key': lambda p: p.sortDate, 'reverse': True }
allPosts.sort(**mostRecent)
for posts in postsByType.values():
	posts.sort(**mostRecent)
for posts in postsByCategory.values():
	posts.sort(**mostRecent)

# -------------------------------------------------
# Render all the site's pages using Jinja templates
# -------------------------------------------------

j.globals['SiteDomain'] = siteDomain
j.globals['SiteTitle'] = siteTitle
j.globals['SiteDisqusName'] = siteDisqusName
j.globals['SiteAuthor'] = siteAuthor

# Make the list of non-hidden posts available to templates
j.globals['AllPosts'] = [p for p in allPosts if not p.hidden]

# Make categories available to templates, as well as the count of non-hidden posts in each one,
# sorted by descending count then name.
j.globals['AllCategories'] = sorted(
								((c, len([p for p in posts if not p.hidden])) for c, posts in postsByCategory.items()),
								key=lambda x:(-x[1], x[0]))

# Expose time and datetime modules to templates
j.globals['datetime'] = datetime
j.globals['time'] = time

# Make the slugify function available, too, as Jinja unaccountably doesn't have this built in
j.filters['slugify'] = slugify

# Define a function to find relative URLs found in a post body and convert them to absolute (within
# the server) by prefixing the post's canonical URL. This is used for rendering posts on index pages.
# Not comprehensive---just uses regexes to find the most common elements where URLs appear, such as
# <a>, <img> and so forth.
def absoluteUrls(postHtml, urlPrefix):
	postHtml = re.sub(r'href="(?!/|https?://)', r'href="%s' % urlPrefix, postHtml)
	postHtml = re.sub(r'src="(?!/|https?://)', r'src="%s' % urlPrefix, postHtml)
	return postHtml
j.filters['absoluteUrls'] = absoluteUrls

# Load all our templates
templateIndex		= j.get_template('index.html')
template404			= j.get_template('404.html')
templatePost		= j.get_template('post.html')
templateIndexType	= j.get_template('index-type.html')
templateCategory	= j.get_template('category.html')
templateAll			= j.get_template('all.html')
templateFeed		= j.get_template('feed.xml')

Retry3x(lambda: os.makedirs(outDir, exist_ok=True))

# Render the index page
with codecs.open(os.path.join(outDir, 'index.html'), mode='w', encoding='utf-8') as f:
	f.write(templateIndex.render())

# Render the 404 page
with codecs.open(os.path.join(outDir, '404.html'), mode='w', encoding='utf-8') as f:
	f.write(template404.render())

# Render the pages for the individual posts
for type, posts in postsByType.items():
	for i, p in enumerate(posts):
		postOutDir = os.path.join(outDir, os.path.normpath(p.url[1:]))	# Strip leading '/' from URL
		os.makedirs(postOutDir, exist_ok=True)

		# Set up the variables that will be available to the template.
		# The special "page" type doesn't get prev/next links. Also, hidden posts don't show up
		# in prev/next links (but they still get rendered).
		postVars = { 'Post': p }
		if type != 'page':
			for q in reversed(posts[:i]):
				if not q.hidden: postVars['PrevPost'] = q; break
			for q in posts[i+1:]:
				if not q.hidden: postVars['NextPost'] = q; break

		# Render the post into index.html in its output directory
		with codecs.open(os.path.join(postOutDir, 'index.html'), mode='w', encoding='utf-8') as f:
			f.write(templatePost.render(**postVars))

		# Update any other files that the post depends on into the output directory as well.
		if p.files:
			postSourceDir = os.path.dirname(p.sourcePath)
			for pattern in p.files:
				for f in glob.glob(os.path.join(postSourceDir, os.path.normpath(pattern))):
					destPath = os.path.join(postOutDir, os.path.relpath(f, postSourceDir))
					os.makedirs(os.path.dirname(destPath), exist_ok=True)
					srcStat = os.stat(f)
					if (not os.path.exists(destPath)) or os.stat(destPath).st_mtime != srcStat.st_mtime:
						shutil.copy2(f, destPath)

	# Render the type listing page if one is needed
	if type not in ['blog', 'page', 'test']:
		typeDir = os.path.join(outDir, type)
		os.makedirs(typeDir, exist_ok=True)
		with codecs.open(os.path.join(typeDir, 'index.html'), mode='w', encoding='utf-8') as f:
			f.write(templateIndexType.render(
						PostType = type,
						Posts = [p for p in posts if not p.hidden],
						PageTitle = { 'made': 'Stuff I’ve Made', 'talks': 'Talks' }[type]
			))

# Render the category listing pages
for c, posts in postsByCategory.items():
	categoryDir = os.path.join(outDir, 'blog', 'category', slugify(c))
	os.makedirs(categoryDir, exist_ok=True)
	with codecs.open(os.path.join(categoryDir, 'index.html'), mode='w', encoding='utf-8') as f:
		f.write(templateCategory.render(
					CategoryName = c,
					CategoryPosts = [p for p in posts if not p.hidden]
		))

# Render the list of all posts
os.makedirs(os.path.join(outDir, 'all'), exist_ok=True)
with codecs.open(os.path.join(outDir, 'all', 'index.html'), mode='w', encoding='utf-8') as f:
	f.write(templateAll.render())

# Render the RSS feed
os.makedirs(os.path.join(outDir, 'feed'), exist_ok=True)
with codecs.open(os.path.join(outDir, 'feed', 'index.xml'), mode='w', encoding='utf-8') as f:
	f.write(templateFeed.render())

# -------------------------------------------
# Update static files from static/ to output/
# -------------------------------------------

# Recursively copy everything from static/ to output/, only touching files that either don't exist
# or are out-of-date in the destination
for srcDir, _, files in os.walk(staticDir):
	destDir = os.path.join(outDir, os.path.relpath(srcDir, staticDir))
	if not os.path.exists(destDir):
		# Can use copytree at this point because destination dir doesn't exist.
		shutil.copytree(srcDir, destDir)
	else:
		# Go file-by-file
		for f in files:
			srcPath = os.path.join(srcDir, f)
			destPath = os.path.join(destDir, f)
			srcStat = os.stat(srcPath)
			if (not os.path.exists(destPath)) or os.stat(destPath).st_mtime != srcStat.st_mtime:
				shutil.copy2(srcPath, destPath)

clockEnd = time.clock()
print('Done in %0.2fs' % (clockEnd - clockStart))
