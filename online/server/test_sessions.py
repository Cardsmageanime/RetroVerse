import unittest
from sessions import SessionRegistry

class SessionTests(unittest.TestCase):
    def test_expiration(self):
        clock=[10]
        registry=SessionRegistry(clock=lambda:clock[0],ttl=5)
        registry.create("client",12)
        self.assertEqual(registry.user("client"),12)
        clock[0]=15
        self.assertIsNone(registry.user("client"))
    def test_logout_revoke(self):
        registry=SessionRegistry()
        registry.create("client",14)
        registry.revoke("client")
        self.assertIsNone(registry.user("client"))
    def test_replace_existing(self):
        registry=SessionRegistry()
        first=registry.create("client",14)
        second=registry.create("client",15)
        self.assertNotEqual(first,second)
        self.assertEqual(registry.user("client"),15)
if __name__=="__main__":unittest.main()
