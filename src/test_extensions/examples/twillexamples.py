from test_extensions.twill import TwillCommon

class TwillExample(TwillCommon):
    """
    Example Twill tests using the TwillCommon class.
    """

    # set a global url. Note you might do this from a settings file.
    url = "http://www.example.com/"

    def test_for_200_status_code(self):
        "Does the provided url return an HTTP status code of 200"
        self.code("200")

    def test_for_h1(self):
        "Does the url return content which matches the given regex"
        self.find("<h1(.*)<\/h1>")