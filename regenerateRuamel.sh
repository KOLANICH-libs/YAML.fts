#!/usr/bin/env sh

rm -rf ./ruamel.yaml
7za x -oruamel.yaml ./ruamel.yaml.zip
./ruamelYamlDatasetConvertor.py
