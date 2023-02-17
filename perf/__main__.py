""" CLI usage of perf. """

import sys

from . import main


if len(sys.argv) == 2:
    main(None, int(sys.argv[1]))
else:
    main()
