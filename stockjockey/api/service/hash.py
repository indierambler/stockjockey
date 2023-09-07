import bcrypt
from sqlalchemy import Text, TypeDecorator
from sqlalchemy.orm import validates
from sqlalchemy.ext.mutable import Mutable
from .. import db


class Password(TypeDecorator):
    """Allows storing and retrieving password hashes using PasswordHash
    - this is the type to be used for each password column
    """
    impl = Text

    def __init__(self, rounds=12, **kwds):
        self.rounds = rounds
        super().__init__(**kwds)  # run inits on inherited classes

    def process_bind_param(self, value, dialect):
        """Ensure the value is a PasswordHash and then return its hash as string.
        - converts PasswordHash object to a value suitable for the implementor type
        """
        return self._convert(value).hash

    def process_result_value(self, value, dialect):
        """Convert the hash to a PasswordHash, if it's non-NULL.
        - converts the value from the db to PasswordHash for use in the python runtime
        """
        if value is not None:
            return PasswordHash(value, rounds=self.rounds)

    def validator(self, password):
        """Provides a validator/converter for @validates usage."""
        return self._convert(password)

    def _convert(self, value):
        """Returns a PasswordHash from the given string.

        PasswordHash instances or None values will return unchanged.
        Strings will be hashed and the resulting PasswordHash returned.
        Any other input will result in a TypeError.
        """
        if isinstance(value, PasswordHash):
            return value
        elif isinstance(value, str):
            return PasswordHash.new(value, self.rounds)
        elif value is not None:
            raise TypeError(
                'Cannot convert {} to a PasswordHash'.format(type(value)))


class PasswordHash(Mutable):
    """Define a hash scheme for a password
    - self.hash_ is the decoded bcrypt hash of the password
    - self.hash is the string representation of the password hash (to be saved in db)
    - the "new" method is to create a bcrypt hash from a plaintext password string
    - a new instance of PasswordHash creates a proper object from an existing hash string
    """
    def __init__(self, hash_, rounds=None):
        assert len(hash_) == 60, f'bcrypt hash with length:{len(hash_)} should be 60 chars.'
        assert hash_.count('$'), 'bcrypt hash should have 3x "$".'
        self.hash = str(hash_)
        self.rounds = int(self.hash.split('$')[2])
        self.desired_rounds = rounds or self.rounds

    def __eq__(self, candidate):
        """Hashes the candidate string and compares it to the stored hash.

        If the current and desired number of rounds differ, the password is
        re-hashed with the desired number of rounds and updated with the results.
        This will also mark the object as having changed (and thus need updating).
        """
        self.hash_ = self.hash.encode('UTF-8')
        if isinstance(candidate, str):
            candidate = candidate.encode('UTF-8')
            if self.hash_ == bcrypt.hashpw(candidate, self.hash_):
                if self.rounds < self.desired_rounds:
                    self._rehash(candidate)
                return True
        return False

    def __repr__(self):
        """Simple object representation."""
        return '<{}>'.format(type(self).__name__)

    @classmethod
    def coerce(cls, key, value):
        """Ensure that loaded values are PasswordHashes."""
        if isinstance(value, PasswordHash):
            return value
        return super(PasswordHash, cls).coerce(key, value)

    @classmethod
    def new(cls, password, rounds):
        """Returns a new PasswordHash object for the given password string and rounds."""
        password = password.encode('UTF-8')
        return cls(cls._new(password, rounds))

    @staticmethod
    def _new(password, rounds):
        """Returns a new bcrypt hash for the given password and rounds."""
        return bcrypt.hashpw(password, bcrypt.gensalt(rounds)).decode('UTF-8')

    def _rehash(self, password):
        """Recreates the internal hash and marks the object as changed."""
        self.hash = self._new(password, self.desired_rounds)
        self.rounds = self.desired_rounds
        self.changed()


class HasPassword(object):
    """Mixin class for any class needing a password to inherit
    - causes the child class to inherit a password column attribute
    - causes the child class to inherit a password validation method
    Example Model Declaration:
        class User(HasPassword, db.Model):
            id = db.Column(Integer, primary_key=True)
            name = db.Column(Text)
    """
    password = db.Column(Password)

    @validates('password')
    def _validate_password(self, key, password):
        return getattr(type(self), key).type.validator(password)
