# OJ-UCI Docker

This repository contains the Docker files to run the [TGBOJ-v2](https://github.com/TGB-Dev/tgboj-v2)

Based on [vnoj-docker](https://github.com/VNOI-Admin/vnoj-docker).

## Installation

First, [Docker](https://www.docker.com/) and [Docker Compose](https://docs.docker.com/compose/) must be installed. Installation instructions can be found on their respective websites.

Clone the repository:

```sh
git clone --recursive https://github.com/leo20826/OJ-UCI.git
cd OJ-UCI/dmoj
```

From now on, it is assumed you are in the `dmoj` directory.

> [!NOTE]
> The following steps should be done in the specified order to prevent conflicts and/or random issues, so read the whole `README.md` file first, then start the process.

> [!IMPORTANT]
> Remember to change the `SECRET_KEY` inside the `dmoj/config/local_settings.py`. For some reason, only that variable has issue when loaded via environment files, so hardcoding is the only stable way to workaround that.
>
> This should be done before moving to next steps.

Initialize the setup by moving the configuration files into the submodule and creating the necessary directories:

```sh
./scripts/initialize
```

Next, configure the environment variables in the files in `dmoj/environment/`. Create the files from the examples:

```sh
cp environment/mysql-admin.env.example environment/mysql-admin.env
cp environment/mysql.env.example environment/mysql.env
cp environment/site.env.example environment/site.env
cp environment/email.env.example environment/email.env
```

Then, set the MYSQL passwords in `mysql.env` and `mysql-admin.env`, and the host and secret key in `site.env`.

Next, build the images:

```sh
docker compose build
```

Start up the site, so you can perform the initial migrations and generate the static files:

```sh
docker compose up -d site db redis celery
```

You will need to generate the schema for the database, since it is currently empty:

```sh
./scripts/migrate
```

You will also need to generate the static files:

```sh
./scripts/copy_static
```

Finally, the TGBOJ comes with fixtures so that the initial install is not blank. They can be loaded with the following commands:

```sh
./scripts/manage.py loaddata navbar
./scripts/manage.py loaddata language_small

# Should only be run on blank systems
./scripts/manage.py loaddata demo
```

Keep in mind that the demo fixture creates a superuser account with a username and password of `admin`. You should change the user's password or remove the user entirely.

You can also create a superuser account for yourself:

```sh
./scripts/manage.py createsuperuser
```

## Usage

To start everything:

```sh
docker compose up -d
```

To stop everything:

```sh
docker compose down
```

## Notes

### Judge server

The judge server is not included in this Docker setup. Please refer to [Setting up a Judge](https://vnoi-admin.github.io/vnoj-docs/#/judge/setting_up_a_judge).

The bridge instance is included in this Docker setup and should be running once you start everything.

### Migrating

As the OJ site is a Django app, you may need to migrate whenever you update. Assuming the site container is running, running the following command should suffice:

```sh
./scripts/migrate
```

### Managing Static Files

If your static files ever change, you will need to rebuild them:

```sh
./scripts/copy_static
```

### Updating The Site

Updating various sections of the site requires different images to be rebuilt.

If any prerequisites were modified, you will need to rebuild most of the images:

```sh
docker compose up -d --build base site celery bridged wsevent
```

If the static files are modified, read the section on [Managing Static Files](#managing-static-files).

If only the source code is modified, a restart is sufficient:

```sh
docker compose restart site celery bridged wsevent
```

### Caddy

We use Caddy because of its ease of config.

> [!IMPORTANT]
> Remember to change the website's URL in `dmoj/caddy/config/Caddyfile` for Caddy to automatically get the HTTPS certificate.
