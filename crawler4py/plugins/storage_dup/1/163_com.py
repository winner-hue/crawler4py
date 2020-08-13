from crawler4py.storage_dup.base_storage_dup import BaseStorageDup


class Test(BaseStorageDup):
    def __init__(self, message):
        super(Test, self).__init__(message)
