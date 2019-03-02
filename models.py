# This code is a part of MagicCap which is a MPL-2.0 licensed project.
# Copyright (C) Jake Gealer <jake@gealer.email> 2018.

from pynamodb.models import Model
from pynamodb.indexes import GlobalSecondaryIndex, AllProjection
from pynamodb.attributes import UnicodeAttribute, NumberAttribute, JSONAttribute, ListAttribute, BooleanAttribute
# Imports go here.


class VersionIndex(GlobalSecondaryIndex):
    """The index used for querying the version."""
    class Meta:
        read_capacity_units = 2
        write_capacity_units = 1
        projection = AllProjection()

    version = UnicodeAttribute(hash_key=True)


class Version(Model):
    """The model used for each version."""
    class Meta:
        table_name = "magiccap_versions"
        region = "eu-west-2"
        read_capacity_units = 2
        write_capacity_units = 1

    release_id = NumberAttribute(hash_key=True)
    version = UnicodeAttribute()
    version_index = VersionIndex()
    changelogs = UnicodeAttribute()
    beta = BooleanAttribute(null=True)


def get_version(version):
    """Uses the index to get a version."""
    for i in Version.version_index.query(version):
        return i
    raise Version.DoesNotExist


class TravisKeys(Model):
    """The model used for Travis API keys."""
    class Meta:
        table_name = "magiccap_travis_keys"
        region = "eu-west-2"
        read_capacity_units = 1
        write_capacity_units = 1

    key = UnicodeAttribute(hash_key=True)


class IPHashTimestamps(Model):
    """The timestamp that a IP address hash connected. This is used for ratelimiting."""
    class Meta:
        table_name = "magiccap_ip_hash_timestamps"
        region = "eu-west-2"
        read_capacity_units = 1
        write_capacity_units = 1

    ip_hash = UnicodeAttribute(hash_key=True)
    timestamp = NumberAttribute()


class UnvalidatedGlobalKeyRequests(Model):
    """Global key requests that have not been validated yet."""
    class Meta:
        table_name = "magiccap_unvalidated_global_key_requests"
        region = "eu-west-2"
        read_capacity_units = 1
        write_capacity_units = 1

    key = UnicodeAttribute(hash_key=True)
    data = JSONAttribute()


class GlobalKeys(Model):
    """Defines global keys (and those pending review)."""
    class Meta:
        table_name = "magiccap_global_keys"
        region = "eu-west-2"
        read_capacity_units = 3
        write_capacity_units = 2

    key = UnicodeAttribute(hash_key=True)
    email = UnicodeAttribute()
    scopes = ListAttribute()
    publisher_name = UnicodeAttribute()
    service_name = UnicodeAttribute()
    reviewed = BooleanAttribute()


class OneTimeKeys(Model):
    """Defines one time keys."""
    class Meta:
        table_name = "magiccap_one_time_keys"
        region = "eu-west-2"
        read_capacity_units = 2
        write_capacity_units = 1

    key = UnicodeAttribute(hash_key=True)
    global_key = UnicodeAttribute()


class DeviceIDIndex(GlobalSecondaryIndex):
    """The index used for querying the device ID."""
    class Meta:
        read_capacity_units = 2
        write_capacity_units = 1
        projection = AllProjection()

    device_id = UnicodeAttribute(hash_key=True)


class InstallID(Model):
    """Defines install ID's."""
    class Meta:
        table_name = "magiccap_install_ids"
        region = "eu-west-2"
        read_capacity_units = 3
        write_capacity_units = 3

    install_id = UnicodeAttribute(hash_key=True)
    device_id = UnicodeAttribute()
    hashed_ip = UnicodeAttribute()
    device_id_index = DeviceIDIndex()


def get_device_id(device_id):
    """Uses the index to get a device ID."""
    for i in InstallID.device_id_index.query(device_id):
        return i
    raise InstallID.DoesNotExist
