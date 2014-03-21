# -*- coding: utf-8 -*-

from opendash import app

from opendash.views import home
from opendash.views import login
from opendash.views import profile
from opendash.views import report_edit
from opendash.views import endpoint

if __name__ == '__main__':
     app.run(debug=True)
