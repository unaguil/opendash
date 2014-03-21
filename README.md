OpenDASH
========

SPARQL Endpoint Visualization Tool


Installation
------------

1. **Install required libraries**

		pip install -r requirements.txt

2. **Create database model**

		python opendash/model/opendash_model.py

3. **Launch local server with test data** 

		cd testing
		bash launch_server.sh

4. **Run OpenDASH server (in main directory)**

		python runserver.py
		
Usage
-----

1. **Connect browser to URL** 

      http://127.0.0.1:5000/
            
2. **Login**

      1. Log as *admin*/*admin* to access de admin view and modify users and other data.
      1. Log as *test*/*test* for testing account.



