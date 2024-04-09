#!/bin/python

import json
from openai import OpenAI

def main(spark_parameter):
    """
    The main function. We want to consume a spark parameter, and output the name,
    the default value, and the value as it should be set for a secure environment.
    """
    client = OpenAI()
    system_message = "You are a cybersecurity assistant. You are being presented a configuration parameter by the user, and respond with the name, its default value, and what the value should be in a secure environment. If the parameter should just be set for a secure environment, put KEY_SHOULD_EXIST as a secure value. The output format should be JSON."
    user_message = spark_parameter
    completion = client.chat.completions.create(
        model = "gpt-4",
        messages = [
            {"role": "system", "content": system_message},
            {"role": "user", "content": user_message},
        ]
    )
    print(completion.choices[0].message.content)

if __name__ == '__main__':
    config_params = [
        "spark.yarn.shuffle.server.recovery.disabled",
        "spark.authenticate",
        "spark.authenticate.secret",
        "spark.authenticate.secret.file",
        "spark.authenticate.secret.driver.file",
        "spark.authenticate.secret.executor.file",
        "spark.network.crypto.enabled",
        "spark.network.crypto.saslFallback",
        "spark.authenticate.enableSaslEncryption",
        "spark.network.sasl.serverAlwaysEncrypt",
        "spark.io.encryption.enabled",
        "spark.io.encryption.keySizeBits",
        "spark.io.encryption.keygen.algorithm",
        "spark.ui.allowFramingFrom",
        "spark.ui.filters",
        "spark.acls.enable",
        "spark.admin.acls",
        "spark.admin.acls.groups",
        "spark.modify.acls",
        "spark.modify.acls.groups",
        "spark.ui.view.acls",
        "spark.ui.view.acls.groups",
        "spark.user.groups.mapping",
        "spark.history.ui.acls.enable",
        "spark.history.ui.admin.acls",
        "spark.history.ui.admin.acls.groups",
        "spark.ssl.enabled",
        "spark.ssl.port",
        "spark.ssl.enabledAlgorithms",
        "spark.ssl.keyPassword",
        "spark.ssl.keyStore",
        "spark.ssl.keyStorePassword",
        "spark.ssl.keyStoreType",
        "spark.ssl.protocol",
        "spark.ssl.needClientAuth",
        "spark.ssl.trustStore",
        "spark.ssl.trustStorePassword",
        "spark.ssl.trustStoreType",
        "spark.ssl.ui.enabled",
        "spark.ssl.ui.port",
        "spark.ssl.ui.enabledAlgorithms",
        "spark.ssl.ui.keyPassword",
        "spark.ssl.ui.keyStore",
        "spark.ssl.ui.keyStorePassword",
        "spark.ssl.ui.keyStoreType",
        "spark.ssl.ui.protocol",
        "spark.ssl.ui.needClientAuth",
        "spark.ssl.ui.trustStore",
        "spark.ssl.ui.trustStorePassword",
        "spark.ssl.ui.trustStoreType",
        "spark.ssl.standalone.enabled",
        "spark.ssl.standalone.port",
        "spark.ssl.standalone.enabledAlgorithms",
        "spark.ssl.standalone.keyPassword",
        "spark.ssl.standalone.keyStore",
        "spark.ssl.standalone.keyStorePassword",
        "spark.ssl.standalone.keyStoreType",
        "spark.ssl.standalone.protocol",
        "spark.ssl.standalone.needClientAuth",
        "spark.ssl.standalone.trustStore",
        "spark.ssl.standalone.trustStorePassword",
        "spark.ssl.standalone.trustStoreType",
        "spark.ssl.historyServer.enabled",
        "spark.ssl.historyServer.port",
        "spark.ssl.historyServer.enabledAlgorithms",
        "spark.ssl.historyServer.keyPassword",
        "spark.ssl.historyServer.keyStore",
        "spark.ssl.historyServer.keyStorePassword",
        "spark.ssl.historyServer.keyStoreType",
        "spark.ssl.historyServer.protocol",
        "spark.ssl.historyServer.needClientAuth",
        "spark.ssl.historyServer.trustStore",
        "spark.ssl.historyServer.trustStorePassword",
        "spark.ssl.historyServer.trustStoreType",
        "spark.ui.xXssProtection",
        "spark.ui.xContentTypeOptions.enabled",
        "spark.ui.strictTransportSecurity",
    ]
    for i in config_params:
        main(i)
