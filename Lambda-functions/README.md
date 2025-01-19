Steps to use the lambda functions:

lambda-orchestrator steps to follow:
[text](https://developers.facebook.com/docs/graph-api/guides/error-handling/)
(my_virtual_env) sparrow@LAPTOP-CM1N29F4:~/Colmena-AI$ pip show langchain-aws
Name: langchain-aws
Version: 0.2.10
Summary: An integration package connecting AWS and LangChain
Home-page: https://github.com/langchain-ai/langchain-aws
Author:
Author-email:
License: MIT
Location: /home/sparrow/Colmena-AI/my_virtual_env/lib/python3.10/site-packages
Requires: boto3, langchain-core, numpy, pydantic
Required-by:

(my_virtual_env) sparrow@LAPTOP-CM1N29F4:~/Colmena-AI$ deactivate
sparrow@LAPTOP-CM1N29F4:~/Colmena-AI/my_virtual_env/lib/python3.10/site-packages$ cd my_virtual_env/lib/python3.10/site-packages
sparrow@LAPTOP-CM1N29F4:~/Colmena-AI/my_virtual_env/lib/python3.10/site-packages$ zip -r ../../../../NAME_OF_THE_ZIP.zip .
sparrow@LAPTOP-CM1N29F4:~/Colmena-AI/my_virtual_env/lib/python3.10/site-packages$ cd ../../../../
sparrow@LAPTOP-CM1N29F4:~/Colmena-AI$
sparrow@LAPTOP-CM1N29F4:~/Colmena-AI$ zip lambda-orchestrator_v2.zip ./Lambda-functions/lambda-orchestrator/orchestrator.py ./Lambd
a-functions/lambda-orchestrator/lambda_function.py ./Lambda-functions/lambda-orchestrator/prompt_templates.py ./Lambda-functions/la
mbda-orchestrator/s3_checkpointer.py
