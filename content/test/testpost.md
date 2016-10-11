Title: Basic Formatting Test
Date: 2016-08-23 12:00:00 -0700
Categories: Test

Hello, world! This is a markdown document. It _can_ have **formatting** and [links](http://example.com).
Also, LaTeX equations both inline, like this: $e^{ix} = \cos x + i \sin x$, and display-style,
like this:
$$e^x = \sum_{k=0}^\infty \frac{x^k}{k!}$$
should work (using [MathJax](https://www.mathjax.org/), of course).

<!--more-->This paragraph is below the "fold", so to speak. Blah blah blabbity blah.
Foo bar baz.

Typographic tests: "double quotes", 'single quotes'. En dash: January--February. Em dash---it's a
handy punctuation alternative, but don't overuse it. Unicode characters like the minus sign: −
and the multiplication sign: × can be included directly in the source.

Emphasis_doesn't_apply_within_one_long_word.

Here are some more math tests with some tricky characters:

* Less-than and greater-than: $x < y \Longleftrightarrow y > x$
  These symbols in the source text get auto-converted to `&lt;` and `&gt;` by Markdown.
* Underscores are ok in simple cases: $a_1, a_2, \ldots a_n$.

	When the underscore is followed by a character like `\` or `{`...
	$$
		Y^m_\ell(\theta, \phi) \equiv
		(-1)^m \sqrt{\frac{(2\ell+1)}{4\pi} \frac{(\ell-m)!}{(\ell+m)!}} \,
		P^m_\ell(\cos\theta) \, e^{im\phi}
		\\
		L_{\text{reflected}}(\omega) = L_{\text{emitted}} +
			\int_\Omega L_{\text{incident}}(\omega') \, f_{\text{BRDF}}(\omega, \omega') \,
				(n \cdot \omega') \, d\omega'
	$$
	...it should be handled correctly by the python-markdown-mathjax extension.
	This also works in inline equations: $f(\theta, \phi) = \sum_{\ell,m} a_{\ell,m} Y_\ell^m(\theta, \phi)$

`Math code doesn't get interpreted inside backticks: $\|\cdot\|_1 \leq \|\cdot\|_2 \leq \|\cdot\|_\infty$`
