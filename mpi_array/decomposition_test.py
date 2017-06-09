"""
==============================================
The :mod:`mpi_array.decomposition_test` Module
==============================================

Module defining :mod:`mpi_array.decomposition` unit-tests.
Execute as::

   python -m mpi_array.decomposition_test


Classes
=======

.. autosummary::
   :toctree: generated/

   IndexingExtentTest - Tests for :obj:`mpi_array.decomposition.IndexingExtent`.
   HaloIndexingExtentTest - Tests for :obj:`mpi_array.decomposition.IndexingExtent`.
   DecompExtentTest - Tests for :obj:`mpi_array.decomposition.DecompExtent`.
   MemAllocTopologyTest - Tests for :obj:`mpi_array.decomposition.MemAllocTopology`.
   CartesianDecompositionTest - Tests for :obj:`mpi_array.decomposition.CartesianDecomposition`.


"""
from __future__ import absolute_import
from .license import license as _license, copyright as _copyright
import mpi_array.unittest as _unittest
import mpi_array.logging as _logging  # noqa: E402,F401
import mpi_array as _mpi_array

import mpi4py.MPI as _mpi
import numpy as _np  # noqa: E402,F401
from mpi_array.decomposition import IndexingExtent, HaloIndexingExtent, DecompExtent
from mpi_array.decomposition import CartesianDecomposition, MemAllocTopology
import array_split as _array_split

__author__ = "Shane J. Latham"
__license__ = _license()
__copyright__ = _copyright()
__version__ = _mpi_array.__version__


class IndexingExtentTest(_unittest.TestCase):
    """
    :obj:`unittest.TestCase` for :obj:`mpi_array.decomposition.IndexingExtentTest`.
    """

    def test_repr(self):
        """
        Test for :samp:`repr(IndexingExtent(start=(1,2,3), stop=(8,9,10)))`.
        """
        ie = IndexingExtent(start=(10,), stop=(32,))
        self.assertNotEqual(None, str(ie))
        self.assertNotEqual("", str(ie))

        self.assertEqual(ie, eval(repr(ie)))

    def test_attributes(self):
        """
        Tests :attr:`mpi_array.decomposition.IndexingExtent.start`
        and :attr:`mpi_array.decomposition.IndexingExtent.stop`
        and :attr:`mpi_array.decomposition.IndexingExtent.shape`
        attributes.
        """
        ie = IndexingExtent(start=(10,), stop=(32,))
        self.assertTrue(_np.all(ie.shape == (22,)))
        self.assertTrue(_np.all(ie.start == (10,)))
        self.assertTrue(_np.all(ie.stop == (32,)))

        ie = IndexingExtent((slice(10, 32),))
        self.assertTrue(_np.all(ie.shape == (22,)))
        self.assertTrue(_np.all(ie.start == (10,)))
        self.assertTrue(_np.all(ie.stop == (32,)))

        ie = IndexingExtent(start=(10, 25), stop=(32, 55))
        self.assertTrue(_np.all(ie.shape == (22, 30)))
        self.assertTrue(_np.all(ie.start == (10, 25)))
        self.assertTrue(_np.all(ie.stop == (32, 55)))

        ie = IndexingExtent((slice(10, 32), slice(25, 55)))
        self.assertTrue(_np.all(ie.shape == (22, 30)))
        self.assertTrue(_np.all(ie.start == (10, 25)))
        self.assertTrue(_np.all(ie.stop == (32, 55)))

    def test_intersection_1d(self):
        """
        Tests :meth:`mpi_array.decomposition.IndexingExtent.calc_intersection` method, 1D indexing.
        """
        ie0 = IndexingExtent(start=(10,), stop=(32,))
        iei = ie0.calc_intersection(ie0)
        self.assertTrue(_np.all(iei.shape == (22,)))
        self.assertTrue(_np.all(iei.start == (10,)))
        self.assertTrue(_np.all(iei.stop == (32,)))

        ie1 = IndexingExtent(start=(5,), stop=(32,))
        iei = ie0.calc_intersection(ie1)
        self.assertTrue(_np.all(iei.shape == (22,)))
        self.assertTrue(_np.all(iei.start == (10,)))
        self.assertTrue(_np.all(iei.stop == (32,)))

        ie1 = IndexingExtent(start=(10,), stop=(39,))
        iei = ie0.calc_intersection(ie1)
        self.assertTrue(_np.all(iei.shape == (22,)))
        self.assertTrue(_np.all(iei.start == (10,)))
        self.assertTrue(_np.all(iei.stop == (32,)))

        ie1 = IndexingExtent(start=(-5,), stop=(39,))
        iei = ie0.calc_intersection(ie1)
        self.assertTrue(_np.all(iei.shape == (22,)))
        self.assertTrue(_np.all(iei.start == (10,)))
        self.assertTrue(_np.all(iei.stop == (32,)))

        ie1 = IndexingExtent(start=(11,), stop=(31,))
        iei = ie0.calc_intersection(ie1)
        self.assertTrue(_np.all(iei.shape == (20,)))
        self.assertTrue(_np.all(iei.start == (11,)))
        self.assertTrue(_np.all(iei.stop == (31,)))

        ie1 = IndexingExtent(start=(5,), stop=(10,))
        iei = ie0.calc_intersection(ie1)
        self.assertEqual(None, iei)

        ie1 = IndexingExtent(start=(32,), stop=(55,))
        iei = ie0.calc_intersection(ie1)
        self.assertEqual(None, iei)

    def test_intersection_2d(self):
        """
        Tests :meth:`mpi_array.decomposition.IndexingExtent.calc_intersection` method, 2D indexing.
        """
        ie0 = IndexingExtent(start=(10, 20), stop=(32, 64))
        iei = ie0.calc_intersection(ie0)
        self.assertSequenceEqual(ie0.shape.tolist(), iei.shape.tolist())
        self.assertSequenceEqual(ie0.start.tolist(), iei.start.tolist())
        self.assertSequenceEqual(ie0.stop.tolist(), iei.stop.tolist())

        ie1 = IndexingExtent(start=(0, 20), stop=(10, 64))
        iei = ie0.calc_intersection(ie1)
        self.assertEqual(None, iei)

        ie1 = IndexingExtent(start=(10, 0), stop=(32, 20))
        iei = ie0.calc_intersection(ie1)
        self.assertEqual(None, iei)

        ie1 = IndexingExtent(start=(0, 0), stop=(10, 20))
        iei = ie0.calc_intersection(ie1)
        self.assertEqual(None, iei)

        ie1 = IndexingExtent(start=(32, 64), stop=(110, 120))
        iei = ie0.calc_intersection(ie1)
        self.assertEqual(None, iei)

        ie1 = IndexingExtent(start=(20, 10), stop=(30, 40))
        iei = ie0.calc_intersection(ie1)
        self.assertSequenceEqual([10, 20], iei.shape.tolist())
        self.assertSequenceEqual([20, 20], iei.start.tolist())
        self.assertSequenceEqual([30, 40], iei.stop.tolist())

        ie1 = IndexingExtent(start=(22, 54), stop=(80, 90))
        iei = ie0.calc_intersection(ie1)
        self.assertSequenceEqual([10, 10], iei.shape.tolist())
        self.assertSequenceEqual([22, 54], iei.start.tolist())
        self.assertSequenceEqual([32, 64], iei.stop.tolist())


class HaloIndexingExtentTest(_unittest.TestCase):
    """
    :obj:`unittest.TestCase` for :obj:`mpi_array.decomposition.HaloIndexingExtentTest`.
    """

    def test_repr(self):
        """
        Test for :samp:`repr(HaloIndexingExtent(start=(1,2,3), stop=(8,9,10)))`.
        """
        ie = HaloIndexingExtent(start=(10, 15), stop=(32, 66), halo=((1, 2), (3, 4)))
        self.assertNotEqual(None, str(ie))
        self.assertNotEqual("", str(ie))

        self.assertEqual(ie, eval(repr(ie)))

    def test_attributes(self):
        """
        :obj:`unittest.TestCase` for :obj:`mpi_array.decomposition.HaloIndexingExtentTest`
        attributes.
        """

        hie1 = HaloIndexingExtent(start=(10, 0), stop=(32, 20), halo=_np.array(((0, 0), (0, 0))))
        self.assertSequenceEqual([10, 0], hie1.start_n.tolist())
        self.assertSequenceEqual([10, 0], hie1.start_h.tolist())
        self.assertSequenceEqual([32, 20], hie1.stop_n.tolist())
        self.assertSequenceEqual([32, 20], hie1.stop_h.tolist())
        self.assertSequenceEqual([22, 20], hie1.shape_n.tolist())
        self.assertSequenceEqual([22, 20], hie1.shape_h.tolist())
        self.assertEqual(22 * 20, hie1.size_n)
        self.assertEqual(22 * 20, hie1.size_h)

        hie1 = HaloIndexingExtent(start=(10, 3), stop=(32, 20), halo=_np.array(((1, 2), (3, 4))))
        self.assertSequenceEqual([10, 3], hie1.start_n.tolist())
        self.assertSequenceEqual([9, 0], hie1.start_h.tolist())
        self.assertSequenceEqual([32, 20], hie1.stop_n.tolist())
        self.assertSequenceEqual([34, 24], hie1.stop_h.tolist())
        self.assertSequenceEqual([22, 17], hie1.shape_n.tolist())
        self.assertSequenceEqual([25, 24], hie1.shape_h.tolist())
        self.assertEqual(22 * 17, hie1.size_n)
        self.assertEqual(25 * 24, hie1.size_h)

    def test_to_slice(self):
        """
        :obj:`unittest.TestCase` for :obj:`mpi_array.decomposition.HaloIndexingExtentTest`
        methods: :samp:`to_slice`, :samp:`to_slice_n`, and :samp:`to_slice_h`.
        """
        hie1 = HaloIndexingExtent(start=(10, 3), stop=(32, 20), halo=_np.array(((1, 2), (3, 4))))
        self.assertSequenceEqual(
            (slice(10, 32, None), slice(3, 20, None)),
            hie1.to_slice_n()
        )
        self.assertSequenceEqual(
            (slice(10, 32, None), slice(3, 20, None)),
            hie1.to_slice()
        )
        self.assertSequenceEqual(
            (slice(9, 34, None), slice(0, 24, None)),
            hie1.to_slice_h()
        )


class DecompExtentTest(_unittest.TestCase):
    """
    :obj:`unittest.TestCase` for :obj:`mpi_array.decomposition.DecompExtent`.
    """

    def test_construct_attribs(self):
        """
        Assertions for properties.
        """
        de = \
            DecompExtent(
                cart_rank=0,
                cart_coord=(0,),
                cart_shape=(1,),
                array_shape=(100,),
                slice=(slice(0, 100),),
                halo=((10, 10),)
            )

        self.assertEqual(0, de.cart_rank)
        self.assertTrue(_np.all(de.cart_coord == (0,)))
        self.assertTrue(_np.all(de.cart_shape == (1,)))
        self.assertTrue(_np.all(de.halo == 0))

    def test_extent_calcs_1d_thick_tiles(self):
        """
        Tests :meth:`mpi_array.decomposition.DecompExtent.halo_slab_extent`
        and :meth:`mpi_array.decomposition.DecompExtent.no_halo_extent` methods
        when halo size is smaller than the tile size.
        """
        halo = ((10, 10),)
        splt = _array_split.shape_split((300,), axis=(3,), halo=0)
        de = \
            [
                DecompExtent(
                    cart_rank=r,
                    cart_coord=(r,),
                    cart_shape=(splt.shape[0],),
                    array_shape=(300,),
                    slice=splt[r],
                    halo=halo
                )
                for r in range(0, splt.shape[0])
            ]

        self.assertEqual(0, de[0].cart_rank)
        self.assertTrue(_np.all(de[0].cart_coord == (0,)))
        self.assertTrue(_np.all(de[0].cart_shape == (3,)))
        self.assertTrue(_np.all(de[0].halo == ((0, 10),)))
        self.assertEqual(
            IndexingExtent(start=(0,), stop=(0,)),
            de[0].halo_slab_extent(0, de[0].LO)
        )
        self.assertEqual(
            IndexingExtent(start=(100,), stop=(110,)),
            de[0].halo_slab_extent(0, de[0].HI)
        )
        self.assertEqual(
            IndexingExtent(start=(0,), stop=(100,)),
            de[0].no_halo_extent(0)
        )

        self.assertEqual(1, de[1].cart_rank)
        self.assertTrue(_np.all(de[1].cart_coord == (1,)))
        self.assertTrue(_np.all(de[1].cart_shape == (3,)))
        self.assertTrue(_np.all(de[1].halo == ((10, 10),)))
        self.assertEqual(
            IndexingExtent(start=(90,), stop=(100,)),
            de[1].halo_slab_extent(0, de[0].LO)
        )
        self.assertEqual(
            IndexingExtent(start=(200,), stop=(210,)),
            de[1].halo_slab_extent(0, de[0].HI)
        )
        self.assertEqual(
            IndexingExtent(start=(100,), stop=(200,)),
            de[1].no_halo_extent(0)
        )

        self.assertEqual(2, de[2].cart_rank)
        self.assertTrue(_np.all(de[2].cart_coord == (2,)))
        self.assertTrue(_np.all(de[2].cart_shape == (3,)))
        self.assertTrue(_np.all(de[2].halo == ((10, 0),)))
        self.assertEqual(
            IndexingExtent(start=(190,), stop=(200,)),
            de[2].halo_slab_extent(0, de[0].LO)
        )
        self.assertEqual(
            IndexingExtent(start=(300,), stop=(300,)),
            de[2].halo_slab_extent(0, de[0].HI)
        )
        self.assertEqual(
            IndexingExtent(start=(200,), stop=(300,)),
            de[2].no_halo_extent(0)
        )

    def test_extent_calcs_1d_thin_tiles(self):
        """
        Tests :meth:`mpi_array.decomposition.DecompExtent.halo_slab_extent`
        and :meth:`mpi_array.decomposition.DecompExtent.no_halo_extent` methods
        when halo size is larger than the tile size, 1D fixture.
        """
        halo = ((5, 5),)
        splt = _array_split.shape_split((15,), axis=(5,), halo=0)
        de = \
            [
                DecompExtent(
                    cart_rank=r,
                    cart_coord=(r,),
                    cart_shape=(splt.shape[0],),
                    array_shape=(15,),
                    slice=splt[r],
                    halo=halo
                )
                for r in range(0, splt.shape[0])
            ]

        self.assertEqual(0, de[0].cart_rank)
        self.assertTrue(_np.all(de[0].cart_coord == (0,)))
        self.assertTrue(_np.all(de[0].cart_shape == (5,)))
        self.assertTrue(_np.all(de[0].halo == ((0, 5),)))
        self.assertEqual(
            IndexingExtent(start=(0,), stop=(0,)),
            de[0].halo_slab_extent(0, de[0].LO)
        )
        self.assertEqual(
            IndexingExtent(start=(3,), stop=(8,)),
            de[0].halo_slab_extent(0, de[0].HI)
        )
        self.assertEqual(
            IndexingExtent(start=(0,), stop=(3,)),
            de[0].no_halo_extent(0)
        )

        self.assertEqual(1, de[1].cart_rank)
        self.assertTrue(_np.all(de[1].cart_coord == (1,)))
        self.assertTrue(_np.all(de[1].cart_shape == (5,)))
        self.assertTrue(_np.all(de[1].halo == ((3, 5),)))
        self.assertEqual(
            IndexingExtent(start=(0,), stop=(3,)),
            de[1].halo_slab_extent(0, de[0].LO)
        )
        self.assertEqual(
            IndexingExtent(start=(6,), stop=(11,)),
            de[1].halo_slab_extent(0, de[0].HI)
        )
        self.assertEqual(
            IndexingExtent(start=(3,), stop=(6,)),
            de[1].no_halo_extent(0)
        )

        self.assertEqual(2, de[2].cart_rank)
        self.assertTrue(_np.all(de[2].cart_coord == (2,)))
        self.assertTrue(_np.all(de[2].cart_shape == (5,)))
        self.assertTrue(_np.all(de[2].halo == ((5, 5),)))
        self.assertEqual(
            IndexingExtent(start=(1,), stop=(6,)),
            de[2].halo_slab_extent(0, de[0].LO)
        )
        self.assertEqual(
            IndexingExtent(start=(9,), stop=(14,)),
            de[2].halo_slab_extent(0, de[0].HI)
        )
        self.assertEqual(
            IndexingExtent(start=(6,), stop=(9,)),
            de[2].no_halo_extent(0)
        )

        self.assertEqual(3, de[3].cart_rank)
        self.assertTrue(_np.all(de[3].cart_coord == (3,)))
        self.assertTrue(_np.all(de[3].cart_shape == (5,)))
        self.assertTrue(_np.all(de[3].halo == ((5, 3),)))
        self.assertEqual(
            IndexingExtent(start=(4,), stop=(9,)),
            de[3].halo_slab_extent(0, de[0].LO)
        )
        self.assertEqual(
            IndexingExtent(start=(12,), stop=(15,)),
            de[3].halo_slab_extent(0, de[0].HI)
        )
        self.assertEqual(
            IndexingExtent(start=(9,), stop=(12,)),
            de[3].no_halo_extent(0)
        )

        self.assertEqual(4, de[4].cart_rank)
        self.assertTrue(_np.all(de[4].cart_coord == (4,)))
        self.assertTrue(_np.all(de[4].cart_shape == (5,)))
        self.assertTrue(_np.all(de[4].halo == ((5, 0),)))
        self.assertEqual(
            IndexingExtent(start=(7,), stop=(12,)),
            de[4].halo_slab_extent(0, de[0].LO)
        )
        self.assertEqual(
            IndexingExtent(start=(15,), stop=(15,)),
            de[4].halo_slab_extent(0, de[0].HI)
        )
        self.assertEqual(
            IndexingExtent(start=(12,), stop=(15,)),
            de[4].no_halo_extent(0)
        )

    def test_extent_calcs_2d_thick_tiles(self):
        """
        Tests :meth:`mpi_array.decomposition.DecompExtent.halo_slab_extent`
        and :meth:`mpi_array.decomposition.DecompExtent.no_halo_extent` methods
        when halo size is smaller than the tile size, 2D fixture.
        """
        halo = ((10, 10), (5, 5))
        splt = _array_split.shape_split((300, 600), axis=(3, 3), halo=0)
        de = \
            [
                DecompExtent(
                    cart_rank=r,
                    cart_coord=_np.unravel_index(r, splt.shape),
                    cart_shape=splt.shape,
                    array_shape=(300, 600),
                    slice=splt[tuple(_np.unravel_index(r, splt.shape))],
                    halo=halo
                )
                for r in range(0, _np.product(splt.shape))
            ]

        self.assertEqual(0, de[0].cart_rank)
        self.assertTrue(_np.all(de[0].cart_coord == (0, 0)))
        self.assertTrue(_np.all(de[0].cart_shape == (3, 3)))
        self.assertSequenceEqual([[0, 10], [0, 5]], de[0].halo.tolist())
        self.assertEqual(
            IndexingExtent(start=(0, 0), stop=(0, 205)),
            de[0].halo_slab_extent(0, de[0].LO)
        )
        self.assertEqual(
            IndexingExtent(start=(100, 0), stop=(110, 205)),
            de[0].halo_slab_extent(0, de[0].HI)
        )
        self.assertEqual(
            IndexingExtent(start=(0, 0), stop=(110, 0)),
            de[0].halo_slab_extent(1, de[0].LO)
        )
        self.assertEqual(
            IndexingExtent(start=(0, 200), stop=(110, 205)),
            de[0].halo_slab_extent(1, de[0].HI)
        )
        self.assertEqual(
            IndexingExtent(start=(0, 0), stop=(100, 205)),
            de[0].no_halo_extent(0)
        )
        self.assertEqual(
            IndexingExtent(start=(0, 0), stop=(110, 200)),
            de[0].no_halo_extent(1)
        )

        self.assertEqual(1, de[1].cart_rank)
        self.assertTrue(_np.all(de[1].cart_coord == (0, 1)))
        self.assertTrue(_np.all(de[1].cart_shape == (3, 3)))
        self.assertSequenceEqual([[0, 10], [5, 5]], de[1].halo.tolist())
        self.assertEqual(
            IndexingExtent(start=(0, 195), stop=(0, 405)),
            de[1].halo_slab_extent(0, de[1].LO)
        )
        self.assertEqual(
            IndexingExtent(start=(100, 195), stop=(110, 405)),
            de[1].halo_slab_extent(0, de[1].HI)
        )
        self.assertEqual(
            IndexingExtent(start=(0, 195), stop=(110, 200)),
            de[1].halo_slab_extent(1, de[0].LO)
        )
        self.assertEqual(
            IndexingExtent(start=(0, 400), stop=(110, 405)),
            de[1].halo_slab_extent(1, de[0].HI)
        )
        self.assertEqual(
            IndexingExtent(start=(0, 195), stop=(100, 405)),
            de[1].no_halo_extent(0)
        )
        self.assertEqual(
            IndexingExtent(start=(0, 200), stop=(110, 400)),
            de[1].no_halo_extent(1)
        )

        self.assertEqual(2, de[2].cart_rank)
        self.assertTrue(_np.all(de[2].cart_coord == (0, 2)))
        self.assertTrue(_np.all(de[2].cart_shape == (3, 3)))
        self.assertSequenceEqual([[0, 10], [5, 0]], de[2].halo.tolist())
        self.assertEqual(
            IndexingExtent(start=(0, 395), stop=(0, 600)),
            de[2].halo_slab_extent(0, de[2].LO)
        )
        self.assertEqual(
            IndexingExtent(start=(100, 395), stop=(110, 600)),
            de[2].halo_slab_extent(0, de[2].HI)
        )
        self.assertEqual(
            IndexingExtent(start=(0, 395), stop=(110, 400)),
            de[2].halo_slab_extent(1, de[0].LO)
        )
        self.assertEqual(
            IndexingExtent(start=(0, 600), stop=(110, 600)),
            de[2].halo_slab_extent(1, de[0].HI)
        )
        self.assertEqual(
            IndexingExtent(start=(0, 395), stop=(100, 600)),
            de[2].no_halo_extent(0)
        )
        self.assertEqual(
            IndexingExtent(start=(0, 400), stop=(110, 600)),
            de[2].no_halo_extent(1)
        )

        self.assertEqual(3, de[3].cart_rank)
        self.assertTrue(_np.all(de[3].cart_coord == (1, 0)))
        self.assertTrue(_np.all(de[3].cart_shape == (3, 3)))
        self.assertSequenceEqual([[10, 10], [0, 5]], de[3].halo.tolist())
        self.assertEqual(
            IndexingExtent(start=(90, 0), stop=(100, 205)),
            de[3].halo_slab_extent(0, de[3].LO)
        )
        self.assertEqual(
            IndexingExtent(start=(200, 0), stop=(210, 205)),
            de[3].halo_slab_extent(0, de[3].HI)
        )
        self.assertEqual(
            IndexingExtent(start=(90, 0), stop=(210, 0)),
            de[3].halo_slab_extent(1, de[3].LO)
        )
        self.assertEqual(
            IndexingExtent(start=(90, 200), stop=(210, 205)),
            de[3].halo_slab_extent(1, de[3].HI)
        )
        self.assertEqual(
            IndexingExtent(start=(100, 0), stop=(200, 205)),
            de[3].no_halo_extent(0)
        )
        self.assertEqual(
            IndexingExtent(start=(90, 0), stop=(210, 200)),
            de[3].no_halo_extent(1)
        )

        self.assertEqual(4, de[4].cart_rank)
        self.assertTrue(_np.all(de[4].cart_coord == (1, 1)))
        self.assertTrue(_np.all(de[4].cart_shape == (3, 3)))
        self.assertSequenceEqual([[10, 10], [5, 5]], de[4].halo.tolist())
        self.assertEqual(
            IndexingExtent(start=(90, 195), stop=(100, 405)),
            de[4].halo_slab_extent(0, de[4].LO)
        )
        self.assertEqual(
            IndexingExtent(start=(200, 195), stop=(210, 405)),
            de[4].halo_slab_extent(0, de[4].HI)
        )
        self.assertEqual(
            IndexingExtent(start=(90, 195), stop=(210, 200)),
            de[4].halo_slab_extent(1, de[0].LO)
        )
        self.assertEqual(
            IndexingExtent(start=(90, 400), stop=(210, 405)),
            de[4].halo_slab_extent(1, de[0].HI)
        )
        self.assertEqual(
            IndexingExtent(start=(100, 195), stop=(200, 405)),
            de[4].no_halo_extent(0)
        )
        self.assertEqual(
            IndexingExtent(start=(90, 200), stop=(210, 400)),
            de[4].no_halo_extent(1)
        )

        self.assertEqual(5, de[5].cart_rank)
        self.assertTrue(_np.all(de[5].cart_coord == (1, 2)))
        self.assertTrue(_np.all(de[5].cart_shape == (3, 3)))
        self.assertSequenceEqual([[10, 10], [5, 0]], de[5].halo.tolist())
        self.assertEqual(
            IndexingExtent(start=(90, 395), stop=(100, 600)),
            de[5].halo_slab_extent(0, de[5].LO)
        )
        self.assertEqual(
            IndexingExtent(start=(200, 395), stop=(210, 600)),
            de[5].halo_slab_extent(0, de[5].HI)
        )
        self.assertEqual(
            IndexingExtent(start=(90, 395), stop=(210, 400)),
            de[5].halo_slab_extent(1, de[0].LO)
        )
        self.assertEqual(
            IndexingExtent(start=(90, 600), stop=(210, 600)),
            de[5].halo_slab_extent(1, de[0].HI)
        )
        self.assertEqual(
            IndexingExtent(start=(100, 395), stop=(200, 600)),
            de[5].no_halo_extent(0)
        )
        self.assertEqual(
            IndexingExtent(start=(90, 400), stop=(210, 600)),
            de[5].no_halo_extent(1)
        )

        self.assertEqual(6, de[6].cart_rank)
        self.assertTrue(_np.all(de[6].cart_coord == (2, 0)))
        self.assertTrue(_np.all(de[6].cart_shape == (3, 3)))
        self.assertSequenceEqual([[10, 0], [0, 5]], de[6].halo.tolist())
        self.assertEqual(
            IndexingExtent(start=(190, 0), stop=(200, 205)),
            de[6].halo_slab_extent(0, de[6].LO)
        )
        self.assertEqual(
            IndexingExtent(start=(300, 0), stop=(300, 205)),
            de[6].halo_slab_extent(0, de[6].HI)
        )
        self.assertEqual(
            IndexingExtent(start=(190, 0), stop=(300, 0)),
            de[6].halo_slab_extent(1, de[6].LO)
        )
        self.assertEqual(
            IndexingExtent(start=(190, 200), stop=(300, 205)),
            de[6].halo_slab_extent(1, de[6].HI)
        )
        self.assertEqual(
            IndexingExtent(start=(200, 0), stop=(300, 205)),
            de[6].no_halo_extent(0)
        )
        self.assertEqual(
            IndexingExtent(start=(190, 0), stop=(300, 200)),
            de[6].no_halo_extent(1)
        )

        self.assertEqual(7, de[7].cart_rank)
        self.assertTrue(_np.all(de[7].cart_coord == (2, 1)))
        self.assertTrue(_np.all(de[7].cart_shape == (3, 3)))
        self.assertSequenceEqual([[10, 0], [5, 5]], de[7].halo.tolist())
        self.assertEqual(
            IndexingExtent(start=(190, 195), stop=(200, 405)),
            de[7].halo_slab_extent(0, de[7].LO)
        )
        self.assertEqual(
            IndexingExtent(start=(300, 195), stop=(300, 405)),
            de[7].halo_slab_extent(0, de[7].HI)
        )
        self.assertEqual(
            IndexingExtent(start=(190, 195), stop=(300, 200)),
            de[7].halo_slab_extent(1, de[0].LO)
        )
        self.assertEqual(
            IndexingExtent(start=(190, 400), stop=(300, 405)),
            de[7].halo_slab_extent(1, de[0].HI)
        )
        self.assertEqual(
            IndexingExtent(start=(200, 195), stop=(300, 405)),
            de[7].no_halo_extent(0)
        )
        self.assertEqual(
            IndexingExtent(start=(190, 200), stop=(300, 400)),
            de[7].no_halo_extent(1)
        )

        self.assertEqual(8, de[8].cart_rank)
        self.assertTrue(_np.all(de[8].cart_coord == (2, 2)))
        self.assertTrue(_np.all(de[8].cart_shape == (3, 3)))
        self.assertSequenceEqual([[10, 0], [5, 0]], de[8].halo.tolist())
        self.assertEqual(
            IndexingExtent(start=(190, 395), stop=(200, 600)),
            de[8].halo_slab_extent(0, de[8].LO)
        )
        self.assertEqual(
            IndexingExtent(start=(300, 395), stop=(300, 600)),
            de[8].halo_slab_extent(0, de[8].HI)
        )
        self.assertEqual(
            IndexingExtent(start=(190, 395), stop=(300, 400)),
            de[8].halo_slab_extent(1, de[0].LO)
        )
        self.assertEqual(
            IndexingExtent(start=(190, 600), stop=(300, 600)),
            de[8].halo_slab_extent(1, de[0].HI)
        )
        self.assertEqual(
            IndexingExtent(start=(200, 395), stop=(300, 600)),
            de[8].no_halo_extent(0)
        )
        self.assertEqual(
            IndexingExtent(start=(190, 400), stop=(300, 600)),
            de[8].no_halo_extent(1)
        )


class MemAllocTopologyTest(_unittest.TestCase):
    """
    :obj:`unittest.TestCase` for :obj:`mpi_array.decomposition.MemAllocTopology`.
    """

    def test_construct_invalid_dims(self):
        mat = None
        with self.assertRaises(ValueError):
            mat = MemAllocTopology()
        with self.assertRaises(ValueError):
            mat = MemAllocTopology(ndims=None, dims=None)
        with self.assertRaises(ValueError):
            mat = MemAllocTopology(dims=tuple(), ndims=1)
        with self.assertRaises(ValueError):
            mat = MemAllocTopology(dims=tuple([0, 2]), ndims=1)
        with self.assertRaises(ValueError):
            mat = MemAllocTopology(dims=tuple([1, 2]), ndims=3)

        self.assertEqual(None, mat)

    def test_construct_shared(self):
        mat = MemAllocTopology(ndims=1)
        self.assertEqual(_mpi.IDENT, _mpi.Comm.Compare(_mpi.COMM_WORLD, mat.rank_comm))

        mat = MemAllocTopology(ndims=4)
        self.assertEqual(_mpi.IDENT, _mpi.Comm.Compare(_mpi.COMM_WORLD, mat.rank_comm))

        mat = MemAllocTopology(dims=(0,))
        self.assertEqual(_mpi.IDENT, _mpi.Comm.Compare(_mpi.COMM_WORLD, mat.rank_comm))

        mat = MemAllocTopology(dims=(0, 0))
        self.assertEqual(_mpi.IDENT, _mpi.Comm.Compare(_mpi.COMM_WORLD, mat.rank_comm))

        mat = MemAllocTopology(dims=(0, 0, 0))
        self.assertEqual(_mpi.IDENT, _mpi.Comm.Compare(_mpi.COMM_WORLD, mat.rank_comm))

    def test_construct_no_shared(self):
        mat = MemAllocTopology(ndims=1, shared_mem_comm=_mpi.COMM_SELF)
        self.assertEqual(_mpi.IDENT, _mpi.Comm.Compare(_mpi.COMM_WORLD, mat.rank_comm))
        self.assertEqual(1, mat.shared_mem_comm.size)
        self.assertNotEqual(_mpi.COMM_WORLD, _mpi.COMM_NULL)


class CartesianDecompositionTest(_unittest.TestCase):
    """
    :obj:`unittest.TestCase` for :obj:`mpi_array.decomposition.CartesianDecomposition`.
    """

    def test_construct_1d(self):
        """
        Test :obj:`mpi_array.decomposition.CartesianDecomposition` construction.
        """
        decomp = CartesianDecomposition((8 * _mpi.COMM_WORLD.size,))
        self.assertNotEqual(None, decomp._mem_alloc_topology)

        mnt = MemAllocTopology(ndims=1, shared_mem_comm=_mpi.COMM_SELF)
        decomp = \
            CartesianDecomposition((8 * _mpi.COMM_WORLD.size,), mem_alloc_topology=mnt)

        decomp.root_logger.info("START " + self.id())
        decomp.root_logger.info(str(decomp))
        decomp.root_logger.info("END   " + self.id())

    def test_construct_1d_with_halo(self):
        """
        Test :obj:`mpi_array.decomposition.CartesianDecomposition` construction.
        """
        decomp = CartesianDecomposition((8 * _mpi.COMM_WORLD.size,), halo=((2, 4),))
        self.assertNotEqual(None, decomp._mem_alloc_topology)

        mnt = MemAllocTopology(ndims=1, shared_mem_comm=_mpi.COMM_SELF)
        decomp = \
            CartesianDecomposition(
                (8 * _mpi.COMM_WORLD.size,),
                halo=((2, 4),),
                mem_alloc_topology=mnt
            )

        decomp.root_logger.info("START " + self.id())
        decomp.root_logger.info(str(decomp))
        decomp.root_logger.info("END   " + self.id())

    def test_construct_1d_empty_tiles(self):
        """
        Test :obj:`mpi_array.decomposition.CartesianDecomposition` construction
        when the partition leads to empty tiles.
        """
        if (_mpi.COMM_WORLD.size > 1):
            decomp = CartesianDecomposition((_mpi.COMM_WORLD.size // 2,), halo=0)
            self.assertNotEqual(None, decomp._mem_alloc_topology)

            mnt = MemAllocTopology(ndims=1, shared_mem_comm=_mpi.COMM_SELF)
            decomp = \
                CartesianDecomposition(
                    (_mpi.COMM_WORLD.size // 2,),
                    halo=0,
                    mem_alloc_topology=mnt
                )

            decomp.root_logger.info("START " + self.id())
            decomp.root_logger.info(str(decomp))
            decomp.root_logger.info("END   " + self.id())

    def test_construct_2d(self):
        """
        Test :obj:`mpi_array.decomposition.CartesianDecomposition` construction.
        """
        decomp = CartesianDecomposition((8 * _mpi.COMM_WORLD.size, 12 * _mpi.COMM_WORLD.size))
        self.assertNotEqual(None, decomp._mem_alloc_topology)

        mnt = MemAllocTopology(ndims=2, shared_mem_comm=_mpi.COMM_SELF)
        decomp = \
            CartesianDecomposition(
                (8 * _mpi.COMM_WORLD.size, 12 * _mpi.COMM_WORLD.size),
                mem_alloc_topology=mnt
            )

        decomp.root_logger.info("START " + self.id())
        decomp.root_logger.info(str(decomp))
        decomp.root_logger.info("END   " + self.id())

    def test_construct_2d_with_halo(self):
        """
        Test :obj:`mpi_array.decomposition.CartesianDecomposition` construction.
        """
        decomp = \
            CartesianDecomposition(
                (8 * _mpi.COMM_WORLD.size, 12 * _mpi.COMM_WORLD.size),
                halo=((2, 2), (4, 4))
            )
        self.assertNotEqual(None, decomp._mem_alloc_topology)

        mnt = MemAllocTopology(ndims=2, shared_mem_comm=_mpi.COMM_SELF)
        decomp = \
            CartesianDecomposition(
                (8 * _mpi.COMM_WORLD.size, 12 * _mpi.COMM_WORLD.size),
                halo=((1, 2), (3, 4)),
                mem_alloc_topology=mnt
            )

        root_logger = _logging.get_root_logger(self.id(), comm=decomp.rank_comm)
        root_logger.info("START " + self.id())
        root_logger.info(str(decomp))
        root_logger.info("END   " + self.id())

    def test_recalculate_2d(self):
        """
        Test :meth:`mpi_array.decomposition.CartesianDecomposition.recalculate` construction.
        """
        mats = \
            [
                None,
                MemAllocTopology(
                    ndims=2,
                    rank_comm=_mpi.COMM_WORLD,
                    shared_mem_comm=_mpi.COMM_SELF
                )
            ]
        for mat in mats:
            orig_shape = (8 * _mpi.COMM_WORLD.size, 12 * _mpi.COMM_WORLD.size)
            decomp = \
                CartesianDecomposition(
                    orig_shape,
                    mem_alloc_topology=mat,
                    halo=((2, 2), (4, 4))
                )

            self.assertSequenceEqual([[2, 2], [4, 4]], decomp.halo.tolist())

            decomp.halo = [[1, 2], [3, 4]]
            self.assertSequenceEqual([[1, 2], [3, 4]], decomp.halo.tolist())

            self.assertSequenceEqual(list(orig_shape), decomp.shape.tolist())
            new_shape = (10 * _mpi.COMM_WORLD.size, 7 * _mpi.COMM_WORLD.size)
            decomp.shape = new_shape
            self.assertSequenceEqual(list(new_shape), decomp.shape.tolist())


_unittest.main(__name__)


__all__ = [s for s in dir() if not s.startswith('_')]
