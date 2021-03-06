"""
======================================
The :mod:`mpi_array.unittest` Module
======================================

Some simple wrappers of python built-in :mod:`unittest` module
for :mod:`mpi_array` unit-tests.

Classes and Functions
=====================

.. autosummary::
   :toctree: generated/
   :template: autosummary/inherits_TestCase_class.rst

   TestCase - Extends :obj:`unittest.TestCase` with :obj:`TestCase.assertArraySplitEqual`.

.. autosummary::
   :toctree: generated/

   TestProgram - Over-ride to use :obj:`logging.Logger` output.
   TextTestRunner - Over-ride to use :obj:`logging.Logger` output.
   TextTestResult - Over-ride to use :obj:`logging.Logger` output.
   main - Convenience command-line test-case *search and run* function.

"""
from __future__ import absolute_import

import unittest as _builtin_unittest
import mpi_array.logging
import numpy as _np
import mpi4py.MPI as _mpi
import time as _time
import warnings as _warnings


def _fix_docstring_for_sphinx(docstr):
    lines = docstr.split("\n")
    for i in range(len(lines)):
        if lines[i].find(" " * 8) == 0:
            lines[i] = lines[i][8:]
    return "\n".join(lines)


class TestCase(_builtin_unittest.TestCase):

    """
    Extends :obj:`unittest.TestCase` with the :meth:`assertArraySplitEqual`.
    """

    def assertArraySplitEqual(self, splt1, splt2):
        """
        Compares :obj:`list` of :obj:`numpy.ndarray` results returned by :func:`numpy.mpi_array`
        and :func:`mpi_array.split.mpi_array` functions.

        :type splt1: :obj:`list` of :obj:`numpy.ndarray`
        :param splt1: First object in equality comparison.
        :type splt2: :obj:`list` of :obj:`numpy.ndarray`
        :param splt2: Second object in equality comparison.
        :raises unittest.AssertionError: If any element of :samp:`{splt1}` is not equal to
            the corresponding element of :samp:`splt2`.
        """
        self.assertEqual(len(splt1), len(splt2))
        for i in range(len(splt1)):
            self.assertTrue(
                (
                    _np.all(_np.array(splt1[i]) == _np.array(splt2[i]))
                    or
                    ((_np.array(splt1[i]).size == 0) and (_np.array(splt2[i]).size == 0))
                ),
                msg=(
                    "element %d of split is not equal %s != %s"
                    %
                    (i, _np.array(splt1[i]), _np.array(splt2[i]))
                )
            )

    #
    # Method over-rides below are just to avoid sphinx warnings
    #
    def assertItemsEqual(self, *args, **kwargs):
        """
        See :obj:`unittest.TestCase.assertItemsEqual`.
        """
        _builtin_unittest.TestCase.assertItemsEqual(self, *args, **kwargs)

    def assertListEqual(self, *args, **kwargs):
        """
        See :obj:`unittest.TestCase.assertListEqual`.
        """
        _builtin_unittest.TestCase.assertListEqual(self, *args, **kwargs)

    def assertRaisesRegexp(self, *args, **kwargs):
        """
        See :obj:`unittest.TestCase.assertRaisesRegexp`.
        """
        _builtin_unittest.TestCase.assertRaisesRegexp(self, *args, **kwargs)

    def assertRaisesRegex(self, *args, **kwargs):
        """
        See :obj:`unittest.TestCase.assertRaisesRegex`.
        """
        _builtin_unittest.TestCase.assertRaisesRegex(self, *args, **kwargs)

    def assertSetEqual(self, *args, **kwargs):
        """
        See :obj:`unittest.TestCase.assertSetEqual`.
        """
        _builtin_unittest.TestCase.assertSetEqual(self, *args, **kwargs)

    def assertTupleEqual(self, *args, **kwargs):
        """
        See :obj:`unittest.TestCase.assertTupleEqual`.
        """
        _builtin_unittest.TestCase.assertTupleEqual(self, *args, **kwargs)

    def assertWarnsRegex(self, *args, **kwargs):
        """
        See :obj:`unittest.TestCase.assertWarnsRegex`.
        """
        _builtin_unittest.TestCase.assertWarnsRegex(self, *args, **kwargs)


if not hasattr(TestCase, "assertSequenceEqual"):
    # code from python-2.7 unitest.case.TestCase
    _MAX_LENGTH = 80

    def safe_repr(obj, short=False):
        try:
            result = repr(obj)
        except Exception:
            result = object.__repr__(obj)
        if not short or len(result) < _MAX_LENGTH:
            return result
        return result[:_MAX_LENGTH] + ' [truncated]...'

    def strclass(cls):
        return "%s.%s" % (cls.__module__, cls.__name__)

    def assertSequenceEqual(self, seq1, seq2, msg=None, seq_type=None):
        """An equality assertion for ordered sequences (like lists and tuples).

        For the purposes of this function, a valid ordered sequence type is one
        which can be indexed, has a length, and has an equality operator.

        :param seq1: The first sequence to compare.
        :param seq2: The second sequence to compare.
        :param seq_type: The expected datatype of the sequences, or None if no
                    datatype should be enforced.
        :param msg: Optional message to use on failure instead of a list of
                    differences.
        """

        import pprint
        import difflib
        if seq_type is not None:
            seq_type_name = seq_type.__name__
            if not isinstance(seq1, seq_type):
                raise self.failureException('First sequence is not a %s: %s'
                                            % (seq_type_name, safe_repr(seq1)))
            if not isinstance(seq2, seq_type):
                raise self.failureException('Second sequence is not a %s: %s'
                                            % (seq_type_name, safe_repr(seq2)))
        else:
            seq_type_name = "sequence"

        differing = None
        try:
            len1 = len(seq1)
        except (TypeError, NotImplementedError):
            differing = 'First %s has no length.    Non-sequence?' % (
                seq_type_name)

        if differing is None:
            try:
                len2 = len(seq2)
            except (TypeError, NotImplementedError):
                differing = 'Second %s has no length.    Non-sequence?' % (
                    seq_type_name)

        if differing is None:
            if seq1 == seq2:
                return

            seq1_repr = safe_repr(seq1)
            seq2_repr = safe_repr(seq2)

            if len(seq1_repr) > 30:
                seq1_repr = seq1_repr[:30] + '...'
            if len(seq2_repr) > 30:
                seq2_repr = seq2_repr[:30] + '...'
            elements = (seq_type_name.capitalize(), seq1_repr, seq2_repr)
            differing = '%ss differ: %s != %s\n' % elements

            for i in range(min(len1, len2)):
                try:
                    item1 = seq1[i]
                except (TypeError, IndexError, NotImplementedError):
                    differing += ('\nUnable to index element %d of first %s\n' %
                                  (i, seq_type_name))
                    break

                try:
                    item2 = seq2[i]
                except (TypeError, IndexError, NotImplementedError):
                    differing += ('\nUnable to index element %d of second %s\n' %
                                  (i, seq_type_name))
                    break

                if item1 != item2:
                    differing += ('\nFirst differing element %d:\n%s\n%s\n' %
                                  (i, item1, item2))
                    break
            else:
                if (len1 == len2 and seq_type is None and
                        not isinstance(seq1, type(seq2))):
                    # The sequences are the same, but have differing types.
                    return

            if len1 > len2:
                differing += ('\nFirst %s contains %d additional '
                              'elements.\n' % (seq_type_name, len1 - len2))
                try:
                    differing += ('First extra element %d:\n%s\n' %
                                  (len2, seq1[len2]))
                except (TypeError, IndexError, NotImplementedError):
                    differing += ('Unable to index element %d '
                                  'of first %s\n' % (len2, seq_type_name))
            elif len1 < len2:
                differing += ('\nSecond %s contains %d additional '
                              'elements.\n' % (seq_type_name, len2 - len1))
                try:
                    differing += ('First extra element %d:\n%s\n' %
                                  (len1, seq2[len1]))
                except (TypeError, IndexError, NotImplementedError):
                    differing += ('Unable to index element %d '
                                  'of second %s\n' % (len1, seq_type_name))
        standardMsg = differing
        diffMsg = '\n' + '\n'.join(
            difflib.ndiff(pprint.pformat(seq1).splitlines(),
                          pprint.pformat(seq2).splitlines()))
        standardMsg = self._truncateMessage(standardMsg, diffMsg)
        msg = self._formatMessage(msg, standardMsg)
        self.fail(msg)

    def _formatMessage(self, msg, standardMsg):
        """Honour the longMessage attribute when generating failure messages.
        If longMessage is False this means:
        * Use only an explicit message if it is provided
        * Otherwise use the standard message for the assert

        If longMessage is True:
        * Use the standard message
        * If an explicit message is provided, plus ' : ' and the explicit message
        """
        if not self.longMessage:
            return msg or standardMsg
        if msg is None:
            return standardMsg
        try:
            # don't switch to '{}' formatting in Python 2.X
            # it changes the way unicode input is handled
            return '%s : %s' % (standardMsg, msg)
        except UnicodeDecodeError:
            return '%s : %s' % (safe_repr(standardMsg), safe_repr(msg))

    def _truncateMessage(self, message, diff):
        DIFF_OMITTED = ('\nDiff is %s characters long. '
                        'Set self.maxDiff to None to see it.')

        max_diff = self.maxDiff
        if max_diff is None or len(diff) <= max_diff:
            return message + diff
        return message + (DIFF_OMITTED % len(diff))

    _maxDiff = 80 * 8
    setattr(TestCase, "maxDiff", _maxDiff)
    setattr(TestCase, "_truncateMessage", _truncateMessage)
    setattr(TestCase, "_formatMessage", _formatMessage)
    setattr(TestCase, "assertSequenceEqual", assertSequenceEqual)
else:

    def assertSequenceEqual(self, *args, **kwargs):
        """
        See :obj:`unittest.TestCase.assertSequenceEqual`.
        """
        _builtin_unittest.TestCase.assertSequenceEqual(self, *args, **kwargs)

    setattr(TestCase, "assertSequenceEqual", assertSequenceEqual)


class LoggerDecorator:

    """
    Decorator for :obj:`logging.Logger` to provide :meth:`write`, :meth:`writeln`
    and :meth:`flush` methods.
    """

    def __init__(self, logger):
        self.logger = logger

    def write(self, v=""):
        self.logger.info(v)

    def writeln(self, v=""):
        self.logger.info(v)

    def write_error(self, v):
        self.logger.error(v)

    def flush(self):
        pass


class TextTestResult(_builtin_unittest.TextTestResult):

    """
    """

    def startTest(self, test):
        _builtin_unittest.result.TestResult.startTest(self, test)
        if self.showAll:
            self.stream.write(self.getDescription(test) + "...")
            self.stream.flush()

    def addSuccess(self, test):
        _builtin_unittest.result.TestResult.addSuccess(self, test)
        if self.showAll:
            self.stream.write(self.getDescription(test) + "..." + "ok")
        elif self.dots:
            self.stream.write('.')
            self.stream.flush()

    def addError(self, test, err):
        _builtin_unittest.result.TestResult.addError(self, test, err)
        if self.showAll:
            self.stream.write_error("ERROR")
        elif self.dots:
            self.stream.write_error('E')
            self.stream.flush()

    def addFailure(self, test, err):
        _builtin_unittest.result.TestResult.addFailure(self, test, err)
        if self.showAll:
            self.stream.write_error("FAIL")
        elif self.dots:
            self.stream.write_error('F')
            self.stream.flush()

    def addSkip(self, test, reason):
        _builtin_unittest.result.TestResult.addSkip(self, test, reason)
        if self.showAll:
            self.stream.write("skipped {0!r}".format(reason))
        elif self.dots:
            self.stream.write("s")
            self.stream.flush()

    def addExpectedFailure(self, test, err):
        _builtin_unittest.result.TestResult.addExpectedFailure(self, test, err)
        if self.showAll:
            self.stream.write("expected failure")
        elif self.dots:
            self.stream.write("x")
            self.stream.flush()

    def addUnexpectedSuccess(self, test):
        _builtin_unittest.result.TestResult.addUnexpectedSuccess(self, test)
        if self.showAll:
            self.stream.write("unexpected success")
        elif self.dots:
            self.stream.write("u")
            self.stream.flush()

    def printErrors(self):
        if self.dots or self.showAll:
            self.stream.write()
        self.printErrorList('ERROR', self.errors)
        self.printErrorList('FAIL', self.failures)

    def printErrorList(self, flavour, errors):
        for test, err in errors:
            self.stream.write_error(self.separator1)
            self.stream.write_error("%s: %s" % (flavour, self.getDescription(test)))
            self.stream.write_error(self.separator2)
            self.stream.write_error("%s" % err)


def handle_arg(arg_index, arg_key, arg_value, args, kwargs):
    """
    Replace an argument with a specified value if it does not
    appear in :samp:`{args}` or :samp:`{kwargs}` argument list.

    :type arg_index: :obj:`int`
    :param arg_index: Index of argument in :samp:`{args}`
    :type arg_key: :obj:`str`
    :param arg_index: String key of argument in :samp:`{kwargs}`
    :type arg_value: :obj:`object`
    :param arg_value: Value for argument if it does not appear in argument
       lists or has :samp:`None` value in argument lists.
    :type args: :obj:`list`
    :param args: List of arguments.
    :type kwargs: :obj:`dict`
    :param kwargs: Dictionary of key-word arguments.
    """
    a = None
    if len(args) > arg_index:
        a = args[arg_index]
    if arg_key in kwargs.keys():
        a = kwargs[arg_key]

    if a is None:
        a = arg_value

    if len(args) > arg_index:
        args[arg_index] = a
    if arg_key in kwargs.keys():
        kwargs[arg_key] = a
    if (len(args) <= arg_index) and (arg_key not in kwargs.keys()):
        kwargs[arg_key] = a

    return a


class TextTestRunner(_builtin_unittest.TextTestRunner):

    """
    A test runner class that displays results in textual form.

    Extends :obj:`unittest.TextTestRunner` with logging output
    instead of :obj:`sys.stderr` output.
    """

    def __init__(self, *args, **kwargs):

        handle_arg(5, "resultclass", TextTestResult, args, kwargs)
        verbosity = handle_arg(2, "verbosity", 0, args, kwargs)

        logger_name = __name__ + ".TextTestRunner"
        logger = mpi_array.logging.get_rank_logger(logger_name)
        log_level = mpi_array.logging.WARN
        if verbosity <= 1:
            if _mpi.COMM_WORLD.rank == 0:
                log_level = mpi_array.logging.INFO
        else:
            log_level = mpi_array.logging.INFO
        mpi_array.logging.initialise_loggers([logger_name, ], log_level)
        stream = LoggerDecorator(logger)

        handle_arg(0, "stream", stream, args, kwargs)

        _builtin_unittest.TextTestRunner.__init__(self, *args, **kwargs)

        # Remove _WritelnDecorator decoration for LoggerDecorator
        if hasattr(self.stream, "stream") and isinstance(self.stream.stream, LoggerDecorator):
            self.stream = self.stream.stream

        if not hasattr(self, "warnings"):
            self.warnings = None

    def run(self, test):
        """
        Run the given test case or test suite.
        """
        result = self._makeResult()
        _builtin_unittest.registerResult(result)
        result.failfast = self.failfast
        result.buffer = self.buffer
        with _warnings.catch_warnings():
            if self.warnings:
                # if self.warnings is set, use it to filter all the warnings
                _warnings.simplefilter(self.warnings)
                # if the filter is 'default' or 'always', special-case the
                # warnings from the deprecated unittest methods to show them
                # no more than once per module, because they can be fairly
                # noisy.  The -Wd and -Wa flags can be used to bypass this
                # only when self.warnings is None.
                if self.warnings in ['default', 'always']:
                    _warnings.filterwarnings(
                        'module',
                        category=DeprecationWarning,
                        message='Please use assert\w+ instead.'
                    )
            startTime = _time.time()
            startTestRun = getattr(result, 'startTestRun', None)
            if startTestRun is not None:
                startTestRun()
            try:
                test(result)
            finally:
                stopTestRun = getattr(result, 'stopTestRun', None)
                if stopTestRun is not None:
                    stopTestRun()
            stopTime = _time.time()
        timeTaken = stopTime - startTime
        result.printErrors()
        if hasattr(result, 'separator2'):
            self.stream.writeln(result.separator2)
        run = result.testsRun
        self.stream.writeln("Ran %d test%s in %.3fs (COMM_WORLD.size=%3d)" %
                            (run, run != 1 and "s" or "", timeTaken, _mpi.COMM_WORLD.size))
        self.stream.writeln()

        expectedFails = unexpectedSuccesses = skipped = 0
        try:
            results = map(len, (result.expectedFailures,
                                result.unexpectedSuccesses,
                                result.skipped))
        except AttributeError:
            pass
        else:
            expectedFails, unexpectedSuccesses, skipped = results

        infos = []
        if not result.wasSuccessful():
            self.stream.write("FAILED")
            failed, errored = len(result.failures), len(result.errors)
            if failed:
                infos.append("failures=%d" % failed)
            if errored:
                infos.append("errors=%d" % errored)
        else:
            self.stream.write("OK")
        if skipped:
            infos.append("skipped=%d" % skipped)
        if expectedFails:
            infos.append("expected failures=%d" % expectedFails)
        if unexpectedSuccesses:
            infos.append("unexpected successes=%d" % unexpectedSuccesses)
        if infos:
            self.stream.writeln(" (%s)" % (", ".join(infos),))
        else:
            self.stream.write("\n")
        return result


class TestProgram(_builtin_unittest.TestProgram):

    """
    A command-line program that runs a set of tests, extends :obj:`unittest.TestProgram`
    by using logging rather than standard stream.
    """

    def __init__(self, *args, **kwargs):
        handle_arg(3, "testRunner", TextTestRunner, args, kwargs)
        _builtin_unittest.TestProgram.__init__(self, *args, **kwargs)


def main(
    module_name,
    log_level=mpi_array.logging.DEBUG,
    init_logger_names=None,
    verbosity=None,
    failfast=None
):
    """
    Like :func:`unittest.main`, initialises :mod:`logging.Logger` objects
    and instantiates a :obj:`TestProgram` to discover and run :obj:`TestCase` objects.
    Loads a set of tests from module and runs them;
    this is primarily for making test modules conveniently executable.
    The simplest use for this function is to include the following line at
    the end of a test module::

       mpi_array.unittest.main(__name__)

    If :samp:`__name__ == "__main__"`, then *discoverable* :obj:`unittest.TestCase`
    test cases are executed.
    Logging level can be explicitly set for a group of modules using::

       import logging

       mpi_array.unittest.main(
           __name__,
           logging.DEBUG,
           [__name__, "module_name_0", "module_name_1", "package.module_name_2"]
       )


    :type module_name: :obj:`str`
    :param module_name: If :samp:`{module_name} == "__main__"` then unit-tests
       are *discovered* and run.
    :type log_level: :obj:`int`
    :param log_level: The default logging level for all
       :obj:`mpi_array.logging.Logger` objects.
    :type init_logger_names: sequence of :obj:`str`
    :param init_logger_names: List of logger names to initialise
       (using :func:`mpi_array.logging.initialise_loggers`). If :samp:`None`,
       then the list defaults to :samp:`[{module_name}, "mpi_array"]`. If list
       is empty no loggers are initialised.

    """
    if module_name == "__main__":
        if (init_logger_names is None):
            init_logger_names = [module_name, "mpi_array"]

        if (len(init_logger_names) > 0):
            mpi_array.logging.initialise_loggers(
                init_logger_names, log_level=log_level)

        kwargs = dict()
        if failfast is not None:
            kwargs["failfast"] = failfast
        if verbosity is not None:
            kwargs["verbosity"] = verbosity

        TestProgram(**kwargs)


__all__ = [s for s in dir() if not s.startswith('_')]
