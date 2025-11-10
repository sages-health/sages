### Docker
* This project can be run via docker
* There are a few ways to launch application services depending on your use case

#### Installing Docker & Docker Compose

* Ubuntu: https://docs.docker.com/engine/install/ubuntu/ 

* Windows & Mac: https://www.docker.com/products/docker-desktop/ (you need a license)

* Windows WSL2: https://docs.docker.com/desktop/windows/wsl/

#### Building Services

* Before services can be launched, their images need to be built with the `docker compose build` command
* This should happen automatically the first time you try to run the stack
* Whenever code changes for a service's image, that image should be rebuilt. Note that the workers and the backend share the same image.

---

### Running on Different Environments
* The dockerization of the application services allows for flexible runtime.
* In general only a few changes need to be made to ensure a functioning system:
  * which data bridge connection information file will be used. These can be changed by modifying which file is targeted in `backend/app.config.py` when running on your machine or changing which file gets mounted in the docker compose file.
  * the nginx hostname & config. These can be changed by modifying the nginx environment variables either 
    through a `.env` file or a `docker-compose.override.yml` override.
  * services can be disabled in the `docker-compose.override.yml` file by adding the snippet below to services. These 
    services can then be run in some other un-dockerized fashion.
  * services can also be excluded by only specifying the core containers to run `docker compose up -d nginx backend` and running the services in some other way or spun up as needed.
```yaml
    deploy:
      replicas: 0
```
* Some examples are listed below

##### Running all built services on the Vims-Dev server
* the defaults in `docker-compose.yml` are set for running the `vims-dev` test instance.
* this can be run via `docker compose -f docker-compose.yml up -d`. 
  * We need to manually specify the `docker-compose.yml` file to avoid the configuration in the `docker-compose.override.yml` file


##### Running all built services locally
* this can be run via `docker compose -f docker-compose.yml up -d`
* You need to override the nginx variables `HOSTNAME` to `localhost` and `NGINX_TEMPLATE_SUFFIX` to `.local_template`


##### Running a subset of built services locally for development
* this can be run with just `docker-compose up -d` as that will automatically apply the configuration changes in 
`docker-compose.override.yml` 
* if you want to perform frontend development
  * Change `NGINX_TEMPLATE_SUFFIX` to `.dev_template`
  * Run the development server
* if you want to perform backend development
  * in your `docker-compose.override.yml` file ensure that the `backend` service is not launched by adding the 
    `replicas: 0` configuration seen above
  * Run the backend with `python -m vims.app`

---

* Can be run via `docker compose`. Example `docker-compose.yml` file below
```yaml 
  version: '3.3'
  services:
    mysql:
      container_name: db
      image: mysql/mysql-server:8.0
      restart: always
      ports:
        - "3306:3306"
      volumes:
        - db_data:/var/lib/mysql
      environment:
        MYSQL_ROOT_PASSWORD: "${SAGES_DB_ROOT_PASSWORD:-password}"
        MYSQL_DATABASE: "${SAGES_DB:-panet}"
        MYSQL_USER: "${SAGES_DB_USER:-admin}"
        MYSQL_PASSWORD: "${SAGES_DB_USER_PASSWORD:-password}"

  volumes:
    db_data:
```
