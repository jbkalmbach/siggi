import os
import unittest
from siggi import _siggiBase, spectra
from siggi.filters import filterFactory
from siggi.lsst_utils import BandpassDict
import numpy as np


class testSiggi(unittest.TestCase):

    @classmethod
    def setUpClass(cls):

        s = spectra()
        cls.red_spec = s.get_red_spectrum()
        cls.blue_spec = s.get_blue_spectrum()

        cls.frozen_dict = BandpassDict.loadTotalBandpassesFromFiles(
                        bandpassNames=['u', 'g'],
                        bandpassDir=os.path.join(os.path.dirname(__file__),
                                                 '../siggi/data',
                                                 'lsst_baseline_throughputs'))

        return

    def test_set_starting_points(self):

        test_sb = _siggiBase()

        # Test that width cannot be set without ratio
        self.assertRaises(AssertionError, test_sb.set_starting_points,
                          [[400., 500.]], 2, 400., 700., width=10)

        test_start_0 = test_sb.set_starting_points(None, 2, 400., 700.)[1]

        self.assertEqual(len(test_start_0), 10)
        self.assertListEqual(test_start_0[0], [400., 450., 500., 550.,
                                               550., 600., 650., 700.])
        self.assertListEqual(test_start_0[1], [400., 425., 450., 475.,
                                               475., 500., 525., 550.])
        self.assertListEqual(test_start_0[2], [550., 575., 600., 625.,
                                               625., 650., 675., 700.])

        test_start_1 = test_sb.set_starting_points(None, 2, 400., 700.,
                                                   ratio=0.5)[1]

        self.assertEqual(len(test_start_1), 10)
        self.assertListEqual(test_start_1[0], [400., 550.,
                                               550., 700.])
        self.assertListEqual(test_start_1[1], [400., 475.,
                                               475., 550.])
        self.assertListEqual(test_start_1[2], [550., 625.,
                                               625., 700.])

        self.assertRaises(AssertionError,
                          test_sb.set_starting_points, [[400., 500.]], 2, 400.,
                          700.)

        self.assertRaises(AssertionError,
                          test_sb.set_starting_points, [[400., 500.]], 2, 400.,
                          700., 0.5)

        test_start_2 = test_sb.set_starting_points([[400., 500., 600., 700.]],
                                                   2, 400., 700., ratio=0.5)[1]

        self.assertEqual(len(test_start_2), 10)
        self.assertListEqual(test_start_2[0], [400., 500., 600., 700.])
        self.assertListEqual(test_start_2[1], [400., 550.,
                                               550., 700.])
        self.assertListEqual(test_start_2[2], [400., 475.,
                                               475., 550.])
        self.assertListEqual(test_start_2[3], [550., 625.,
                                               625., 700.])

        test_start_3 = test_sb.set_starting_points([[450., 525.]],
                                                   2, 400., 700., ratio=1.0,
                                                   width=100)[1]

        self.assertEqual(len(test_start_3), 10)
        self.assertListEqual(test_start_3[0], [450., 525.])
        self.assertListEqual(test_start_3[1], [400., 600.])
        self.assertListEqual(test_start_3[2], [500., 600.])
        self.assertListEqual(test_start_3[3], [600., 600.])

        return

    def test_create_and_validate_filter_dict(self):

        test_sb = _siggiBase()
        test_f = filterFactory.create_filter_object('trap')

        # Test that assertion raised if wavelength grid not set
        self.assertRaises(AssertionError,
                          test_sb.create_and_validate_filter_dict,
                          [200.]*4, 200., 200., 2, test_f)

        test_f.set_wavelen_grid()

        # Test AssertionError raised with wrong number of filt edges
        self.assertRaises(AssertionError,
                          test_sb.create_and_validate_filter_dict,
                          [200.]*4, 200., 200., 2, test_f)

        # Test AssertionError raised with wrong number of filt edges
        self.assertRaises(AssertionError,
                          test_sb.create_and_validate_filter_dict,
                          [200.]*8, 200., 200., 2, test_f, 0.5)

        # Test AssertionError raised with wrong number of filt edges
        self.assertRaises(AssertionError,
                          test_sb.create_and_validate_filter_dict,
                          [301., 302.], 300., 302., 1, test_f, ratio=0.5,
                          width=1.)

        # Test AssertionError raised with width
        # unable to fit with filter bounds
        self.assertRaises(AssertionError,
                          test_sb.create_and_validate_filter_dict,
                          [301.], 300., 302., 1, test_f, ratio=0.5,
                          width=10.)

        # Test that higher center filter is not to left of lower
        test_input_0 = test_sb.create_and_validate_filter_dict(
            [400., 401., 402., 403., 300., 301., 302., 303.],
            300., 600., 2, test_f
        )
        self.assertFalse(test_input_0)

        test_input_0_ratio = test_sb.create_and_validate_filter_dict(
            [400., 403., 300., 303.], 300., 600., 2, test_f, ratio=0.5
        )

        self.assertFalse(test_input_0_ratio)

        # Test that proper filters get through
        test_input_1 = test_sb.create_and_validate_filter_dict(
            [300., 301., 302., 303., 400., 401., 402., 403.],
            300., 403., 2, test_f
        )
        self.assertTrue(test_input_1)

        test_input_1_ratio = test_sb.create_and_validate_filter_dict(
            [300., 303., 400., 403.], 300., 403., 2, test_f, ratio=0.5
        )
        self.assertTrue(test_input_1_ratio)

        # Test that filter cannot be less than min allowed wavelength
        test_input_2 = test_sb.create_and_validate_filter_dict(
            [300., 301., 302., 303., 400., 401., 402., 403.],
            301., 600., 2, test_f
        )
        self.assertFalse(test_input_2)

        test_input_2_ratio = test_sb.create_and_validate_filter_dict(
            [300., 303., 400., 403.], 301., 600., 2, test_f, ratio=0.5
        )
        self.assertFalse(test_input_2_ratio)

        # Test that filter cannot be more than max allowed wavelength
        test_input_3 = test_sb.create_and_validate_filter_dict(
            [300., 301., 302., 303., 400., 401., 402., 403.],
            300., 402., 2, test_f
        )
        self.assertFalse(test_input_3)

        test_input_3_ratio = test_sb.create_and_validate_filter_dict(
            [300., 303., 400., 403.], 300., 402., 2, test_f, ratio=0.5)
        self.assertFalse(test_input_3_ratio)

        # Test that a single filter will properly be tested

        test_input_4 = test_sb.create_and_validate_filter_dict(
            [300., 301., 302., 303.], 300., 600., 1, test_f
        )
        self.assertTrue(test_input_4)

        test_input_4_ratio = test_sb.create_and_validate_filter_dict(
            [300., 303.], 300., 600., 1, test_f, ratio=0.5
        )
        self.assertTrue(test_input_4_ratio)

        test_input_5 = test_sb.create_and_validate_filter_dict(
            [300., 301., 302., 303.], 301., 600., 1, test_f
        )
        self.assertFalse(test_input_5)

        test_input_5_ratio = test_sb.create_and_validate_filter_dict(
            [300., 303.], 301., 600., 1, test_f, ratio=0.5
        )
        self.assertFalse(test_input_5_ratio)

        test_input_6 = test_sb.create_and_validate_filter_dict(
            [300., 301., 302., 303.], 300., 302., 1, test_f
        )
        self.assertFalse(test_input_6)

        test_input_6_ratio = test_sb.create_and_validate_filter_dict(
            [300., 303.], 300., 302., 1, test_f, ratio=0.5
        )
        self.assertFalse(test_input_6_ratio)

        test_input_7 = test_sb.create_and_validate_filter_dict(
            [300., 301., 302., 301.95], 300., 303., 1, test_f
        )
        self.assertFalse(test_input_7)

        test_input_7_ratio = test_sb.create_and_validate_filter_dict(
            [301., 300.95], 300., 302., 1, test_f, ratio=0.5
        )
        self.assertFalse(test_input_7_ratio)

        # Test filters are not smaller than wavelength step

        wave_step = test_f.wavelen_step

        test_input_8 = test_sb.create_and_validate_filter_dict(
            [300., 300., 300., 300. + 2*wave_step], 300., 303., 1, test_f
        )
        self.assertFalse(test_input_8)

        test_input_8_ratio = test_sb.create_and_validate_filter_dict(
            [301., 301. + 2*wave_step], 300., 302., 1, test_f, ratio=0.5
        )
        self.assertFalse(test_input_8_ratio)

        # Test that wavelength step check doesn't affect triangular filter

        test_input_9 = test_sb.create_and_validate_filter_dict(
            [300., 300., 300. + wave_step*2, 301.9], 300., 303., 1, test_f
        )
        self.assertTrue(test_input_9)

        test_input_10 = test_sb.create_and_validate_filter_dict(
            [300., 301., 301.5, 301.9, 301.9, 302.1, 302.3, 302.5],
            300., 303., 2, test_f
        )
        self.assertTrue(test_input_10)

        test_input_10_ratio = test_sb.create_and_validate_filter_dict(
            [301., 301.3, 301.3, 301.9], 300., 302., 2, test_f, ratio=0.5
            )
        self.assertTrue(test_input_10_ratio)

        # Test giving different wavelen_step

        wave_step = 0.05
        test_f.set_wavelen_grid(wavelen_step=wave_step)

        test_input_11 = test_sb.create_and_validate_filter_dict(
            [300., 300., 300., 300. + wave_step/2.], 300., 303., 1, test_f
        )
        self.assertFalse(test_input_11)

        test_input_11_ratio = test_sb.create_and_validate_filter_dict(
            [301., 301. + wave_step/2.], 300., 302., 1, test_f, ratio=0.5
        )
        self.assertFalse(test_input_11_ratio)

        # Test giving set width

        width = 10
        test_input_12_ratio = test_sb.create_and_validate_filter_dict(
            [301.], 300., 312., 1, test_f, ratio=0.5, width=width
        )
        self.assertTrue(test_input_12_ratio)

        # Now should fail if the left edge is too great to fit in filt_max

        test_input_13_ratio = test_sb.create_and_validate_filter_dict(
            [305.], 300., 312., 1, test_f, ratio=0.5, width=width
        )
        self.assertFalse(test_input_13_ratio)


if __name__ == '__main__':
    unittest.main()
