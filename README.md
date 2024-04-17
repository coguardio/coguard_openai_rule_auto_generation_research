# Using LLMs to generate policies for configuration security

## Introduction

Disclosure: This research was partially funded under [OpenAI's Cybersecurity Grant
program](https://openai.com/blog/openai-cybersecurity-grant-program).

In this research, we present our work on using the OpenAI
API to help battle the problem of software and platform misconfiguration. The
misconfiguration of software is a common cause of data breaches and
other security vulnerabilities and risks. The complexity of
configuring an interconnected cloud application is greater than just configuring an individual
piece of software in isolation. The complexity in configuring cloud
applications grows with each interconnected component. Configuring
cloud environments becomes significantly complex as applications are
inter-connected and networks expand into clusters, multiplying
configuration files and dependencies between nodes.

Many open-source software-driven configuration scanning solutions require
developers to write and maintain rules-based policies, e.g., REGO
rules in [Open Policy Agent](https://www.openpolicyagent.org) based
frameworks. These rules may not check
all of the possible configurations for each individual piece of
software and may not include the inter-connectivity between
components. Additionally these policies and rule-sets are not
maintained with current software updates due the complexity
and challenges of rule maintenance, and do not include many of the commonly used server
software in their policies. This is creating a false sense of security in having completed
a configuration scan, but with unknown risks.

This is why CoGuard was founded. We are on a mission to prevent
misconfigurations from making it into production, at all layers of the
infrastructure. We have built a
configuration scanner which takes interconnection into account, and
can grow its ruleset, supported services and diverse infrastructure fast.

As software infrastructures continue to grow in complexity,
and this requires automated quality control tooling to evaluate configurations
and reduce the risk of humman error in evaluating safe/secure configurations. CoGuard consists of
two parts:
-  **CoGuard Engine and Infrastructure Model** -- a predicate logic engine and representation of infrastructure,
network, containers and applications.
- **Policies, Rules and Rulesets** -- Supported services, applications and compliance frameworks.

Adding and maintaining the rules is a manual process.
Using OpenAI and CoGuard, we see a way to identify and add
new policies/rules for configurations of all kinds of software and
maintain or future proof existing configurations.

### Increasing Software Choices

The landscape of technologies used in modern organizations is
expanding (see e.g. the [increasing adoption of SaaS
products](https://www.statista.com/statistics/1233538/average-number-saas-apps-yearly/).),
which leads to an increasing complexity of maintenance of software and
tools used inside an organization. Each database, web server,
messaging system, etc., adds a custom configuration, and each
configuration is also contextually interdependent with
others. Networking each container and device adds additional
complexity with cloud configuration or other hosting configurations
and the configurations of the operating systems, firewalls, etc. The
complexity expands “exponentially”.

To illustrate the number of different configuration parameters for different projects, please consider the following table.

| Project Name                                                                        | Current # of Configuration parameters |
|-------------------------------------------------------------------------------------|---------------------------------------|
| Apache Kafka (not including Log4j)                                                  | >300                                  |
| Apache Hadoop (core, hdfs and mapreduce)                                            | >1100                                 |
| AWS CloudFormation (and hence also Terraform AWS providers and Ansible AWS modules) | >2000                                 |
| Azure Resource Manager                                                              | >2000                                 |
| Google Cloud                                                                        | >2000                                 |
| Kerberos (KRB5 + KDC)                                                               | >100                                  |
| PostgreSQL (extracted via pg_settings)                                              | >300                                  |
| MySQL                                                                               | >500                                  |
| Apache HTTPD                                                                        | >300                                  |
| NGINX (basic modules)                                                               | >300                                  |


Misconfiguration scanning and identification is a feature that is
offered by major security vendors, but they mainly touch the cloud
configurations and some container orchestration. Some customers have recognized the risks
and the problems associated with misconfigurations and are seeking
solutions to fight back. Right now, they are performing mostly manual
processes by tasking their DevOps teams to go through CIS-benchmark
documents and checking their configurations with the help of
those. With the increase of error-based data-breaches as per Verizon's
yearly ["Data-breach investigations
report"](https://www.verizon.com/business/resources/reports/dbir/),
more and more organizations are recognizing the importance of securing
each software piece in the infrastructure.

A review of [a sample of technology
stacks](https://stackshare.io/stacks) showed a significant portion of
configurable software that is self-reportedly used in production
environments, but is currently not covered by automated scanners on
the market.

Adding new tools to existing configuration scanning frameworks is slow
and difficult. We have selected 15 configurable software projects that
are not automatically scanned, i.e., they are not included in the
rulesets used by configuration scanners, despite the age of the
software and the wide adoption with organizations:

- Apache Spark
- Apache Airflow
- Jenkins
- Hive
- CouchDB
- Cassandra
- Druid
- Iceberg
- Zeppelin
- Jupyter
- Ignite
- GraphQL
- NiFi
- Flink
- Mesos

All of these projects may handle secrets and sensitive information,
i.e. securing each one of them is relevant for compliance purposes.

This document contains the research on the viability of LLMs to solve
this problem. We are going to create a modularized pipeline approach
to generate rules and tests from these rules for software. From
manuals to policies. Each module in the pipeline is examined for
applicability of LLMs in terms of the completeness and accuracy of the
provided output. The goal is to create a baseline with simple
functionality, which can then be optimized and extended in future work.

This research was partially funded under [OpenAi's Cybersecurity Grant
program](https://openai.com/blog/openai-cybersecurity-grant-program).

### Assumptions and versions

We assume using the current training data of OpenAI, which is
cut off 2022-01.

The OpenAI API wrapper version used for Python was 1.13.3, while the
Python version was 3.11.8.

Unless stated otherwise, the model used for each prompt has been
GPT-4.

### Related work

- https://arxiv.org/pdf/2205.12615.pdf
- https://arxiv.org/abs/1910.08210

## General architecture

Let us summarize how the general architecture of the described system
can be modularized. We have, after some experimentation and discussion
defined the following components.

### Running example

As a running example for each component, and as our first general
research test case, we are using [Apache
Spark](https://spark.apache.org).
We have selected Spark because it is a highly distributed software
system (over [38k stars on GitHub](https://github.com/apache/spark))
with enough configuration parameters (above 300). These qualities make
Spark a good test for identifying important config parameters.
Additionally, Spark has not been included in any of the common security
benchmarks, such as [CIS](https://www.cisecurity.org) or [DoD
Stigs](https://public.cyber.mil/stigs/downloads/). This ensures that
there are no existing security benchmark data that OpenAI could have
been trained from.

### [C1] Extraction of security and uptime-relevant configuration parameters from manuals

The goal of this component is simple to describe, but hard to
accomplish. Given a manual for a software component, extract the
configuration parameters and define the security relevant ones from
it.

**Example:** For Apache Spark, the manual is provided on the general [confiugration
page](https://spark.apache.org/docs/latest/configuration.html#spark-ui)
online, i.e. in HTML format, and there is also a specific [security
page](https://spark.apache.org/docs/latest/security.html). The
expectation would be to at least extract the parameters from the
security page, as well as some log-related items from the general
page. In total, when manually examining the configuration parameters,
it totals approximately 80 parameters that are security relevant. You can
find these in the [Appendix A](##appendix-a).


### [C2] Identification of defaults and recommended values

This component assumes that [C1] has run and uses each extracted
parameter.

Each configuration parameter may have a default value. From a security
perspective, and to correctly define the rule, one should know what
the recommended value should be and if it coincides with the default
value.

There may be an operator involved which describes the
recommended value. This operator may be in relation to the default
value as well.

The input for this component is one or more configuration
parameters, and the output should be a combination of quadruples
comprised of:

- `configuration_parameter`: The configuration parameter name;
- `default_value`: The value of the parameter if it is not explicitly
  set in the configuration file. This can be empty if by default,
  there is no value set;
- `recommended_value`: The value the parameter should be set for
  security purposes;
- `operator`: The operator to be applied when formulating the rule.

**Example:** An example for a `configuration_parameter` could be in
spark `spark.ssl.enabled`.

**Example:** When it comes to `default_value`, `spark.ssl.enabled` is
set by default to `false`, but should be set to `true`. In this way,
encryption in transit is fulfilled. Another parameter is
`spark.authenticate.secret.file`. The default value for this parameter
would be empty, since the path to the file is custom to the user's
setup and can not possibly be predicted.

**Example:** When it comes to recommended values, you can already see
from the previous example that `spark.ssl.enabled` should be set to
`true`. When it comes to the `spark.authenticate.secret.file`
parameter, the recommended rule for this
scenario would be to have this parameter simply existing.

**Example:** The operators that we currently support in CoGuard can be
found in [Appendix B](##appendix-b).

### [C3] Translation of identified parameters and recommended values into rules

This module will take the output from [C2] as input. The goal is to
get a list of related quadruples as a list (if all conditions have to
be fulfilled at the same time), and produce a policy definition in
either our proprietary, SAT based definition or any other format
(CoGuard e.g. also provides a Python API for the parsed file).

The main components for the policy definition can be defined as
follows:

- An identifier: A unique identifier of this specific issue, so that
  it can be catalogued.
- A severity estimation, i.e. how impactful not setting this value
  would be.
- Documentation: A short description of the parameter, why it matters
  from a security perspective, and what goal is achieved by setting it
  to the recommended value.
- Remediation: A short description how to fix the issue, i.e. in which
  configuration file and how to set the fix.
- Sources: References to the configuration parameter and potentially
  direct references to security frameworks stating that setting this
  value concludes in the expected behavior.
- The policy as defined by the domain specific language
  ([DSL](https://en.wikipedia.org/wiki/Domain-specific_language)) of
  the chosen policy engine (e.g. [CoGuard](https://www.coguard.io) or
  [OPA](https://www.openpolicyagent.org))

The output of this component, as long as described to the LLM either in words or
through [function
calls](https://platform.openai.com/docs/guides/function-calling),
should be exactly the policy that would check if the set of parameters
is fulfilling the recommended value or not (including the knowledge of
the default parameter).

**Example:** The output in our proprietary format for the
`spark.ssl.enabled` property would be

```json
{
  "identifier": "apache_spark_enable_ssl",
  "severity": 4,
  "documentation": {
    "description": "Not enabling SSL for Apache Spark can leave the data and the operations running on the cluster exposed to potential man-in-the-middle attacks. This would potentially allow attackers to view or modify the data in transmission.",
    "remediation": "To enforce this policy, set the 'spark.ssl.enabled' parameter to 'true' in the Apache Spark configuration file. The default setting for this parameter is 'false'.",
    "sources": [
      "https://spark.apache.org/docs/latest/security.html"
    ]
  },
  "clauses": [
    {
      "literals": [
        {
          "service": "apache_spark",
          "configurationFile": "spark-defaults.conf",
          "keyPath": [
            "spark.ssl.enabled"
          ],
          "operator": "is",
          "value": "true",
          "default": "false"
        }
      ]
    }
  ]
}
```

### [C4] Creation of test configuration files to verify the created rules

We at CoGuard are committed to ensuring that all policies have not only a small chance of
ending up being a false positive/true negative, but also ensuring proper change management.
This is why we have a test for every policy for a `fail` scenario, a
`pass` scenario and a `default` scenario (the latter can be either
pass or fail, dependent on the default). These are practical tests ensuring that
the logic formulating the policy has not been flawed and that edge cases are properly
failing or passing.

For each scenario, we are normally crafting test files, and run the CoGuard
engine against it.

These files have to be created with the appropriate values and the correct
format (there are many configuration file formats out there, e.g. [INI](https://en.wikipedia.org/wiki/INI_file),
[properties](https://en.wikipedia.org/wiki/.properties),
[HCL2](https://developer.hashicorp.com/nomad/docs/job-specification/hcl2),
[YAML](https://en.wikipedia.org/wiki/YAML)).

The goal with these test files is to cover as many base and edge cases as possible
that should either controllably fail the policy, or pass it.

Hence, the goal of the last component is to create these test files for the auto-generated rules,
so that the policies can then be tested against the engine in a
feedback loop, and to have everything set for the future maintenance
of this rule. In this way, feedback about the created rules can be
right away sent back to the engine for re-creation of either test or policy files in case of an error.

**Example:** For the `spark.ssl.enabled` property, there should be
three test files in place.

Fail:
```
# spark-defaults.conf
spark.ssl.enabled = false
```
Pass:
```
# spark-defaults.conf
spark.ssl.enabled = true
```

Fail via default:
```
# spark-defaults.conf
```

One may also add as a remark here that there are other parameters that
also need to be set once `spark.ssl.enable` is true, like the
certificate locations. But these files are just created for as minimal examples
to ensure that the rules that check for this specific parameter are passing or failing respectively.

### Summarizing the generalized architecture visually

```
+----------------+       +----------------+         +------------------+         +--------------------+
|      [C1]      |       |     [C2]       |         |     [C3]         |         |       [C4]         |
|                |       |                |         |                  |         |                    |
| Parameter ex-  +------>| Identification +-------->| Generation of    +-------->| Generation of      |
| traction from  |       | of default and |         | policy file and  |         | test files.        |
| configurations |       | recommended    |         | documentation    |         |                    |
|                |       | settings       |         |                  |         |                    |
+----------------+       +----------------+         +------------------+----+----+--------------------+
                                                            ^               |
                                                            |               |
                                                            |               v
                                                            + +------------------------------+
                                                            | |                              |
                                                            | |        COGUARD ENGINE        |
                                                            +-+                              |
                                                              |                              |
                                                              +------------------------------+
```


## LLM experiments by component

### Extraction of security relevant parameters in [C1]

The goal of the initial experimentation was to ask the LLM model what
the security relevant configuration parameters were in Apache Spark.

#### Description of the experimentation

The messages chosen for the GPT model were

```
messages=[
     {"role": "system", "content": "You are an assistant that is a cybersecurity expert and knows their configuration files. Your response here should be a JSON list of strings."},
     {"role": "user", "content": "Using the documentation of Apache Spark, which configuration parameters are relevant from a security perspective?."}
]
```

When using `gpt-3.5-turbo`, the resulting output was

```json
[
    "spark.authenticate",
    "spark.ssl.enabled",
    "spark.ssl.keyStore",
    "spark.ssl.keyStorePassword",
    "spark.ssl.trustStore",
    "spark.ssl.trustStorePassword",
    "spark.acls.enable",
    "spark.ui.acls.enable",
    "spark.ui.view.acls",
    "spark.ui.view.acls.groups",
    "spark.hadoop.fs.s3a.access.key",
    "spark.hadoop.fs.s3a.secret.key"
]
```

When using `gpt-4`, the output was producing 2.5x more valid parameters but still not good
enough when considering the manual extraction of [Appendix A](##apendix-a).

```json
[
  "spark.acls.enable",
  "spark.ui.reverseProxy",
  "spark.ui.reverseProxyUrl",
  "spark.ui.filters",
  "spark.ui.view.acls",
  "spark.ui.view.acls.groups",
  "spark.admin.acls",
  "spark.admin.acls.groups",
  "spark.modify.acls",
  "spark.modify.acls.groups",
  "spark.hadoop.yarn.timeline-service.enabled",
  "spark.ssl.enabled",
  "spark.ssl.protocol",
  "spark.ssl.factory",
  "spark.ssl.storesSecretProvider",
  "spark.ssl.keyPassword",
  "spark.ssl.keyStore",
  "spark.ssl.keyStorePassword",
  "spark.ssl.keyStoreType",
  "spark.ssl.trustStore",
  "spark.ssl.trustStorePassword",
  "spark.ssl.trustStoreType",
  "spark.ssl.enabledAlgorithms",
  "spark.redaction.regex",
  "spark.network.crypto.enabled",
  "spark.network.crypto.saslFallback",
  "spark.authenticate",
  "spark.authenticate.enableSaslEncryption",
  "spark.authenticate.secret"
]
```

This means, with simple requests, we are achieving less than 40%
coverage with respect to the numbers of parameters we have seen in
[Appendix A](##appendix-a), which is not good enough.

In a similar fashion, also ask for all configuration
parameters that the LLM model may know, and the result is similarly
low coverage-wise.

For the data from the experimentation, please consider the following
two files that contain the summary of the calls:

- [File 1](./experiments/first_round_prompts/tmp_output.txt)
- [File 2](./experiments/first_round_prompts/tmp_output_2.txt)

The next experiment that we did was using additional assistant
messages with previous responses, and trying to see if the model would
produce more output this way.

An initial prompt idea in that direction was

```
messages=[
     {"role": "system", "content": "You are a helpful assistant
     outputting stuff as JSON and knowing things about
     cybersecurity. Ensure that each string in a list is unique and
     that strings are sorted alphabetically."},
     {"role": "user", "content": "Please list all configuration
     parameters of Apache Spark that are relevant to security. Act as
     if I am continuously asking for more parameters (up to 10 times)
     and keep adding to the list new parameters that weren't there
     before. Make sure to have at least 10 parameters with each
     request. Output ONLY the final list after the 10th iteration in the end."}
]
```

This type of request did, for GPT-4, created only 2 more parameters
(27 vs. 29). See [File 3](./experiments/first_round_prompts/tmp_output_3.txt) for reference.

Even by adding `user`-`assistant`-`user` tuning in the API by
repeatedly asking

```
"Please list security relevant Apache spark configuration parameters
that you have not found yet in previous prompt answers to me. Include
in the output list all previously found configuration parameters."
```

while supplying the previous answer via a message with role
`assistant` did capture in the end less parameters (24 vs 29). I.e., it converged at the previous
set of identified parameters.

The code to do this in a loop can be found in this [Python
script](./experiments/repetitive_ask_and_re_ask_more_configs.py), and the ouput can
be found [here](./experiments/output_repetitive_ask_and_re_ask.txt).

#### Conclusion on the extraction of configuration parameters via LLMs

It appears that the direct use of the GPT models to identify security
relevant, or even just any configuration parameters, of Apache Spark
configurations, can be deemed as impractical due to the low
coverage. This portion of the extraction has to be done using
different ways, including some natural language processing directly
from the document.

### Identification of defaults and recommended values [C2]

We have been using our list of security relevant configuration
parameters as per [this
summary](https://spark.apache.org/docs/latest/security.html), and
checked if GPT-4 could, if provided with a parameter, identify the
default parameter and the recommended one. For simplicity, we are only
looking at `KEY_SHOULD[_NOT]_EXIST` and `IS[_NOT]` as a operators.

The system message was described as following:

```
You are a cybersecurity assistant. You are being presented a
configuration parameter by the user, and respond with the name, its
default value, and what the value should be in a secure
environment. If the parameter should just be set for a secure
environment, put KEY_SHOULD_EXIST as a secure value. The output format
should be JSON.
```

The final user question was simply the Apache Spark configuration
parameter. We did the input/output in form of a script, which you can
find [here](./experiments/extract_info_per_single_parameter.py).

The following table juxtaposes the identification of the default and
recommended parameters:

| Config parameter                              | default value (actual) | default value (openai) | recommended value (actual)                                                                                                                            | recommended value (openai)   |
|-----------------------------------------------|------------------------|------------------------|-------------------------------------------------------------------------------------------------------------------------------------------------------|------------------------------|
| `spark.yarn.shuffle.server.recovery.disabled` | false                  | false                  | true                                                                                                                                                  | true                         |
| `spark.authenticate`                          | false                  | false                  | true                                                                                                                                                  | true                         |
| `spark.authenticate.secret`                   | null                   | null                   | KEY_SHOULD_EXIST                                                                                                                                      | KEY_SHOULD_EXIST             |
| `spark.authenticate.secret.file`              | null                   | null                   | KEY_SHOULD_EXIST                                                                                                                                      | KEY_SHOULD_EXIST             |
| `spark.authenticate.secret.driver.file`       | null                   | null                   | KEY_SHOULD_EXIST                                                                                                                                      | KEY_SHOULD_EXIST             |
| `spark.authenticate.secret.executor.file`     | null                   | null                   | KEY_SHOULD_EXIST                                                                                                                                      | KEY_SHOULD_EXIST             |
| `spark.network.crypto.enabled`                | false                  | false                  | true                                                                                                                                                  | true                         |
| `spark.network.crypto.saslFallback`           | true                   | true                   | true or false                                                                                                                                         | false                        |
| `spark.authenticate.enableSaslEncryption`     | false                  | false                  | true                                                                                                                                                  | true                         |
| `spark.network.sasl.serverAlwaysEncrypt`      | false                  | false                  | true                                                                                                                                                  | true                         |
| `spark.io.encryption.enabled`                 | false                  | false                  | true                                                                                                                                                  | true                         |
| `spark.io.encryption.keySizeBits`             | 128                    | 128                    | 256                                                                                                                                                   | 256                          |
| `spark.io.encryption.keygen.algorithm`        | HmacSHA1               | HmacSHA1               | HmacSHA256                                                                                                                                            | HmacSHA256                   |
| `spark.ui.allowFramingFrom`                   | SAMEORIGIN             | null                   | SAMEORIGIN                                                                                                                                            | null                         |
| `spark.ui.filters`                            | null                   | null                   | KEY_SHOULD_EXIST                                                                                                                                      | KEY_SHOULD_EXIST             |
| `spark.acls.enable`                           | false                  | false                  | true                                                                                                                                                  | true                         |
| `spark.admin.acls`                            | null                   | null                   | KEY_SHOULD_EXIST                                                                                                                                      | KEY_SHOULD_EXIST             |
| `spark.admin.acls.groups`                     | null                   | null                   | KEY_SHOULD_EXIST                                                                                                                                      | KEY_SHOULD_EXIST             |
| `spark.modify.acls`                           | null                   | null                   | KEY_SHOULD_EXIST                                                                                                                                      | KEY_SHOULD_EXIST             |
| `spark.modify.acls.groups`                    | null                   | null                   | KEY_SHOULD_EXIST                                                                                                                                      | KEY_SHOULD_EXIST             |
| `spark.ui.view.acls`                          | null                   | null                   | KEY_SHOULD_EXIST                                                                                                                                      | KEY_SHOULD_EXIST             |
| `spark.ui.view.acls.groups`                   | null                   | null                   | KEY_SHOULD_EXIST                                                                                                                                      | KEY_SHOULD_EXIST             |
| `spark.user.groups.mapping`                   | null                   | null                   | KEY_SHOULD_EXIST                                                                                                                                      | KEY_SHOULD_EXIST             |
| `spark.history.ui.acls.enable`                | false                  | false                  | true                                                                                                                                                  | true                         |
| `spark.history.ui.admin.acls`                 | null                   | null                   | KEY_SHOULD_EXIST                                                                                                                                      | KEY_SHOULD_EXIST             |
| `spark.history.ui.admin.acls.groups`          | null                   | null                   | KEY_SHOULD_EXIST                                                                                                                                      | KEY_SHOULD_EXIST             |
| `spark.ssl.enabled`                           | false                  | false                  | true                                                                                                                                                  | true                         |
| `spark.ssl.port`                              | null                   | null                   | KEY_SHOULD_EXIST                                                                                                                                      | KEY_SHOULD_EXIST             |
| `spark.ssl.enabledAlgorithms`                 | null                   | null                   | TLS_DHE_DSS_WITH_AES_128_GCM_SHA256,TLS_ECDHE_ECDSA_WITH_AES_128_GCM_SHA256,TLS_DHE_RSA_WITH_AES_128_GCM_SHA256,TLS_ECDHE_RSA_WITH_AES_128_GCM_SHA256 | TLSv1.2,TLSv1.3              |
| `spark.ssl.keyPassword`                       | null                   | null                   | KEY_SHOULD_EXIST                                                                                                                                      | KEY_SHOULD_EXIST             |
| `spark.ssl.keyStore`                          | null                   | null                   | KEY_SHOULD_EXIST                                                                                                                                      | KEY_SHOULD_EXIST             |
| `spark.ssl.keyStorePassword`                  | null                   | null                   | KEY_SHOULD_EXIST                                                                                                                                      | KEY_SHOULD_EXIST             |
| `spark.ssl.keyStoreType`                      | JKS                    | JKS                    | JKS                                                                                                                                                   | JKS                          |
| `spark.ssl.protocol`                          | null                   | null                   | TLSv1.2                                                                                                                                               | TLS                          |
| `spark.ssl.needClientAuth`                    | false                  | false                  | true                                                                                                                                                  | true                         |
| `spark.ssl.trustStore`                        | null                   | null                   | KEY_SHOULD_EXIST                                                                                                                                      | KEY_SHOULD_EXIST             |
| `spark.ssl.trustStorePassword`                | null                   | null                   | KEY_SHOULD_EXIST                                                                                                                                      | KEY_SHOULD_EXIST             |
| `spark.ssl.trustStoreType`                    | JKS                    | JKS                    | JKS                                                                                                                                                   | JKS                          |
| `spark.ssl.ui.enabled`                        | false                  | false                  | true                                                                                                                                                  | true                         |
| `spark.ssl.ui.port`                           | null                   | null                   | KEY_SHOULD_EXIST                                                                                                                                      | KEY_SHOULD_EXIST             |
| `spark.ssl.ui.enabledAlgorithms`              | null                   | null                   | TLS_RSA_WITH_AES_128_CBC_SHA                                                                                                                          | KEY_SHOULD_EXIST             |
| `spark.ssl.ui.keyPassword`                    | null                   | null                   | KEY_SHOULD_EXIST                                                                                                                                      | KEY_SHOULD_EXIST             |
| `spark.ssl.ui.keyStore`                       | null                   | null                   | KEY_SHOULD_EXIST                                                                                                                                      | KEY_SHOULD_EXIST             |
| `spark.ssl.ui.keyStorePassword`               | null                   | null                   | KEY_SHOULD_EXIST                                                                                                                                      | KEY_SHOULD_EXIST             |
| `spark.ssl.ui.keyStoreType`                   | JKS                    | JKS                    | JKS                                                                                                                                                   | PKCS12                       |
| `spark.ssl.ui.protocol`                       | null                   | TLS                    | TLSv1.2                                                                                                                                               | TLSv1.2                      |
| `spark.ssl.ui.needClientAuth`                 | false                  | false                  | true                                                                                                                                                  | true                         |
| `spark.ssl.ui.trustStore`                     | null                   | null                   | KEY_SHOULD_EXIST                                                                                                                                      | KEY_SHOULD_EXIST             |
| `spark.ssl.ui.trustStorePassword`             | null                   | null                   | KEY_SHOULD_EXIST                                                                                                                                      | KEY_SHOULD_EXIST             |
| `spark.ssl.ui.trustStoreType`                 | JKS                    | null                   | JKS                                                                                                                                                   | JKS                          |
| `spark.ssl.standalone.enabled`                | false                  | false                  | true                                                                                                                                                  | true                         |
| `spark.ssl.standalone.port`                   | null                   | -1                     | KEY_SHOULD_EXIST                                                                                                                                      | KEY_SHOULD_EXIST             |
| `spark.ssl.standalone.enabledAlgorithms`      | null                   | null                   | TLS_DHE_DSS_WITH_AES_128_GCM_SHA256,TLS_ECDHE_ECDSA_WITH_AES_128_GCM_SHA256,TLS_DHE_RSA_WITH_AES_128_GCM_SHA256,TLS_ECDHE_RSA_WITH_AES_128_GCM_SHA256 | TLS_RSA_WITH_AES_128_CBC_SHA |
| `spark.ssl.standalone.keyPassword`            | null                   | null                   | KEY_SHOULD_EXIST                                                                                                                                      | KEY_SHOULD_EXIST             |
| `spark.ssl.standalone.keyStore`               | null                   | null                   | KEY_SHOULD_EXIST                                                                                                                                      | KEY_SHOULD_EXIST             |
| `spark.ssl.standalone.keyStorePassword`       | null                   | null                   | KEY_SHOULD_EXIST                                                                                                                                      | KEY_SHOULD_EXIST             |
| `spark.ssl.standalone.keyStoreType`           | JKS                    | JKS                    | JKS                                                                                                                                                   | PKCS12                       |
| `spark.ssl.standalone.protocol`               | null                   | TLSv1.1                | TLSv1.2                                                                                                                                               | TLSv1.2                      |
| `spark.ssl.standalone.needClientAuth`         | false                  | false                  | true                                                                                                                                                  | true                         |
| `spark.ssl.standalone.trustStore`             | null                   | null                   | KEY_SHOULD_EXIST                                                                                                                                      | KEY_SHOULD_EXIST             |
| `spark.ssl.standalone.trustStorePassword`     | null                   | null                   | KEY_SHOULD_EXIST                                                                                                                                      | KEY_SHOULD_EXIST             |
| `spark.ssl.standalone.trustStoreType`         | JKS                    | JKS                    | JKS                                                                                                                                                   | PKCS12                       |
| `spark.ssl.historyServer.enabled`             | false                  | false                  | true                                                                                                                                                  | true                         |
| `spark.ssl.historyServer.port`                | null                   | null                   | KEY_SHOULD_EXIST                                                                                                                                      | KEY_SHOULD_EXIST             |
| `spark.ssl.historyServer.enabledAlgorithms`   | null                   | null                   | TLS_DHE_DSS_WITH_AES_128_GCM_SHA256,TLS_ECDHE_ECDSA_WITH_AES_128_GCM_SHA256,TLS_DHE_RSA_WITH_AES_128_GCM_SHA256,TLS_ECDHE_RSA_WITH_AES_128_GCM_SHA256 | TLSv1.2,TLSv1.3              |
| `spark.ssl.historyServer.keyPassword`         | null                   | null                   | KEY_SHOULD_EXIST                                                                                                                                      | KEY_SHOULD_EXIST             |
| `spark.ssl.historyServer.keyStore`            | null                   | null                   | KEY_SHOULD_EXIST                                                                                                                                      | KEY_SHOULD_EXIST             |
| `spark.ssl.historyServer.keyStorePassword`    | null                   | null                   | KEY_SHOULD_EXIST                                                                                                                                      | KEY_SHOULD_EXIST             |
| `spark.ssl.historyServer.keyStoreType`        | null                   | null                   | JKS                                                                                                                                                   | JKS                          |
| `spark.ssl.historyServer.protocol`            | null                   | TLS                    | TLSv1.2                                                                                                                                               | TLSv1.2                      |
| `spark.ssl.historyServer.needClientAuth`      | false                  | false                  | true                                                                                                                                                  | true                         |
| `spark.ssl.historyServer.trustStore`          | null                   | null                   | KEY_SHOULD_EXIST                                                                                                                                      | KEY_SHOULD_EXIST             |
| `spark.ssl.historyServer.trustStorePassword`  | null                   | null                   | KEY_SHOULD_EXIST                                                                                                                                      | KEY_SHOULD_EXIST             |
| `spark.ssl.historyServer.trustStoreType`      | null                   | null                   | JKS                                                                                                                                                   | JKS                          |
| `spark.ui.xXssProtection`                     | 1; mode=block          | 1; mode=block          | 1; mode=block                                                                                                                                         | 1; mode=block                |
| `spark.ui.xContentTypeOptions.enabled`        | true                   | false                  | true                                                                                                                                                  | true                         |
| `spark.ui.strictTransportSecurity`            | null                   | false                  | KEY_SHOULD_EXIST                                                                                                                                      | true                         |

A couple of observations here:
- GPT-4, without being told anything about it, knows well that
  `HMACSHA1` is not a good choice, and should be replaced by
  `HMACSHA256` for better security.
- It appears that GPT-4 seems to not be able to distinguish between
  the times when a parameter only looks for a
  cryptographic protocol such as TLS and the times when a parameter
  asks for a cipher-suite such as one identified by the naming scheme
  `TLS_ECDHE_RSA_WITH_AES_128_GCM_SHA256`. You can see it in the
  `*.enabledAlgorithms` rows, where the suite is often just identified
  via the protocol.

#### Conclusion on the identification of the recommended/default parameters via LLMs

The default value deduction accuracy was amazing and exceeded 90%. For
the recommended value, the accuracy has been ~87%, just from a simple
prompt. This is very promising, and with additional training and
teaching to look for the right thing, the correct value may be
possible to be lifted to a much higher threshold.

### Translation of identified parameters and recommended values into rules [C3]

#### Creating the JSON with the policy

As an initial first step, we described our policy JSON format to the
engine in the system message, and proceeded to let the user provide
the outputs of [C2].

Since the output format is proprietary to CoGuard, we will omit the
exact LLM description from this report.

The verbosity came with some initial errors that were adjusted in the
wording. these included:
- `null` values, i.e. instead of omitting the key, it was set to
  `null`, which is considered different in the JSON schema than
  omission.
- interpolation of final values to boolean or numbers; this is
  generally fine, but our schema requires the values and defaults to be strictly strings.

After adjustments for these small edge cases, we have a 98.7% schema
correctness of the produced rules.

Hence, as an intermediate result, one can say that the generation of
the rules, from a perspective of pure schema-adherence, was a success.

When it comes to the correctness of the content, we have observed only
a few one-offs, which we are listing here:
- 7 times the LLM failed to provide a source URL, and one time it was
  an invalid one.
- There were 5 errors of the kind where a `null` has been suggested
  as a valid value in the text, which is not right.
- There were 4 cases where the documentation string stated a wrong
  statement.

We will discuss the correctness of the generated policy DSL code in a subsequent
section, as they require us to generate the appropriate test files.

### Generating test files [C4]

We have also created instructions to generate the test files based on
the JSON rules generated in [C3].

Again, these test files have been generated using prompts directly to
the LLM with a descriptive language.

After examining the test files, we were counting how many test files
have actually been correctly created.

The adherence to the specific configuration file type
can be determined to be at 94.15%. The main mistake that the model did
was to split up the keys at the `.` and create some form of JSON for it.

The correctness of the settings inside the generated test files can be
put as 83.8%.

Again, these are overall very good results for a text-based only first
try. One may be able to get better results with a lot of fine-tuning
there.


#### Correctness of the rules when tested against the test files

After correcting the errors examined in the test files in the previous
subsection, we ran the test suite with the generated rules in the
engine.

It appeared that the correctness of the generated rules was at 96.8%,
so that is amazing.

## Costs

The costs running the scripts were surprisingly low. Assuming [C1] is
done using a different methodology, the OpenAI API costs were limited
at <$5 per complete run of [C2]-[C4].

## Overall conclusion of applicability of LLMs to the different components

While [C1] showed very sobering results out of the box, all the other
components showed to be practical out of the box with little to no
additional fine-tuning.

Hence, as a first result, we can say that the application of LLMs for
generating new rules and adding new services is a viable approach to
reduce developer time.

## Future work

The future work of this research can be summarized in the following
way:

- Create a viable way to extract configuration parameters from a
  provided document, i.e. the architecture piece [C1] in our general
  architecture description.
- Apply the pipeline to 10 further software products and refine the
  steps each time to achieve a higher accuracy.
- Expand the complexity of the rules, and eventually create some which
  take interdependence of services into account.

# Appendices

## Appendix A

The following parameters were identified by the CoGuard team by hand
as relevant from a security point of view.

- `spark.yarn.shuffle.server.recovery.disabled`
- `spark.authenticate`
- `spark.authenticate.secret`
- `spark.authenticate.secret.file`
- `spark.authenticate.secret.driver.file`
- `spark.authenticate.secret.executor.file`
- `spark.network.crypto.enabled`
- `spark.network.crypto.config.*`
- `spark.network.crypto.saslFallback`
- `spark.authenticate.enableSaslEncryption`
- `spark.network.sasl.serverAlwaysEncrypt`
- `spark.io.encryption.enabled`
- `spark.io.encryption.keySizeBits`
- `spark.io.encryption.keygen.algorithm`
- `spark.io.encryption.commons.config.*`
- `spark.ui.allowFramingFrom`
- `spark.ui.filters`
- `spark.acls.enable`
- `spark.admin.acls`
- `spark.admin.acls.groups`
- `spark.modify.acls`
- `spark.modify.acls.groups`
- `spark.ui.view.acls`
- `spark.ui.view.acls.groups`
- `spark.user.groups.mapping`
- `spark.history.ui.acls.enable`
- `spark.history.ui.admin.acls`
- `spark.history.ui.admin.acls.groups`
- `spark.ssl.enabled`
- `spark.ssl.port`
- `spark.ssl.enabledAlgorithms`
- `spark.ssl.keyPassword`
- `spark.ssl.keyStore`
- `spark.ssl.keyStorePassword`
- `spark.ssl.keyStoreType`
- `spark.ssl.protocol`
- `spark.ssl.needClientAuth`
- `spark.ssl.trustStore`
- `spark.ssl.trustStorePassword`
- `spark.ssl.trustStoreType`
- `spark.ssl.ui.enabled`
- `spark.ssl.ui.port`
- `spark.ssl.ui.enabledAlgorithms`
- `spark.ssl.ui.keyPassword`
- `spark.ssl.ui.keyStore`
- `spark.ssl.ui.keyStorePassword`
- `spark.ssl.ui.keyStoreType`
- `spark.ssl.ui.protocol`
- `spark.ssl.ui.needClientAuth`
- `spark.ssl.ui.trustStore`
- `spark.ssl.ui.trustStorePassword`
- `spark.ssl.ui.trustStoreType`
- `spark.ssl.standalone.enabled`
- `spark.ssl.standalone.port`
- `spark.ssl.standalone.enabledAlgorithms`
- `spark.ssl.standalone.keyPassword`
- `spark.ssl.standalone.keyStore`
- `spark.ssl.standalone.keyStorePassword`
- `spark.ssl.standalone.keyStoreType`
- `spark.ssl.standalone.protocol`
- `spark.ssl.standalone.needClientAuth`
- `spark.ssl.standalone.trustStore`
- `spark.ssl.standalone.trustStorePassword`
- `spark.ssl.standalone.trustStoreType`
- `spark.ssl.historyServer.enabled`
- `spark.ssl.historyServer.port`
- `spark.ssl.historyServer.enabledAlgorithms`
- `spark.ssl.historyServer.keyPassword`
- `spark.ssl.historyServer.keyStore`
- `spark.ssl.historyServer.keyStorePassword`
- `spark.ssl.historyServer.keyStoreType`
- `spark.ssl.historyServer.protocol`
- `spark.ssl.historyServer.needClientAuth`
- `spark.ssl.historyServer.trustStore`
- `spark.ssl.historyServer.trustStorePassword`
- `spark.ssl.historyServer.trustStoreType`
- `spark.ui.xXssProtection`
- `spark.ui.xContentTypeOptions.enabled`
- `spark.ui.strictTransportSecurity`

## Appendix B

The operators currently supported by CoGuard for simple
predicate-driven rules are:

- `KEY_SHOULD_EXIST`
- `KEY_SHOULD_NOT_EXIST`
- `IS`
- `IS_NOT`
- `ALL`
- `CONTAINS`
- `CONTAINS_NOT`
- `MATCHES`
- `MATCHES_NOT`
- `MATCHES_SOME`
- `MATCHES_NONE`
- `MATCHES_ALL`
- `GREATER`
- `SMALLER`
