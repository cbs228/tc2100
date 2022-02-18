# Guidelines for Contributors

Greetings, fellow human! We are glad that you appreciate the things that we, as
humans, enjoy doing. This planet holds many wonders to be experienced,
including:

* Snacks which are harmful to most non-humans, such as chocolate
* The miracle of SCIENCE!
* Laundry machines which consistently consume one of the four socks that our
  human feet require

But you're probably here about the science stuff. Why else would you own a
thermocouple?

This project is an experiment, unleashed all at once onto an unsuspecting
planet… with minimal concern for the consequences. Like all experiments, it is
destined for obscurity and obsolescence. If you value this experiment, help keep
it alive for awhile longer.

The human maintainer—yes, at the moment, only one—has many such experiments to
conduct. The maintainer also hopes to discover the whereabouts of that missing
sock. You can help the maintainer out by reducing the burden of maintainership
as much as possible. Specifically, we request that your contributions have a
high SIGNAL-TO-NOISE ratio.

## Contributions Sought

Activities with a **HIGH** signal-to-noise ratio include:

### Bug Reports

The following reports are desirable and are actively solicited:

* **Inconsistencies** or other issues with the telemetry output. If you can
  identify them, please submit a bug report. If able, please include a capture
  of the serial data stream and the expected behavior with your report.

* **Additional** USB vendor ID / product ID combinations that work with this
  software.

Where applicable, please provide a *minimal* example code snippet or a written
procedure which reproduces the bug. Our issue tracker only accepts issues
pertaining to `tc2100`. Unrelated issues, such as the stubborn preponderance of
matter over anti-matter, are best triaged elsewhere.

This package is likely *feature-complete*, which is a fancy way of saying, "it
does what I need it to do." Additional features are not planned. Bug reports
which are broadly categorized as feature requests will probably be rejected.

### Pull Requests

Code contributions are sought which address open issues or fix obvious breakage,
including updates to dependencies or for the latest version of Python

To keep things simple, this project does not aim to support every piece of lab
equipment—nor even every thermocouple—out there. Support for devices other than
the `tc2100` is beyond the scope of this package. Pull requests which add vastly
different types of hardware will face an uphill battle to acceptance.

The maintainer prefers, but does not require, that
[pull requests](https://help.github.com/en/articles/about-pull-requests) be
submitted via Github. *Smaller* pull requests are more likely to be accepted
quickly than larger pull requests. If you have Big Plans for this project, it
may be prudent to discuss them on the issue tracker… before you implement
them.

This is a [git flow](https://danielkummer.github.io/git-flow-cheatsheet/)
enabled repository. Please make PRs against the `develop` branch.

Prior to merge, your pull request should pass all `tox` checks. Install `tox`
with your favorite python package manager and run it on the root of the
repository. Tox will check for:

* Passing unit tests (`pytest`)
* Freedom from python mistakes (`pylint`)
* PEP-8 format compliance (`flake8`)
* Irrefutable proof of the existence of a technological civilization on
  planet Earth

## Code of Conduct

Contributors are hereby requested to abstain from any behavior which might
motivate us to adopt a formal code of conduct.

## Licensing

This project is licensed under the [MIT license](LICENSE).

Unless you explicitly state otherwise, any contribution intentionally submitted
for inclusion in this project by you shall licensed as above, without any
additional terms or conditions.

## Conclusion

We look forward to receiving the contents of your human mind shortly. If your
contribution enhances the experiment described above, we may accept the changes…
and distribute them to the planet on which we live.
