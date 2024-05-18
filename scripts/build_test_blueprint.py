#!/bin/env python3

import sys
from factory_designer_gtk.widgets import build_test_blueprint

bp = build_test_blueprint()
# bp.factory.simulate()
bp.save(sys.argv[1])
