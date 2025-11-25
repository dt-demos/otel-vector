# Overview

This repo is used to demonstrate how to configure [Vector](https://vector.dev) data Sinks to [Dynatrace](https://dynatrace.com).

This assumes installation of both Python, the sample Python app, and Vector on a MAC, but it can be adapted to other locations such as EC2 with Linux.

To try out the demo, you will need to have 3 terminal windows.
* terminal 1 - to run the Python sample app
* terminal 2 - to run Vector as a command.  You can run as a service, but this way is easier for quick demoing and changing vector configurations
* terminal 3 - to run command line to send requests to the sample app

# Setup

### Step 1: Clone Repo

Clone this Repo and navigate to base folder of the cloned repo

```
git clone git@github.com:dt-demos/otel-vector.git
cd otel-vector
```

### Step 2: Create Dynatrace API Token

This demo will send data to the [Dynatrace Log Ingest API](https://docs.dynatrace.com/docs/discover-dynatrace/references/dynatrace-api/environment-api/log-monitoring-v2/post-ingest-logs) and the [Dynatrace OLTP API](https://docs.dynatrace.com/docs/ingest-from/opentelemetry/otlp-api)

You can just make one Dynatrace API Token with these scopes from the `Access Tokens` page within Dynatrace.
* `openTelemetryTrace.ingest`
* `metrics.ingest`
* `logs.ingest`

### Step 3: Update Environment Variables

Your Dynatrace environment and API token need to be saved to an `.env` file. The Vector configuration file refers to these variables.

To do this, first copy this template file and then edit the `.env` file for the Dynatrace tenant and the API token created in the previous step.

```
cp .env-template .env
```

### Step 4: Install Vector 

From the [Vector Docs](https://vector.dev/docs/setup/installation/package-managers/homebrew), run these command to install vector.  NOTE: You can also run Vector as a Docker container, but you will need to adjust this to use environment variables and the appropriate configuration files specified in this repo.

```
brew tap vectordotdev/brew && brew install vector
```

### Step 5: Validate Vector Config

You first need to source the `.env` file and then run these commands to valdiate the Vector configuration files.

```
source .env
vector validate --config-yaml logs/vector.yaml
vector validate --config-yaml otel/vector.yaml
```

You should see a message like

```
...
√ Component configuration
√ Health check "sink_dynatrace_otel_traces"
√ Health check "sink_dynatrace_otel_logs"
-----------------------------------------------
Validated
```

### Step 6: Install Python dependencies

This example assumed the use an [Python Virtual Environment](https://www.w3schools.com/python/python_virtualenv.asp) as to isolate the required Python packages.

To make virtual environment and install pacakges, run these commands.
```
python3 -m venv otel-vector
source otel-vector/bin/activate
pip install -r requirements.txt 
```

To start the Python app, run this command
```
python3 app.py 
```

You will keep this running on one of your terminal windows.  Enter `ctrl-c` to exit the program.

# Demo of HTTP Logs

In this demo, you will start up vector with the configuration to send logs to the [Dynatrace Log Ingest API](https://docs.dynatrace.com/docs/discover-dynatrace/references/dynatrace-api/environment-api/log-monitoring-v2/post-ingest-logs).

### Step 1: Start Vector

In a seperate terminal, run this command.  Enter `ctrl-c` to exit the program when done your demo.  

```
source .env
vector --config-yaml logs/vector.yaml
```

### Step 2: Make a test log

The vector config is looking for a `app.log` file and each time a row is added, it will send to dynatrace. To simulate logs, in another terminal and in the base folder of the repo, make some logs.  

```
echo '{"content": "Test Log","log.source": "otel-vector","severity": "error"}' >> app.log
```

Within Dynatrace, you can verify logs in the `Logs App` with a DQL statment such as this.  

```
fetch logs
| filter matchesPhrase(content,"Test Log")
```

### Step 3: Make a test log using Vector demo_log source

Vector has a [demo_logs](https://vector.dev/docs/reference/configuration/sources/demo_logs/) source than can also simulate logs.  In the the `logs\vector.yaml` file, this is configured but set to send zero logs.

To try this option, just adjust that file for example to 5 logs lines as shown below.

```
demo_log_source:
    type: demo_logs
    count: 5
```

You then just need to stop and start vector again. At startup, vector will then send in sample logs and within Dynatrace, you can verify logs in the `Logs App`.

# Demo of OTEL Data

In this demo, you will start up vector with the configuration to send data to the [Dynatrace OLTP API](https://docs.dynatrace.com/docs/ingest-from/opentelemetry/otlp-api).

### Step 1: Start Vector

In a seperate terminal, run this command.  Enter `ctrl-c` to exit the program when done your demo.  

```
source .env
vector --config-yaml otel/vector.yaml
```

### Step 2: Make a test logs 

In another terminal and in the base folder of the repo, make some logs by running this command.  The `q` querystring is the content for the log

```
curl http://localhost:5000/log?q=test_log
```

Within Dynatrace, you can verify logs in the `Logs App` with a DQL statment such as this.  

```
fetch logs
| filter matchesValue(service.name, "test_log")
```

### Step 3: Make a test spans 

In another terminal and in the base folder of the repo, make some logs by running this command.  The `q` querystring is the name of the trace request.

```
curl http://localhost:5000/trace?q=test_span
```

Within Dynatrace, you can verify logs in the `Distributed Traces App`