#!/bin/bash

# Activate virtual env.
. /home/fedecarles/legalminer/venv/bin/activate

# Run scraper
 python3 /home/fedecarles/legalminer/cij_scrape.py

# Update index
# python3 manage.py update_index \-\-age\=2


