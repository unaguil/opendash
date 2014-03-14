# -*- coding: utf-8 -*-

from opendash import app

from opendash.views import login
from opendash.views import profile
from opendash.views import report_edit
from opendash.views import endpoint

app.run(debug=True)