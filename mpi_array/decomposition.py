"""
=========================================
The :mod:`mpi_array.decomposition` Module
=========================================

Sub-division of arrays over nodes and/or MPI processes.

Classes and Functions
=====================

.. autosummary::
   :toctree: generated/

   SharedMemInfo - Shared-memory communicator generation.
   MemNodeTopology - Topology of MPI processes which allocate shared memory.
   Decomposition - Partition of an array *shape* overs MPI processes and/or nodes.


"""
from __future__ import absolute_import
from .license import license as _license, copyright as _copyright
import pkg_resources as _pkg_resources
import mpi4py.MPI as _mpi
import array_split as _array_split
import array_split.split  # noqa: F401
import numpy as _np

__author__ = "Shane J. Latham"
__license__ = _license()
__copyright__ = _copyright()
__version__ = _pkg_resources.resource_string("mpi_array", "version.txt").decode()


class SharedMemInfo(object):
    """
    Info on possible shared memory allocation for a specified MPI communicator.
    """

    def __init__(self, comm, shared_mem_comm=None):
        if shared_mem_comm is None:
            if hasattr(_mpi, "COMM_TYPE_SHARED"):
                shared_mem_comm = comm.Split_type(_mpi.COMM_TYPE_SHARED, key=comm.rank)
            else:
                shared_mem_comm = comm.Split(comm.rank, key=comm.rank)

        self.shared_mem_comm = shared_mem_comm

        # Count the number of self.shared_mem_comm rank-0 processes
        # to work out how many communicators comm was split into.
        is_rank_zero = 0
        if self.shared_mem_comm.rank == 0:
            is_rank_zero = 1
        self.num_shared_mem_nodes = comm.allreduce(is_rank_zero, _mpi.SUM)


class MemNodeTopology(object):
    """
    Defines cartesian communication topology for MPI processes.
    """

    def __init__(
        self,
        ndims=None,
        dims=None,
        periods=None,
        rank_comm=None,
        shared_mem_comm=None
    ):
        """
        Create a partitioning of :samp:`{shape}` over mem-nodes.

        :type dims: sequence of :obj:`int`
        :param dims: The number of partitions along each array axis, zero elements
           are replaced with positive integers such
           that :samp:`numpy.product({dims}) == {rank_comm}.size`.
        :type periods: sequence of :obj:`bool`
        :param periods: Indicates the axes which are periodic.
        :type rank_comm: :obj:`mpi4py.MPI.Comm`
        :param rank_comm: The MPI processes over which an array is to be distributed.
        :type shared_mem_comm: :obj:`mpi4py.MPI.Comm`
        :param shared_mem_comm: The MPI communicator used to allocate shared memory
            via :obj:`mpi4py.MPI.Win.Allocate_shared`.
        """
        if (ndims is None) and (dims is None):
            raise ValueError("Must specify one of dims or ndims in MemNodeTopology constructor.")
        elif (ndims is not None) and (dims is not None) and (len(dims) != ndims):
            raise ValueError(
                "Length of dims (len(dims)=%s) not equal to ndims=%s." % (len(dims), ndims)
            )
        elif ndims is None:
            ndims = len(dims)

        if dims is None:
            dims = _np.zeros((ndims,), dtype="int")
        if periods is None:
            periods = _np.zeros((ndims,), dtype="bool")
        if rank_comm is None:
            rank_comm = _mpi.COMM_WORLD

        self.rank_comm = rank_comm
        self.shared_mem_info = SharedMemInfo(self.rank_comm, shared_mem_comm)
        self.cart_comm = None

        self.dims = \
            _array_split.split.calculate_num_slices_per_axis(
                dims,
                self.shared_mem_info.num_shared_mem_nodes
            )

        # Create a cartesian grid communicator
        if self.shared_mem_info.num_shared_mem_nodes > 1:
            color = _mpi.UNDEFINED
            if self.shared_mem_info.shared_mem_comm.rank == 0:
                color = 0
            splt_comm = self.rank_comm.Split(color, self.rank_comm.rank)
            if splt_comm != _mpi.COMM_NULL:
                self.cart_comm = splt_comm.Create_cart(self.dims, periods, reorder=True)
            else:
                self.cart_comm = _mpi.COMM_NULL


class Decomposition(object):
    """
    Partitions an array shape over MPI processes and/or mem-nodes.
    """

    def __init__(
        self,
        shape,
        halo=0,
        mem_node_topology=None,
    ):
        """
        Create a partitioning of :samp:`{shape}` over mem-nodes.

        :type shape: sequence of :obj:`int`
        :param shape: The shape of the array which is to be partitioned into smaller *sub-shapes*.
        :type halo: :obj:`int`, sequence of :obj:`int` or :samp:`(len(shape), 2)` shaped array.
        :param dims: The number of partitions along each array axis, zero elements
           are replaced with positive integers such
           that :samp:`numpy.product({dims}) == {rank_comm}.size`.
        """
        self.shape = _np.array(shape)
        if mem_node_topology is None:
            mem_node_topology = MemNodeTopology(ndims=self.shape.size)

        self.mem_node_topology = mem_node_topology
        shape_spliter = \
            _array_split.ShapeSplitter(
                array_shape=self.shape,
                axis=self.mem_node_topology.dims,
                halo=halo
            )

        self.shape_decomp = shape_spliter.calculate_split()


__all__ = [s for s in dir() if not s.startswith('_')]
