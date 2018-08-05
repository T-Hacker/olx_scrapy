#!/bin/bash
scrapy crawl olx -t json --nolog -o - > /home/pedro/projects/olx_viewer/public/feed.json

