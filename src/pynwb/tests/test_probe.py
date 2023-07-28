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
        session_description="session_description",
        identifier="identifier",
        session_start_time=datetime.datetime.now(datetime.timezone.utc),
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
        """Set up an NWB file"""
        self.probe0 = create_single_shank_probe()
        self.probe1 = create_multi_shank_probe()
        self.probegroup = create_probe_group()

    def test_constructor_from_probe_single_shank(self):
        """Test that the constructor from Probe sets values as expected for single-shank."""

        probe = self.probe0
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
        np.testing.assert_array_equal(contact_table["contact_position"][:], probe.contact_positions)
        np.testing.assert_array_equal(contact_table["contact_shape"][:], probe_array["contact_shapes"])

        # set channel indices
        device_channel_indices = np.arange(probe.get_contact_count())
        probe.set_device_channel_indices(device_channel_indices)
        device_w_indices = Probe.from_probe(probe)
        shank_names = list(device_w_indices.shanks.keys())
        contact_table = device_w_indices.shanks[shank_names[0]].contact_table
        np.testing.assert_array_equal(contact_table["device_channel_index_pi"][:], device_channel_indices)

    def test_constructor_from_probe_multi_shank(self):
        """Test that the constructor from Probe sets values as expected for multi-shank."""

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
        device_channel_indices = np.arange(probe.get_contact_count())
        probe.set_device_channel_indices(device_channel_indices)
        device_w_indices = Probe.from_probe(probe)
        for i_s, shank_name in enumerate(shank_names):
            contact_table = device_w_indices.shanks[shank_name].contact_table
            pi_shank = probe.get_shanks()[i_s]
            np.testing.assert_array_equal(
                contact_table["contact_position"][:], probe.contact_positions[pi_shank.get_indices()]
            )
            np.testing.assert_array_equal(
                contact_table["contact_shape"][:], probe_array["contact_shapes"][pi_shank.get_indices()]
            )
            np.testing.assert_array_equal(
                contact_table["device_channel_index_pi"][:], device_channel_indices[pi_shank.get_indices()]
            )

    def test_constructor_from_probegroup(self):
        """Test that the constructor from probegroup sets values as expected."""

        probegroup = self.probegroup
        global_device_channel_indices = np.arange(probegroup.get_channel_count())
        probegroup.set_global_device_channel_indices(global_device_channel_indices)
        devices = Probe.from_probegroup(probegroup)
        probes = probegroup.probes
        shank_counts = [1, 2]

        for i, device in enumerate(devices):
            probe = probes[i]
            # assert correct objects
            self.assertIsInstance(device, Device)
            self.assertIsInstance(device, Probe)

            # assert correct attributes
            self.assertEqual(len(device.shanks), shank_counts[i])

            # properties
            shank_names = list(device.shanks.keys())
            probe_array = probe.to_numpy()
            # TODO fix
            device_channel_indices = probe.device_channel_indices
            # set channel indices
            for i_s, shank_name in enumerate(shank_names):
                contact_table = device.shanks[shank_name].contact_table
                pi_shank = probe.get_shanks()[i_s]
                np.testing.assert_array_equal(
                    contact_table["contact_position"][:], probe.contact_positions[pi_shank.get_indices()]
                )
                np.testing.assert_array_equal(
                    contact_table["contact_shape"][:], probe_array["contact_shapes"][pi_shank.get_indices()]
                )

                np.testing.assert_array_equal(
                    contact_table["device_channel_index_pi"][:], device_channel_indices[pi_shank.get_indices()]
                )


class TestProbeRoundtrip(TestCase):
    """Simple roundtrip test for Probe device."""

    def setUp(self):
        self.nwbfile0 = set_up_nwbfile()
        self.nwbfile1 = set_up_nwbfile()
        self.nwbfile2 = set_up_nwbfile()

        self.probe0 = create_single_shank_probe()
        self.probe1 = create_multi_shank_probe()
        self.probegroup = create_probe_group()

        self.path0 = "test0.nwb"
        self.path1 = "test01.nwb"
        self.path2 = "testgroup.nwb"

    def tearDown(self):
        for path in [self.path0, self.path1, self.path2]:
            remove_test_file(path)

    def test_roundtrip_from_probe_single_shank(self):
        device = Probe.from_probe(self.probe0)
        self.nwbfile0.add_device(device)

        with NWBHDF5IO(self.path0, mode="w") as io:
            io.write(self.nwbfile0)

        with NWBHDF5IO(self.path0, mode="r", load_namespaces=True) as io:
            read_nwbfile = io.read()
            devices = read_nwbfile.devices
            self.assertContainerEqual(device, read_nwbfile.devices[device.name])

    def test_roundtrip_from_probe_multi_shank(self):
        device = Probe.from_probe(self.probe1)
        self.nwbfile1.add_device(device)

        with NWBHDF5IO(self.path1, mode="w") as io:
            io.write(self.nwbfile1)

        with NWBHDF5IO(self.path1, mode="r", load_namespaces=True) as io:
            read_nwbfile = io.read()
            devices = read_nwbfile.devices
            self.assertContainerEqual(device, read_nwbfile.devices[device.name])

    def test_roundtrip_from_probegroup(self):
        devices = Probe.from_probegroup(self.probegroup)
        for device in devices:
            self.nwbfile2.add_device(device)

        with NWBHDF5IO(self.path2, mode="w") as io:
            io.write(self.nwbfile2)

        with NWBHDF5IO(self.path2, mode="r", load_namespaces=True) as io:
            read_nwbfile = io.read()
            for device in devices:
                self.assertContainerEqual(device, read_nwbfile.devices[device.name])


if __name__ == "__main__":
    # test = TestProbeConstructors()
    # test.setUp()
    # # test.test_constructor_from_probe_single_shank()
    # # test.test_constructor_from_probe_multi_shank()
    # test.test_constructor_from_probegroup()

    test1 = TestProbeRoundtrip()
    test1.setUp()
    # test.test_constructor_from_probe_single_shank()
    # test.test_constructor_from_probe_multi_shank()
    test1.test_roundtrip_from_probe_single_shank()
    test1.test_roundtrip_from_probe_multi_shank()
    test1.test_roundtrip_from_probegroup()
