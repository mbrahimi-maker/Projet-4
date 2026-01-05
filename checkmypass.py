import requests
import sys
import hashlib


class check:
    def request_api_data(self, first_five_char):
        """
        Fetches data from the Pwned Passwords API using the first five characters of the SHA-1 hash.
        Raises a RuntimeError for non-200 status codes.

        :param first_five_char: First five characters of the hashed password.
        :return: API response.
        """
        url = "https://api.pwnedpasswords.com/range/" + first_five_char
        res = requests.get(url)
        if res.status_code != 200:
            raise RuntimeError(f"Error fetching: {res.status_code}, check the API.")
        return res


    def pwned_api_check(self,password):
        """
        Hashes the given password using SHA1, queries the Pwned Passwords API, and checks for password leaks.

        :param password: The password to hash and check.
        :return: The number of times the password was found in the Pwned Passwords database.
        """
        sha1password = hashlib.sha256(password.encode("utf-8")).hexdigest().upper()
        first5_char, tail = sha1password[:5], sha1password[5:]
        response = self.request_api_data(first5_char)
        return self.get_password_leaks_count(response, tail)


    def get_password_leaks_count(self, hashes, hash_to_check):
        """
        Checks the number of leaks for a given hash.

        :param hashes: API response containing hash records.
        :param hash_to_check: Hash to search for.
        :return: Number of matches found.
        """
        hashes = (line.split(":") for line in hashes.text.splitlines())
        for h, count in hashes:
            if h == hash_to_check:
                return count
        return 0


    def main(self, passwords):
        """
        Checks passwords for compromise and prints results.

        :param args: List of passwords to check.
        :return: Completion status.
        """
        count = self.pwned_api_check(passwords)
        if count:   
            return False
        else:
            return True



if __name__ == "__main__":
    check = check()
    sys.exit(check.main(sys.argv[1:]))
