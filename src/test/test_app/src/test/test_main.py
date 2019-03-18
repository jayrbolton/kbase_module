import kbase_module
import unittest


class TestMain(unittest.TestCase):

    def test_echo(self):
        """Test the echo function."""
        message = "Hello world!"
        result = kbase_module.run_method('echo', {'message': message})
        self.assertEqual(result, message)

    def test_echo_invalid_params(self):
        """Test the case where we don't pass the 'message' param."""
        with self.assertRaises(RuntimeError) as context:
            kbase_module.run_method('echo', {})
        msg = "'message' is a required property"
        self.assertTrue(msg in str(context.exception))
