import pytest
import datetime
import numpy as np

import probeinterface as pi

from pynwb import NWBHDF5IO, NWBFile
from pynwb.core import DynamicTableRegion
from pynwb.device import Device
from pynwb.ecephys import ElectrodeGroup
from pynwb.file import ElectrodeTable as get_electrode_table
from pynwb.testing import TestCase, remove_test_file, AcquisitionH5IOMixin

from ndx_probeinterface import Probe, Shank, ContactTable


def set_up_nwbfile():
    nwbfile = NWBFile(
        session_description='session_description',
        identifier='identifier',
        session_start_time=datetime.datetime.now(datetime.timezone.utc)
    )
    return nwbfile


def create_single_shank_probe():
    probe = pi.generate_linear_probe()
    probe.annotate(name="Single-shank")
    probe.set_contact_ids([f"c{i}" for i in range(probe.get_contact_count())])
    return probe


def create_multi_shank_probe():
    probe = pi.generate_multi_shank()
    probe.annotate(name="Multi-shank")
    probe.set_contact_ids([f"cm{i}" for i in range(probe.get_contact_count())])
    return probe


def create_probe_group():
    probe0 = create_single_shank_probe()
    probe1 = create_multi_shank_probe()

    pg = pi.ProbeGroup()
    pg.add_probe(probe0)
    pg.add_probe(probe1)
    return pg


class TestProbeConstructors(TestCase):

    def setUp(self):
        """Set up an NWB file. Necessary because TetrodeSeries requires references to electrodes."""
        self.nwbfile = set_up_nwbfile()
        self.probe = create_single_shank_probe()
        self.probe1 = create_multi_shank_probe()
        self.probegroup = create_probe_group()
        

    def test_constructor_from_probe_single_shank(self):
        """Test that the constructor for TetrodeSeries sets values as expected."""

        probe = self.probe
        device = Probe.from_probe(probe)
        # assert correct objects
        self.assertIsInstance(device, Device)
        self.assertIsInstance(device, Probe)

        # assert correct attributes
        self.assertEqual(len(device.shanks), 1)

        # properties
        shank_names = list(device.shanks.keys())
        contact_table = device.shanks[shank_names[0]].contact_table
        probe_array = probe.to_numpy()
        np.testing.assert_array_equal(contact_table["contact_position"][:],
                                      probe.contact_positions)
        np.testing.assert_array_equal(contact_table["contact_shape"][:],
                                      probe_array["contact_shapes"])

        # set channel indices
        device_channel_indices = np.arange(probe.get_contact_count())
        probe.set_device_channel_indices(device_channel_indices)
        device_w_indices = Probe.from_probe(probe)
        shank_names = list(device.shanks.keys())
        contact_table = device_w_indices.shanks[shank_names[0]].contact_table
        np.testing.assert_array_equal(contact_table["device_channel_index"][:],
                                      device_channel_indices)

    def test_constructor_from_probe_multi_shank(self):
        """Test that the constructor for TetrodeSeries sets values as expected."""

        probe = self.probe1
        device = Probe.from_probe(probe)
        # assert correct objects
        self.assertIsInstance(device, Device)
        self.assertIsInstance(device, Probe)

        # assert correct attributes
        self.assertEqual(len(device.shanks), 2)

        # properties
        shank_names = list(device.shanks.keys())
        probe_array = probe.to_numpy()

        # set channel indices
        device_channel_indices = np.arange(self.probe.get_contact_count())
        probe.set_device_channel_indices(device_channel_indices)

        for i_s, shank_name in enumerate(shank_names):
            contact_table = device.shanks[shank_name].contact_table
            pi_shank = probe.get_shanks()[i_s]
            np.testing.assert_array_equal(contact_table["contact_position"][:],
                                          probe.contact_positions[pi_shank.get_indices()])
            np.testing.assert_array_equal(contact_table["contact_shape"][:],
                                          probe_array["contact_shapes"][pi_shank.get_indices()])

            np.testing.assert_array_equal(contact_table["device_channel_index"][:],
                                          device_channel_indices)
        
    def test_constructor_from_probegroup(self):
        """Test that the constructor for TetrodeSeries sets values as expected."""

        probegroup = self.probegroup
        devices = Probe.from_probegroup(probegroup)
        probes = probegroup.probes

        for i, device in enumerate(devices):
            probe = probes[i]
            # assert correct objects
            self.assertIsInstance(device, Device)
            self.assertIsInstance(device, Probe)

            # assert correct attributes
            self.assertEqual(len(device.shanks), 2)

            # properties
            shank_names = list(device.shanks.keys())
            probe_array = probe.to_numpy()

            # set channel indices
            device_channel_indices = np.arange(probe.get_contact_count())
            probe.set_device_channel_indices(device_channel_indices)

            for i_s, shank_name in enumerate(shank_names):
                contact_table = device.shanks[shank_name].contact_table
                pi_shank = probe.get_shanks()[i_s]
                np.testing.assert_array_equal(contact_table["contact_position"][:],
                                            probe.contact_positions[pi_shank.get_indices()])
                np.testing.assert_array_equal(contact_table["contact_shape"][:],
                                            probe_array["contact_shapes"][pi_shank.get_indices()])

                np.testing.assert_array_equal(contact_table["device_channel_index"][:],
                                             device_channel_indices)


# class TestTetrodeSeriesRoundtrip(TestCase):
#     """Simple roundtrip test for TetrodeSeries."""

#     def setUp(self):
#         self.nwbfile = set_up_nwbfile()
#         self.path = 'test.nwb'

#     def tearDown(self):
#         remove_test_file(self.path)

#     def test_roundtrip(self):
#         """
#         Add a TetrodeSeries to an NWBFile, write it to file, read the file, and test that the TetrodeSeries from the
#         file matches the original TetrodeSeries.
#         """
#         all_electrodes = self.nwbfile.create_electrode_table_region(
#             region=list(range(0, 10)),
#             description='all the electrodes'
#         )

#         data = np.random.rand(100, 3)
#         tetrode_series = TetrodeSeries(
#             name='TetrodeSeries',
#             description='description',
#             data=data,
#             rate=1000.,
#             electrodes=all_electrodes,
#             trode_id=1
#         )

#         self.nwbfile.add_acquisition(tetrode_series)

#         with NWBHDF5IO(self.path, mode='w') as io:
#             io.write(self.nwbfile)

#         with NWBHDF5IO(self.path, mode='r', load_namespaces=True) as io:
#             read_nwbfile = io.read()
#             self.assertContainerEqual(tetrode_series, read_nwbfile.acquisition['TetrodeSeries'])


if __name__ == '__main__':
    test = TestProbeConstructors()
    test.setUp()
    test.test_constructor_from_probe_single_shank()