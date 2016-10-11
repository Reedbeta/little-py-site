Title: Syntax Highlighting Test
Date: 2016-09-14 17:03:41 -0700
Categories: Test

This is a test of static syntax highlighting.

<!--more-->

Here is some unhighlighted preformatted code:
```text
Hello, world
	This line is indented
		This one even more
		<> & ! _foo_ $bar$
```

Here is some C++ code:
```cpp
#pragma once
#include "util-basics.h"
#include "util-err.h"
#include <initializer_list>
#include <type_traits>

// Base array type: not really a container, just a pointer and size,
// with the actual data stored elsewhere.
template <typename T>
struct array
{
	T *		data;
	size_t	size;

	// Subscript accessor
	T & operator[] (size_t i)
	{
		ASSERT_ERR(i < size);
		return data[i];
	}

	// Constructors
	array(): data(nullptr), size(0) {}
	array(T * data_, size_t size_): data(data_), size(size_) {}
	template <typename U> array(std::initializer_list<U> initList): data(&(*initList.begin())), size(initList.size()) {}
	template <typename U> array(array<U> a): data(a.data), size(a.size) {}
	template <typename U, size_t N> array(U(& a)[N]): data(a), size(N) {}

	// Create a "view" of a sub-range of the array
	array<T> slice(size_t start, size_t sliceSize)
	{
		ASSERT_ERR(start < size);
		ASSERT_ERR(start + sliceSize < size);
		return { data + start, sliceSize };
	}
};
```

Here is some Python code:
```python
# Parse a date string in ISO syntax (e.g. '2016-08-23')
def parseDate(dateStr):
	return datetime.date(*(int(s) for s in dateStr.split('-')))

# Convert a title to a URL slug, e.g. "My Awesome Post!!" -> 'my-awesome-post'
def slugify(title):
	return '-'.join(re.sub(r'\W', '', s.lower()) for s in title.split())

# Class for storing a rendered post and its metadata
class Post:
	def __init__(self, sourcePath, html, meta):
		self.sourcePath = sourcePath
		self.html = html

		# Extract summary (for index page) by reading up to the <!--more--> marker in the HTML.
		# Note: if the marker isn't present this will return the entire HTML.
		self.summary = html.split('<!--more-->')[0].strip()

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
		self.date		= parseDate(meta['date'][0]) if 'date' in meta else datetime.date(datetime.date.today().year + 1, 1, 1)
		self.categories	= meta.get('categories', [])
		self.files		= meta.get('files', [])
		self.hidden		= (meta['hidden'][0].lower() in ['true', 'yes']) if 'hidden' in meta else False
```

String with escape codes:
```cpp
printf("Hello, world!\t\tFoo!\n");
```

Here's some Javascript with an inline regular expression:
```js
var re = /(?:\d{3}|\(\d{3}\))([-\/\.])\d{3}\1\d{4}/;  
function testInfo(phoneInput){  
  var OK = re.exec(phoneInput.value);  
  if (!OK)  
    window.alert(phoneInput.value + " isn't a phone number with area code!");  
  else
    window.alert("Thanks, your phone number is " + OK[0]);  
}  
```

Here's some PHP with a heredoc string and variable interpolation:
```php
<?php
/* More complex example, with variables. */
class foo
{
    var $foo;
    var $bar;

    function foo()
    {
        $this->foo = 'Foo';
        $this->bar = array('Bar1', 'Bar2', 'Bar3');
    }
}

$foo = new foo();
$name = 'MyName';

echo <<<EOT
My name is "$name". I am printing some $foo->foo.
Now, I am printing some {$foo->bar[1]}.
This should print a capital 'A': \x41
EOT;
?>
```

Here's some Bash script with backticks and variable interpolation:
```bash
sudo chown `id -u` /somedir
for file in *.png
do
  mv "$file" "${file/.png/_old.png}"
done
```

Here's some LaTeX code:
```latex
\section{The Standard Model}

It's an interesting exercise to try to count how many particle species there are in the Standard
Model.  The answer depends on what you decide to consider ``distinct'' species.

First, let's limit ourselves to just the particles the SM considers fundamental (i.e.\ no hadrons).
The usual accounting goes something like this:
	\begin{itemize}
		\item 6 leptons: $e, \mu, \tau, \nu_e, \nu_\mu, \nu_\tau$
		\item 6 quarks: $u, d, s, c, b, t$
		\item 4 ``force-carrier'' bosons: $\gamma, W, Z, g$
		\item The Higgs boson.
	\end{itemize}
That adds up to 17 particle species.
```

And here are some random snippets of HLSL I gathered:

```hlsl
[numthreads(256, 1, 1)]
void cs_main(uint3 threadId : SV_DispatchThreadID)
{
	// Seed the PRNG using the thread ID
	rng_state = threadId.x;

	// Generate a few numbers...
	uint r0 = rand_xorshift();
	uint r1 = rand_xorshift();
	// Do some stuff with them...

	// Generate a random float in [0, 1)...
	float f0 = float(rand_xorshift()) * (1.0 / 4294967296.0);

	// ...etc.
}
```

```hlsl
// Constant buffer of parameters
cbuffer IntegratorParams : register(b0)
{
	float2 specPow;		// Spec powers in XY directions (equal for isotropic BRDFs)
	float3 L;			// Unit vector toward light 
	int2 cThread;		// Total threads launched in XY dimensions
	int2 xyOutput;		// Where in the output buffer to store the result
}

static const float pi = 3.141592654;

float AshikhminShirleyNDF(float3 H)
{
	float normFactor = sqrt((specPow.x + 2.0f) * (specPow.y + 2.0)) * (0.5f / pi);
	float NdotH = H.z;
	float2 Hxy = normalize(H.xy);
	return normFactor * pow(NdotH, dot(specPow, Hxy * Hxy));
}

float BeckmannNDF(float3 H)
{
	float glossFactor = specPow.x * 0.5f + 1.0f;	// This is 1/m^2 in the usual Beckmann formula
	float normFactor = glossFactor * (1.0f / pi);
	float NdotHSq = H.z * H.z;
	return normFactor / (NdotHSq * NdotHSq) * exp(glossFactor * (1.0f - 1.0f / NdotHSq));
}
```
