import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import Mock, patch

import osgint


class OsgintTests(unittest.TestCase):
    def setUp(self):
        osgint.jsonOutput.clear()
        osgint.fileJsonOutput.clear()
        osgint.Output.clear()
        osgint.emailOutput.clear()

    @patch("osgint.requests.get")
    def test_batch_profile_keeps_repository_count(self, get):
        get.return_value = Mock(
            status_code=200,
            json=lambda: {
                "login": "octocat",
                "public_repos": 8,
                "public_gists": 4,
            },
        )

        self.assertTrue(osgint.findInfoFromUsername("octocat", batch=True))
        result = osgint.fileJsonOutput["octocat"]

        self.assertEqual(result["public_repos"], 8)
        self.assertEqual(result["public_gists"], "https://gist.github.com/octocat")

    @patch("osgint.requests.get")
    def test_api_error_is_recorded_in_batch_output(self, get):
        get.return_value = Mock(status_code=403)

        self.assertFalse(osgint.findInfoFromUsername("octocat", batch=True))
        self.assertEqual(
            osgint.fileJsonOutput["octocat"]["error"],
            "GitHub API request failed with status 403",
        )

    @patch("osgint.requests.get")
    def test_repository_lookup_uses_api_data(self, get):
        get.return_value = Mock(
            status_code=200,
            json=lambda: [
                {"name": "original", "fork": False},
                {"name": "forked", "fork": True},
            ],
        )

        self.assertEqual(osgint.findReposFromUsername("octocat"), ["original"])

    @patch("osgint.requests.get")
    def test_email_lookup_uses_encoded_query_parameters(self, get):
        get.return_value = Mock(
            status_code=200,
            json=lambda: {"items": [{"login": "octocat"}]},
        )

        osgint.findUsernameFromEmail("person+tag@example.com")

        self.assertEqual(osgint.jsonOutput["username"], "octocat")
        get.assert_called_once_with(
            "https://api.github.com/search/users",
            params={"q": "person+tag@example.com"},
        )

    @patch("osgint.fullScan")
    @patch("osgint.findInfoFromUsername", return_value=True)
    def test_input_file_ignores_empty_lines_and_whitespace(self, find_info, full_scan):
        with tempfile.TemporaryDirectory() as directory:
            input_path = Path(directory) / "usernames.txt"
            output_path = Path(directory) / "result.json"
            input_path.write_text(" octocat \n\n  torvalds\t\n", encoding="utf-8")

            osgint.findInfoFromFile(input_path, output_path)

            self.assertEqual(
                [call.args for call in find_info.call_args_list],
                [("octocat",), ("torvalds",)],
            )
            self.assertTrue(
                all(call.kwargs == {"batch": True} for call in find_info.call_args_list)
            )
            self.assertEqual(json.loads(output_path.read_text()), {})
            self.assertEqual(full_scan.call_count, 2)

    def test_cli_inputs_are_mutually_exclusive(self):
        with self.assertRaises(SystemExit) as error, patch("sys.stderr"):
            osgint.parse_args(["--username", "octocat", "--input", "users.txt"])

        self.assertEqual(error.exception.code, 2)

    @patch("osgint.findPublicKeysFromUsername")
    @patch("osgint.findEmailFromUsername")
    def test_full_scan_does_not_depend_on_global_args(self, find_email, find_keys):
        osgint.jsonOutput["login"] = "octocat"

        with patch("builtins.print"):
            osgint.fullScan("octocat", json_mode=True)

        self.assertEqual(osgint.jsonOutput["email"], [])
        find_email.assert_called_once_with("octocat")
        find_keys.assert_called_once_with("octocat", False)


if __name__ == "__main__":
    unittest.main()
