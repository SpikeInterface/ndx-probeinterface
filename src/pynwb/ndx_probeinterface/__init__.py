import os
from pynwb import load_namespaces, get_class

# Set path of the namespace.yaml file to the expected install location
ndx_probeinterface_specpath = os.path.join(
    os.path.dirname(__file__),
    'spec',
    'ndx-probeinterface.namespace.yaml'
)

# If the extension has not been installed yet but we are running directly from
# the git repo
if not os.path.exists(ndx_probeinterface_specpath):
    ndx_probeinterface_specpath = os.path.abspath(os.path.join(
        os.path.dirname(__file__),
        '..', '..', '..',
        'spec',
        'ndx-probeinterface.namespace.yaml'
    ))

# Load the namespace
load_namespaces(ndx_probeinterface_specpath)

# TODO: import your classes here or define your class using get_class to make
# them accessible at the package level
Probe = get_class('Probe', 'ndx-probeinterface')
Shank = get_class('Shank', 'ndx-probeinterface')
ContactTable = get_class('ContactTable', 'ndx-probeinterface')


# Add custom constructors
from .io import from_probe, from_probegroup, to_probeinterface
Probe.from_probe = from_probe
Probe.from_probegroup = from_probegroup
Probe.to_probeinterface = to_probeinterface