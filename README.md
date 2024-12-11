## Documentation

Pointything is a simple agile/scrum tool that allows a group of users to vote on story
points for a task.  It's a personal project, not meant to be novel or even particular
useful in any way, but instead a playground to try out some technologies I was not
previously familiar with.

This project is built using

- [Astro](https://astro.build/)
- [Alpine.js](https://alpinejs.dev/)
- [htmx](https://htmx.org/)
- [tailwindcss](https://tailwindcss.com/)
- [Django](https://www.djangoproject.com/) and [Django Channels](https://channels.readthedocs.io/en/latest/)
- [Ansible](https://www.ansible.com/)

among others.  My main goals were to

1. See what its like to build a non-SPA web frontend using the latest tools
1. Try out Django Channels and see how it works.  (I have done a lot of Django and have familiarity with socket.io, but was curious about this alternative.)

Overall it was a really fun project to build.  The declarative style of Alpine.js and htmx are really
clever and offer a great alternative to heavyweights like React and Angular.  If the past I would have
reached for React whenever I needed a frontend with non-trivial interactivity, but having Alpine.js and
htmx in the toolbox makes it possible to build surprisingly complex applications that still have
small over-the-wire packages.

A live deployment of the site is available at [pointy.buttermilkcake.co](https://pointy.buttermilkcake.co)

## Running locally

I mainly use a Mac for development and find that running node watch in a container is really slow,
so I use a two-terminal local environment.  In the first terminal, run

```
docker compose up
```

That will run the backend app, redis and an nginx frontend.

In the second terminal, run

```
cd src/frontend
pnpm install
pnpm dev
```

That will install, build and watch the Astro frontend project.  The site will be available at
[localhost:8080](http://localhost:8080).

## Deploying to AWS

The build folder has some scripts to stand up an EC2 instance to run a production version
of the compose project.  It uses EC2, ECR, Route53 and LetsEncrypt.

First, copy `build/hosts.sample.yml` to `build/hosts.yml` and fill in the values.  Next review
the values in `build/group_vars/all` and make any changes to customize your deployment.  Make
sure your local SSH client is set up with the key needed to access your EC2 instance.

To build the prod containers, run

```
cd build
ansible-playbook build-container.yml
```

To stand up a new server, run

```
ansible-playbook new-server.yml
```

To stand initialize or update the SSL cert, run

```
ansible-playbook new-ssl-cert.yml
```

At this point the app should be available on your domain.  If you ever make changes and want to
deploy them, run

```
ansible-playbook build-container.yml
ansible-playbook deploy-app.yml
```
