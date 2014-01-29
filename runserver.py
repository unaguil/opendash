# -*- coding: utf-8 -*-

from opendash import app

from opendash.views import login
from opendash.views import edit
from opendash.views import profile

app.run(debug=True)