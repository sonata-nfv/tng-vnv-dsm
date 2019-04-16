[![Join the chat at https://gitter.im/sonata-nfv/Lobby](https://badges.gitter.im/Join%20Chat.svg)](https://gitter.im/sonata-nfv/Lobby) [![Build Status](https://jenkins.sonata-nfv.eu/buildStatus/icon?job=tng-vnv-dsm/master)](https://jenkins.sonata-nfv.eu/job/tng-vnv-dsm/job/master/)

<p align="center"><img src="https://github.com/sonata-nfv/tng-api-gtw/wiki/images/sonata-5gtango-logo-500px.png" /></p>

# tng-vnv-dsm
## Decision Support Mechanism/SVD-based Recommender System

This repository includes the `tng-vnv-dsm` component, which incorporates the Decision Support Mechanism of the 5GTANGO Catalogues, both of which are part of the European H2020 project [5GTANGO](http://www.5gtango.eu). The component is responsible for delivering test recommendations to the end-users of the 5GTANGO ecosystem, through the deployment of matrix-factorization techniques.

## Documentation

Besides this README file, more documentation is available in the [wiki](https://github.com/sonata-nfv/tng-vnv-dsm/wiki) belonging to this repository.

## Installation and Dependencies

This component is implemented in Python3. Its requirements are specified in the `requirements.txt` in the root folder as follows [here](https://github.com/sonata-nfv/tng-vnv-dsm/blob/master/requirements.txt). In general, a new virtual environment would be beneficial in the installation.

### Automated installation:

The automated installation requires `pip` (more specifically `pip3`).

```bash
$ pip install git+https://github.com/sonata-nfv/tng-vnv-dsm
```

### Manual installation:

```bash
$ git clone git@github.com:sonata-nfv/tng-vnv.dsm.git
$ cd tng-vnv-dsm
$ python setup.py install
```

## Usage

The Decision Support mechanism is delivered to be deployed as a micro service, offering a REST API to provide recommendations on top of the 5GTANGO Catalogues. However, it can be utilized as a standalone service to provide recommendations based on SVD matrix factorization technique.


#### Run `tng-vnv-dsm` as a service:

##### Docker-based

In this option, a functional mongoDB is essential for the core functionality of the service.
```bash
# build Docker container
sudo docker build .

# run Docker container
docker run --rm -d -p 4010:4010 --name tng-vnv-dsm registry.sonata-nfv.eu:5000/tng-vnv-dsm
```

## Development

To contribute to the development of this 5GTANGO component, you may use the very same development workflow as for any other 5GTANGO Github project. That is, you have to fork the repository and create pull requests.

### Setup development environment

```bash
$ python setup.py develop
```

### CI Integration

All pull requests are automatically tested by Jenkins and will only be accepted if no test is broken.

## License

This 5GTANGO component is published under Apache 2.0 license. Please see the LICENSE file for more details.

---
#### Lead Developers

The following lead developers are responsible for this repository and have admin rights. They can, for example, merge pull requests.

- Marios Touloupou ([@mtouloup](https://github.com/mtouloup))

#### Feedback-Chanel

* Please use the GitHub issues to report bugs.