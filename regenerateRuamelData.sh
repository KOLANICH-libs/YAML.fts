#!/usr/bin/env sh

rm -rf ./ruamel.yaml.data
7za x -oruamel.yaml.data ./ruamel.yaml.data.zip
./ruamelYamlDatasetConvertor.py
